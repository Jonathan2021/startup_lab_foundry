"""Integrated operator flows over disposable records, including unsafe inputs."""

import re
from urllib.parse import parse_qs, urlsplit

from fastapi.testclient import TestClient

from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.web import create_app


def test_filters_reviews_scores_project_drafts_help_and_restart(tmp_path):
    url = f"sqlite:///{tmp_path / 'console.db'}"
    upgrade_database(url)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    p = PortfolioService(factory)
    for i in range(6):
        p.create_idea(
            IdeaDraft(title="Sports " + str(i), description="Fixture"), idea_id=str(i)
        )
    with TestClient(create_app(factory, tmp_path), base_url="http://127.0.0.1") as c:
        token = re.search(r'name="foundry-token" content="([^"]+)"', c.get("/").text)[1]
        headers = {"X-Foundry-Token": token, "Origin": "http://127.0.0.1"}
        page = c.get(
            "/ideas?q=Sports&score_view=reviewed&criterion=founder_fit&sort=score&direction=asc&limit=2"
        )
        assert page.status_code == 200
        link = re.search(r'href="([^"]+)">Next', page.text)[1].replace("&amp;", "&")
        query = parse_qs(urlsplit(link).query)
        assert (
            query["score_view"] == ["reviewed"]
            and query["criterion"] == ["founder_fit"]
            and query["direction"] == ["asc"]
            and query["offset"] == ["2"]
        )
        assert c.get(link).status_code == 200
        assert c.get("/api/ideas?min_score=NaN").status_code == 400
        assert c.get("/ideas?limit=0").status_code == 400
        workspace = p.show_idea("0")["workspace_id"]
        review = {
            "workspace_id": workspace,
            "expected_revision": 0,
            "investigation_stage": "comparison",
            "product_maturity": "prototype",
            "disposition": "dropped",
            "next_action": "Reopen if participants use it",
            "reason": "<script>untrusted</script>",
            "author": "tester",
        }
        assert c.post("/api/reviews", json=review, headers=headers).status_code == 201
        assert c.post("/api/reviews", json=review, headers=headers).status_code == 409
        assert (
            c.post(
                "/api/reviews",
                json={
                    **review,
                    "expected_revision": 1,
                    "disposition": "pursue",
                    "reason": "Participant access",
                },
                headers=headers,
            ).status_code
            == 201
        )
        assert (
            c.post(
                "/api/scores",
                json={
                    "idea_id": "0",
                    "scores": {"founder_fit": 9},
                    "rationale": "First party utility only",
                    "author": "tester",
                },
                headers=headers,
            ).status_code
            == 201
        )
        assert "&lt;script&gt;untrusted&lt;/script&gt;" in c.get("/ideas/0").text
        project = {
            "venture_id": "test-project",
            "source_idea_id": "0",
            "name": "Existing",
            "description": "Prototype",
            "product_maturity": "prototype",
            "reason_paused": "Buyer unknown",
            "next_bounded_test": "Interview",
            "author": "tester",
            "repositories": [
                {
                    "local_reference": "/etc/passwd",
                    "observed_at": "2026-10-04T10:00:00Z",
                }
            ],
        }
        response = c.post("/api/existing-projects", json=project, headers=headers)
        assert response.status_code == 201
        assert c.post("/api/existing-projects", json=project, headers=headers).json()[
            "unchanged"
        ]
        assert c.get("/ventures?product_maturity=prototype").status_code == 200
        detail = c.get("/ventures/test-project")
        assert (
            "Existing project checkpoint" in detail.text
            and "Buyer unknown" in detail.text
        )
        assert c.get("/existing-project?venture_id=test-project").status_code == 200
        draft = {
            "purpose": "Review fictional sample",
            "subject": "<svg onload=evil>",
            "body_text": "Bonjour\nRésumé",
            "language": "fr",
            "tone": "formal",
            "to": [],
        }
        response = c.post(
            "/api/outreach",
            json={"venture_id": "test-project", "request_key": "draft", "draft": draft},
            headers=headers,
        )
        assert response.status_code == 201
        identity = response.json()["id"]
        assert "&lt;svg onload=evil&gt;" in c.get("/outreach/" + identity).text
        edited = c.post(
            "/api/outreach/" + identity,
            json={
                "expected_version": 1,
                "actor": "tester",
                "draft": {**draft, "subject": "Updated"},
            },
            headers=headers,
        )
        assert edited.status_code == 200 and edited.json()["draft_revision"] == 2
        assert c.get("/outreach/" + identity + "/export?format=text").status_code == 200
        assert c.get("/outreach/" + identity + "/export?format=eml").status_code == 200
        for route in [
            "/help",
            "/outreach",
            "/outreach/new",
            "/existing-project",
            "/ideas",
            "/ventures",
        ]:
            assert c.get(route).status_code == 200
        assert (
            c.post(
                "/api/outreach",
                json={
                    "venture_id": "test-project",
                    "request_key": "unsafe",
                    "draft": {**draft, "subject": "Injection\nBcc: a@b.invalid"},
                },
                headers=headers,
            ).status_code
            == 422
        )
        assert c.post("/api/reviews", json=review).status_code == 403
    with TestClient(create_app(factory, tmp_path), base_url="http://127.0.0.1") as c:
        assert "Updated" in c.get("/outreach").text
        assert (
            c.get(
                "/api/ideas?score_view=reviewed&criterion=founder_fit&min_score=9"
            ).json()["total"]
            == 1
        )
    engine.dispose()
