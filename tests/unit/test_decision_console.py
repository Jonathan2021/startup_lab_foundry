"""The human UI and agent interface share the same scoped mutation contracts."""

import re

from fastapi.testclient import TestClient

from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.web import create_app


def test_local_map_context_result_and_capture_forms(tmp_path):
    url = f"sqlite:///{tmp_path / 'console.db'}"
    upgrade_database(url)
    f = create_session_factory(create_db_engine(url))
    p = PortfolioService(f)
    idea = p.create_idea(
        IdeaDraft(title="<script>unsafe</script>", description="Synthetic scope")
    )
    venture = p.promote_idea(idea["id"])
    ws = venture["workspace_id"]
    with TestClient(create_app(f, tmp_path), base_url="http://127.0.0.1") as client:
        page = client.get("/ventures/" + venture["id"])
        assert "Decision map" in page.text and "Record a change" in page.text
        assert "<script>unsafe</script>" not in page.text
        token = re.search(r'name="foundry-token" content="([^"]+)"', page.text)[1]
        headers = {"X-Foundry-Token": token}
        endpoint = f"/api/workspaces/{ws}/decision-map"
        draft = client.get(endpoint + "/draft").json()
        payload = {
            "expected_head": None,
            "request_key": "map",
            "actor": "operator",
            "rationale": "Use current scope",
            "map": draft,
        }
        assert client.post(endpoint, json=payload).status_code == 403
        assert (
            client.post(
                endpoint,
                json=payload,
                headers={**headers, "Origin": "https://evil.invalid"},
            ).status_code
            == 403
        )
        preview = client.post(endpoint + "/preview", json=payload, headers=headers)
        assert preview.status_code == 200, preview.text
        assert client.get(endpoint).json()["id"] is None
        saved = client.post(endpoint, json=payload, headers=headers).json()
        editor = client.get(f"/workspaces/{ws}/decision-map")
        assert (
            editor.status_code == 200
            and "Purpose and possible next steps" in editor.text
        )
        assert "Edit decision map" in editor.text
        resume = client.get(f"/api/workspaces/{ws}/resume").json()
        work = resume["work"][0]
        ctx_response = client.post(
            f"/api/workspaces/{ws}/contexts",
            headers=headers,
            json={
                "expected_head": saved["id"],
                "request_key": "context",
                "actor": "operator",
                "work_id": work["id"],
                "expected_work_version": work["version_id"],
            },
        )
        assert ctx_response.status_code == 200, ctx_response.text
        ctx = ctx_response.json()
        context_page = client.get("/handoffs/" + ctx["id"])
        assert (
            context_page.status_code == 200 and "Return findings" in context_page.text
        )
        assert (
            client.get("/handoffs/" + ctx["id"] + ".md")
            .headers["content-type"]
            .startswith("text/plain")
        )
        assert "Local research/drafts only" in context_page.text
        result = client.post(
            f"/api/workspaces/{ws}/results",
            headers=headers,
            json={
                "context_id": ctx["id"],
                "request_key": "result",
                "actor": "agent",
                "summary": "Stop this investigation",
                "rationale": "No useful gap found",
                "limits": "Synthetic example",
                "outcome": "stop",
                "next_action": "Retain rationale",
            },
        ).json()
        review_page = client.get("/decision-results/" + result["id"])
        assert (
            review_page.status_code == 200
            and "Accept these changes" in review_page.text
        )
        choice = {
            "expected_result_digest": result["digest"],
            "expected_head": saved["id"],
            "expected_work_version": work["version_id"],
            "expected_review_revision": 0,
            "resolution": "accept",
            "actor": "operator",
            "rationale": "Reviewed",
        }
        accepted = client.post(
            "/api/decision-results/" + result["id"] + "/resolve",
            headers=headers,
            json=choice,
        )
        assert accepted.status_code == 200, accepted.text
        assert client.get("/decision-results/" + result["id"]).status_code == 200
