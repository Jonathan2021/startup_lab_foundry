"""Durable answers, source safety and manual ownership on disposable stores."""

import pytest

from startup_foundry.errors import ConflictError, ValidationError
from startup_foundry.human_inputs import (
    ClaimInput,
    HumanInputService,
    RequestInput,
    ResponseInput,
    ReviewResult,
)
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory


@pytest.fixture
def inputs(tmp_path):
    url = f"sqlite:///{tmp_path / 'db'}"
    upgrade_database(url)
    factory = create_session_factory(create_db_engine(url))
    p = PortfolioService(factory)
    p.create_idea(IdeaDraft(title="Sports", description="Fixture"), idea_id="P103")
    p.promote_idea("P103", venture_id="v-sports")
    workspace = p.show_idea("P103")["workspace_id"]
    service = HumanInputService(factory, tmp_path)
    service.register(
        RequestInput(
            id="R006",
            workspace_id=workspace,
            target_workspace_ids=[workspace],
            title="Sport",
            question="Which sport?",
            file_path="answers.md",
        )
    )
    return service, tmp_path


def test_repeat_correction_reversion_nonanswer_edits_and_restart(inputs):
    s, root = inputs
    f = root / "answers.md"
    f.write_text("## R006 — Sport\nWhich sport?\nResponse: Volleyball\n")
    assert s.sync(s.preview())["imported"] == 1
    assert s.sync(s.preview())["imported"] == 0
    f.write_text("## R006 — Sport\nEdited question\nResponse: Volleyball\n")
    assert s.sync(s.preview())["imported"] == 0
    for text in ["Tennis", "Volleyball"]:
        f.write_text("## R006 — Sport\nResponse: " + text + "\n")
        assert s.sync(s.preview())["imported"] == 1
    assert len(s.show("R006")["responses"]) == 3


def test_claim_old_answer_and_divergent_file_keep_new_answer_pending(inputs):
    s, root = inputs
    f = root / "answers.md"
    f.write_text("## R006 — Sport\nResponse: Volleyball\n")
    s.sync(s.preview())
    r = s.show("R006")
    claim = s.claim("R006", ClaimInput(expected_version=r["version"], actor="agent"))
    with pytest.raises(ConflictError):
        s.claim("R006", ClaimInput(expected_version=claim["version"], actor="other"))
    s.submit(
        "R006",
        ResponseInput(
            expected_version=claim["version"],
            text="<script>tennis</script>",
            author="operator",
            submission_key="ui-1",
        ),
    )
    f.write_text("## R006 — Sport\nResponse: Football\n")
    preview = s.preview()
    assert preview["items"][0]["diagnostic"] == "conflict"
    with pytest.raises(ConflictError):
        s.sync(preview)
    s.complete(
        "R006",
        ReviewResult(
            work_id=claim["work_id"],
            response_id=claim["response_id"],
            actor="agent",
            interpretation="Old answer",
            outcome="no_change",
            rationale="Historical only",
        ),
    )
    assert s.show("R006")["status"] == "ready_for_review"
    assert s.show("R006")["answer"]["text"] == "<script>tennis</script>"


def test_stale_fingerprint_symlink_duplicate_heading_and_empty(inputs):
    s, root = inputs
    f = root / "answers.md"
    f.write_text("## R006 — Sport\nResponse: A\n")
    preview = s.preview()
    f.write_text("## R006 — Sport\nResponse: B\n")
    with pytest.raises(ConflictError):
        s.sync(preview)
    f.write_text("## R006 — Sport\nResponse:\n- Usual sport:\n")
    assert s.preview()["items"][0]["diagnostic"] == "empty"
    f.write_text("## R006 — Sport\nResponse: A\n## R006 — duplicate\nResponse: B\n")
    assert s.preview()["items"][0]["diagnostic"] == "source_needs_attention"
    f.unlink()
    f.symlink_to(root / "db")
    assert s.preview()["items"][0]["diagnostic"] == "source_needs_attention"
    with pytest.raises(ValidationError):
        s.read_source("../db")
