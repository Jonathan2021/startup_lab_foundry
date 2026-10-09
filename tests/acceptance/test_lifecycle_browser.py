"""Real desktop/mobile Chromium checks of the local human decision loop."""

from __future__ import annotations

import os
import shutil
import socket
import threading
import time
from pathlib import Path

import pytest
import uvicorn
from playwright.sync_api import expect, sync_playwright

from startup_foundry.migrations import upgrade_database
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.web import create_app


@pytest.fixture
def browser_server(tmp_path):
    url = f"sqlite:///{tmp_path / 'browser.db'}"
    upgrade_database(url)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    app = create_app(factory, tmp_path)
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, log_level="error", access_log=False))
    thread = threading.Thread(
        target=server.run, kwargs={"sockets": [sock]}, daemon=True
    )
    thread.start()
    deadline = time.monotonic() + 10
    while not server.started and time.monotonic() < deadline:
        time.sleep(0.02)
    assert server.started
    try:
        yield f"http://127.0.0.1:{port}", factory
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        sock.close()
        engine.dispose()


@pytest.mark.parametrize("width", [1280, 390])
def test_create_map_capture_return_review_and_restart(browser_server, tmp_path, width):
    browser_server, _ = browser_server
    executable = os.environ.get("FOUNDRY_BROWSER_EXECUTABLE") or shutil.which(
        "chromium"
    )
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=executable, headless=True)
        browser_context = browser.new_context(viewport={"width": width, "height": 900})
        page = browser_context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(browser_server + "/new")
        form = page.locator('form[data-api="/api/ideas"]')
        form.get_by_label("Title", exact=True).fill("Synthetic service lifecycle")
        form.get_by_label("Problem and proposed approach").fill(
            "Keep an operating service reliable"
        )
        form.get_by_role("button", name="Save idea", exact=True).click()
        page.wait_for_url("**/ideas/*")
        page.get_by_role(
            "button", name="Open venture investigation", exact=True
        ).click()
        page.wait_for_url("**/ventures/*")
        venture_url = page.url.split("?", 1)[0]
        page.goto(venture_url + "?tab=scores&score_view=original")
        page.get_by_text("Append independent assessment", exact=False).click()
        scores = page.locator('form[data-api="/api/venture-scores"]')
        scores.locator('[name="score:problem"]').fill("7")
        scores.get_by_label("Rationale", exact=True).fill(
            "Synthetic interaction check only"
        )
        scores.get_by_role("button", name="Save assessment", exact=True).click()
        expect(scores.locator('[name="expected_sequence"]')).to_have_value("1")
        page.goto(venture_url)
        expect(page.locator(".score-summary")).to_contain_text("Partial assessment")
        page.get_by_role("link", name="Create a map", exact=True).click()
        page.wait_for_url("**/decision-map*")
        editor = page.locator("[data-map-editor]")
        editor.get_by_role("button", name="Add goal, question or alternative").click()
        alternative = editor.locator("[data-map-node]").last
        alternative.locator('[name="node_kind"]').select_option("alternative")
        alternative.get_by_label("Title", exact=True).fill("Hold a failing release")
        branch_id = alternative.locator('[name="node_id"]').input_value()
        editor.get_by_role("button", name="Add relationship", exact=True).click()
        edge = editor.locator("[data-map-edge]").last
        edge.locator('[name="edge_source"]').select_option("goal")
        edge.locator('[name="edge_target"]').select_option(branch_id)
        edge.get_by_label("Condition (required for a possible branch)").fill(
            "A boundary check fails"
        )
        edge.locator('[name="edge_outcome"]').select_option("blocked")
        editor.get_by_role("button", name="Preview revision", exact=True).click()
        expect(editor.locator(".map-preview")).to_be_visible()
        editor.get_by_role("button", name="Apply this revision", exact=True).click()
        expect(page.get_by_text("Revision 1", exact=True).first).to_be_visible()
        page.get_by_role("link", name="Now", exact=True).click()
        page.get_by_text("Record a change", exact=True).click()
        capture = page.locator('form[data-lifecycle="capture"]')
        capture.get_by_label("What changed?").fill(
            "Synthetic release boundary test failed"
        )
        capture.get_by_label("Details and limits").fill(
            "Staging only; production impact unknown"
        )
        capture.get_by_label("Source", exact=True).fill(
            "observation: synthetic staging reproduction"
        )
        capture.get_by_role("button", name="Save for review", exact=True).click()
        expect(capture).not_to_be_visible()
        page.get_by_role(
            "button", name="Prepare agent context", exact=True
        ).first.click()
        page.wait_for_url("**/handoffs/*")
        expect(
            page.get_by_text("Evidence still to inspect", exact=True)
        ).to_be_visible()
        page.get_by_role(
            "button", name="Prepare context including these records", exact=True
        ).click()
        expect(page.get_by_text("Evidence still to inspect", exact=True)).to_have_count(
            0
        )
        result_form = page.locator('form[data-lifecycle="result"]')
        result_form.get_by_label("Result summary", exact=True).fill(
            "Hold the release test"
        )
        result_form.get_by_label("Reasoning", exact=True).fill(
            "The boundary check failed"
        )
        result_form.get_by_label("Limits and unknowns", exact=True).fill(
            "Synthetic; no production evidence"
        )
        result_form.get_by_role("combobox", name="Outcome").select_option("hold")
        result_form.get_by_label("Next action or reason for stopping").fill(
            "Revisit the release after a corrected boundary test"
        )
        result_form.get_by_label("Revisit trigger (required for hold)").fill(
            "Independent passing check"
        )
        result_form.get_by_role(
            "button", name="Save result for review", exact=True
        ).click()
        page.wait_for_url("**/decision-results/*")
        review_url = page.url
        review = page.locator('form[data-lifecycle="resolve"]')
        review.get_by_label("Review rationale", exact=True).fill(
            "Evidence and scope reviewed"
        )
        review.get_by_role("button", name="Defer", exact=True).click()
        expect(
            page.get_by_text("Deferred by local operator:", exact=False)
        ).to_be_visible()
        review.get_by_label("Review rationale", exact=True).fill(
            "Evidence and scope reviewed"
        )
        review.get_by_role("button", name="Preview work effects", exact=True).click()
        expect(
            review.get_by_text("Preview only — no changes saved.", exact=True)
        ).to_be_visible()
        review.get_by_role("button", name="Accept these changes", exact=True).click()
        expect(
            page.get_by_role("heading", name="Recorded resolution: Accept", exact=True)
        ).to_be_visible()
        assert page.evaluate(
            "document.documentElement.scrollWidth <= window.innerWidth + 1"
        )
        screenshot_dir = Path(
            os.environ.get("FOUNDRY_BROWSER_ARTIFACTS", str(tmp_path))
        )
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        page.screenshot(
            path=str(screenshot_dir / f"result-{width}.png"), full_page=True
        )
        page.goto(venture_url)
        page.get_by_role("link", name="Open map", exact=True).click()
        page.screenshot(path=str(screenshot_dir / f"map-{width}.png"), full_page=True)
        assert page.evaluate(
            "document.documentElement.scrollWidth <= window.innerWidth + 1"
        )
        # Fresh browser context recovers the same retained result and history.
        browser_context.close()
        fresh = browser.new_context(viewport={"width": width, "height": 900})
        restarted = fresh.new_page()
        restarted.goto(review_url)
        expect(
            restarted.get_by_role(
                "heading", name="Recorded resolution: Accept", exact=True
            )
        ).to_be_visible()
        assert not errors
        browser.close()


def test_input_answer_and_readable_fusion_edit_accept(browser_server, tmp_path):
    from startup_foundry.application import FoundryApplication
    from startup_foundry.domain import VentureStage
    from startup_foundry.human_inputs import HumanInputService, RequestInput
    from startup_foundry.portfolio import IdeaDraft, PortfolioService
    from startup_foundry.proposals import FusionInput, ProposalService

    url, factory = browser_server
    FoundryApplication(factory).create_venture(
        venture_id="v-foundry",
        name="Foundry",
        objective="Fixture",
        stage=VentureStage.DISCOVERY,
    )
    portfolio = PortfolioService(factory)
    for identity in ["sport-a", "sport-b"]:
        idea = portfolio.create_idea(
            IdeaDraft(title=identity, description="Synthetic sports group"),
            idea_id=identity,
        )
        portfolio.promote_idea(identity, venture_id="v-" + identity)
    inputs = HumanInputService(factory, tmp_path)
    inputs.register(
        RequestInput(
            id="R077",
            workspace_id=idea["workspace_id"],
            target_workspace_ids=[idea["workspace_id"]],
            title="Which group?",
            question="Which sport and group?",
        )
    )
    proposals = ProposalService(factory)
    proposal = proposals.create(
        FusionInput(
            name="Shared group investigation",
            description="Compare two sports jobs",
            source_idea_ids=["sport-a", "sport-b"],
            source_venture_ids=["v-sport-a", "v-sport-b"],
            result_venture_id="v-shared",
            request_key="browser-fusion",
            rationale="Potential shared audience",
            scope=[
                {
                    "capability": "Fair teams",
                    "treatment": "combined",
                    "reason": "Same group",
                    "provenance": "Synthetic fixture",
                }
            ],
            alternatives=["Keep separate"],
        )
    )
    executable = os.environ.get("FOUNDRY_BROWSER_EXECUTABLE") or shutil.which(
        "chromium"
    )
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=executable, headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(url + "/requests/R077")
        page.get_by_label("Your answer").fill(
            "Synthetic volleyball group, twelve people"
        )
        page.get_by_role("button", name="Submit answer", exact=True).click()
        expect(
            page.get_by_role("heading", name="Saved answer · waiting for review")
        ).to_be_visible()
        assert inputs.show("R077")["status"] == "ready_for_review"
        page.goto(url + "/proposals/" + proposal["id"])
        page.get_by_text("Edit proposal (creates a new revision)", exact=True).click()
        edit = page.locator("form[data-proposal-edit]")
        edit.get_by_label("Name", exact=True).fill("Synthetic volleyball group")
        edit.locator('[name="scope_treatment"]').first.select_option("deferred")
        edit.locator('[name="scope_reason"]').first.fill(
            "Test the shared audience first"
        )
        edit.locator('[name="work_treatment"]').first.select_option("supersede")
        edit.locator('[name="work_reason"]').first.fill(
            "Continue in the composite task"
        )
        edit.locator('[name="rationale"]').fill(
            "One sport first; keep alternatives visible"
        )
        edit.get_by_role("button", name="Save new revision", exact=True).click()
        expect(
            page.get_by_role("heading", name="Synthetic volleyball group", exact=True)
        ).to_be_visible()
        decide = page.locator('form[data-api$="/resolve"]')
        decide.locator('[name="action"]').select_option("accept")
        decide.get_by_label("Required decision rationale").fill(
            "Apply the reviewed synthetic fusion"
        )
        decide.get_by_role("button", name="Record decision", exact=True).click()
        expect(
            page.get_by_role("heading", name="Controlled reversal", exact=True)
        ).to_be_visible()
        assert proposals.show(proposal["id"])["state"] == "applied"
        reversal = page.locator('form[data-api$="/resolve"]')
        reversal.get_by_label("Rationale", exact=True).fill("Synthetic reversal review")
        reversal.get_by_role("button", name="Record reversal").click()
        expect(
            page.get_by_role("heading", name="Controlled reversal", exact=True)
        ).to_have_count(0)
        assert proposals.show(proposal["id"])["state"] == "reversed"
        other = proposals.create(
            FusionInput(
                name="Another synthetic proposal",
                description="Keep separate for now",
                source_idea_ids=["sport-a", "sport-b"],
                source_venture_ids=["v-sport-a", "v-sport-b"],
                result_venture_id="v-second",
                request_key="browser-rejection",
                rationale="Compare alternatives",
                scope=[
                    {
                        "capability": "Fair teams",
                        "treatment": "deferred",
                        "reason": "Uncertain",
                        "provenance": "Fixture",
                    }
                ],
                alternatives=["Keep separate"],
            )
        )
        page.goto(url + "/proposals/" + other["id"])
        rejection = page.locator('form[data-api$="/resolve"]')
        rejection.get_by_label("Required decision rationale").fill(
            "Keep the synthetic investigations separate"
        )
        rejection.get_by_role("button", name="Record decision").click()
        expect(rejection).to_have_count(0)
        assert proposals.show(other["id"])["state"] == "rejected"
        assert not errors
        browser.close()
