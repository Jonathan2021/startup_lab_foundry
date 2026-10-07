"""Close the earlier repair's real-browser gate with disposable records."""

from urllib.parse import quote

import pytest
from playwright.sync_api import expect, sync_playwright
from test_lifecycle_browser import browser_server as browser_server

from startup_foundry.human_inputs import (
    ClaimInput,
    HumanInputService,
    RequestInput,
    ReviewResult,
    TargetChange,
)
from startup_foundry.manual_intake import IntakeCompletion, ManualIntakeService
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.scoring import (
    FACTORS,
    AssessmentInput,
    ScorecardInput,
    ScoringService,
)
from startup_foundry.venture_scoring import (
    VentureAssessmentInput,
    VentureScoringService,
)
from startup_foundry.workspace_modules import (
    ConfigInput,
    IssueInput,
    WorkspaceModuleService,
)


@pytest.mark.parametrize("width", [1280, 390])
def test_intake_scores_corrections_modules_and_return_paths(
    browser_server, tmp_path, width
):
    import os
    import shutil

    url, factory = browser_server
    p = PortfolioService(factory)
    p.create_idea(
        IdeaDraft(
            title="P103 synthetic sports", description="A bounded sports fixture"
        ),
        idea_id="P103",
    )
    executable = os.environ.get("FOUNDRY_BROWSER_EXECUTABLE") or shutil.which(
        "chromium"
    )
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=executable)
        context = browser.new_context(viewport={"width": width, "height": 900})
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(url + "/ideas/P103")
        page.get_by_role("button", name="Request initial review", exact=True).click()
        expect(
            page.locator("#initial-review").get_by_text(
                "Queued for manual agent review", exact=True
            )
        ).to_be_visible()
        ScoringService(factory).assess(
            AssessmentInput(
                idea_id="P103",
                scores={"problem": 6},
                rationale="Synthetic source baseline",
                author="fixture",
            )
        )
        page.reload()
        page.get_by_role(
            "button", name="Open venture investigation", exact=True
        ).click()
        page.wait_for_url("**/ventures/*")
        venture_id = page.url.split("?", 1)[0].rsplit("/", 1)[1]
        venture = p.promote_idea("P103")
        assert venture["id"] == venture_id
        expect(page.locator(".score-summary")).to_contain_text(
            "Starting estimate from source idea"
        )
        intake = ManualIntakeService(factory)
        handoff = intake.handoff("venture", venture_id)
        claim = intake.claim(
            "venture",
            venture_id,
            ClaimInput(
                expected_version=handoff["work"]["version"], actor="fixture agent"
            ),
        )
        completed = intake.complete(
            "venture",
            venture_id,
            IntakeCompletion(
                work_id=handoff["work"]["id"],
                expected_version=claim["version"],
                actor="fixture agent",
                request_key="browser-completion",
                research_summary="Synthetic comparison",
                research_source="Invented fixture",
                research_limits="No field validation",
                scores={"problem": 7},
                score_rationale="Only the fixture problem factor is known",
                unknown_reason="No other evidence",
                expected_sequence=1,
                expected_review_revision=0,
                next_action="Compare a concrete group workflow",
                next_work_title="Sports comparison work",
                next_owner="agent",
            ),
        )
        page.reload()
        expect(page.locator(".score-summary")).to_contain_text("1/12 factors")
        expect(page.locator(".next-action")).to_contain_text(
            "Compare a concrete group workflow"
        )
        work_id = completed["next_work_id"]
        modules = WorkspaceModuleService(factory)
        modules.configure(
            venture_id,
            ConfigInput(expected_revision=0, actor="fixture", modules=["software"]),
        )
        modules.issue(
            venture_id,
            IssueInput(
                work_id=work_id,
                category="bug",
                severity="unknown",
                source="Synthetic report",
                actor="fixture",
            ),
        )
        back = "/ventures?q=P103&sort=name&direction=asc&offset=0"
        base = (
            url
            + "/ventures/"
            + venture_id
            + "?score_view=original&return_to="
            + quote(back, safe="")
        )
        page.goto(base)
        page.get_by_role("link", name="Software", exact=True).click()
        expect(page.locator(".score-summary")).to_contain_text("portfolio-original-v1")
        page.get_by_role("link", name="Work " + work_id, exact=True).click()
        expect(
            page.get_by_role("heading", name="Sports comparison work", exact=True)
        ).to_be_visible()
        page.goto(base)
        page.get_by_role("link", name="History", exact=True).click()
        assert "score_view=original" in page.url
        page.get_by_role("link", name="Back to portfolio", exact=False).click()
        assert page.url == url + back
        page.goto(base + "&tab=history&limit=1")
        page.get_by_role("link", name="Next", exact=True).click()
        assert "offset=1" in page.url and "score_view=original" in page.url
        page.goto(base + "&tab=settings")
        settings = page.locator("form[data-config]")
        settings.locator('input[value="software"]').uncheck()
        settings.get_by_role("button", name="Save workspace settings").click()
        expect(settings.locator('[name="expected_revision"]')).to_have_value("2")
        page.goto(base + "&tab=software")
        expect(page.get_by_role("heading", name="Software is disabled")).to_be_visible()
        assert len(modules.show(venture_id)["issues"]) == 1

        score_url = url + "/ventures/" + venture_id + "?tab=scores"
        page.goto(score_url)
        page.get_by_text("Append independent assessment", exact=False).click()
        scores = page.locator("form[data-score]")
        # Keep this tab stale while a second writer appends an actual zero total.
        zero = {
            key: 1 if direction == "positive" else 10
            for key, _, direction, _ in FACTORS
        }
        VentureScoringService(factory).assess(
            VentureAssessmentInput(
                venture_id=venture_id,
                expected_sequence=2,
                request_key="zero",
                author="fixture",
                scores=zero,
                rationale="Synthetic floor score",
            )
        )
        scores.locator('[name="score:problem"]').fill("8")
        scores.get_by_label("Rationale", exact=True).fill(
            "Stale tab must not overwrite"
        )
        scores.get_by_role("button", name="Save assessment").click()
        expect(scores.locator(".form-error")).not_to_be_empty()
        page.reload()
        expect(page.locator(".score-summary")).to_contain_text("0 / 100")
        ScoringService(factory).import_scorecard(
            ScorecardInput(
                id="access-v1",
                name="Local access",
                version=1,
                rationale="Synthetic custom rubric",
                criteria=[
                    {
                        "key": "local_access",
                        "name": "Local access",
                        "direction": "positive",
                        "weight": "1",
                    }
                ],
            )
        )
        page.goto(score_url + "&score_view=access-v1")
        page.get_by_text("Append independent assessment", exact=False).click()
        custom = page.locator("form[data-score]")
        custom.locator('[name="score:local_access"]').fill("4")
        custom.get_by_label("Rationale", exact=True).fill("Synthetic custom factor")
        custom.get_by_role("button", name="Save assessment").click()
        expect(page.locator(".score-summary")).to_contain_text("40.0 / 100")
        assert page.locator('input[name="score:problem"]').count() == 0

        inputs = HumanInputService(factory, tmp_path)
        inputs.register(
            RequestInput(
                id="R088",
                workspace_id=venture["workspace_id"],
                target_workspace_ids=[venture["workspace_id"]],
                title="Group",
                question="Which group?",
                file_path="answers.md",
            )
        )
        (tmp_path / "answers.md").write_text("## R088 — Group\nResponse: Volleyball\n")
        assert inputs.sync(inputs.preview())["imported"] == 1
        item = inputs.show("R088")
        claimed = inputs.claim(
            "R088", ClaimInput(expected_version=item["version"], actor="review agent")
        )
        inputs.complete(
            "R088",
            ReviewResult(
                work_id=claimed["work_id"],
                response_id=claimed["response_id"],
                actor="review agent",
                interpretation="Use volleyball for the synthetic comparison",
                outcome="sufficient",
                rationale="Named group",
                changes=[
                    TargetChange(
                        workspace_id=venture["workspace_id"],
                        expected_revision=1,
                        next_action="Check the named group",
                        next_work_title="Named group comparison",
                    )
                ],
            ),
        )
        page.goto(url + "/requests/R088")
        expect(page.get_by_text("Current answer review", exact=False)).to_be_visible()
        page.get_by_role("link", name="Named group comparison", exact=True).click()
        expect(
            page.get_by_role("heading", name="Named group comparison", exact=True)
        ).to_be_visible()
        page.goto(url + "/requests/R088")
        page.get_by_label("Your answer").fill("Correction: tennis group")
        page.get_by_role("button", name="Submit answer", exact=True).click()
        expect(
            page.get_by_text("Historical review · older reply", exact=False)
        ).to_be_visible()
        expect(
            page.get_by_role("heading", name="Saved answer · waiting for review")
        ).to_be_visible()
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement !== document.body")
        assert page.evaluate(
            "document.documentElement.scrollWidth <= window.innerWidth + 1"
        )
        assert not errors
        browser.close()
