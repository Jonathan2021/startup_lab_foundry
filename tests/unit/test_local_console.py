"""Human console workflow and local mutation boundary."""

import re

from fastapi.testclient import TestClient

from startup_foundry.migrations import upgrade_database
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.web import create_app


def test_console_creates_promotes_runs_and_survives_restart(tmp_path):
    url = f"sqlite:///{tmp_path / 'console.db'}"
    upgrade_database(url)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    with TestClient(
        create_app(factory, tmp_path / "requests"), base_url="http://127.0.0.1"
    ) as client:
        page = client.get("/")
        token = re.search(r'name="foundry-token" content="([^"]+)"', page.text)[1]
        headers = {"X-Foundry-Token": token, "Origin": "http://127.0.0.1"}
        created = client.post(
            "/api/ideas",
            headers=headers,
            json={
                "title": "<script>alert(1)</script>",
                "description": "A real testable problem",
                "customer": "Riders",
                "validation_test": "Compare one specified trip",
            },
        )
        assert created.status_code == 201
        identity = created.json()["id"]
        page = client.get("/ideas/" + identity)
        assert (
            "&lt;script&gt;" in page.text
            and "<script>alert(1)</script>" not in page.text
        )
        promoted = client.post(
            "/api/ideas/" + identity + "/promote", headers=headers, json={}
        )
        assert promoted.status_code == 201
        venture = promoted.json()["id"]
        payload = {
            "subject": "venture",
            "subject_id": venture,
            "kind": "readiness",
            "request_key": "ui-check",
        }
        run = client.post("/api/steps", headers=headers, json=payload)
        assert run.status_code == 200 and run.json()["status"] == "succeeded"
        assert (
            client.post("/api/steps", headers=headers, json=payload).json()
            == run.json()
        )
        assert client.get("/steps/" + run.json()["id"]).status_code == 200
    with TestClient(
        create_app(factory, tmp_path / "requests"), base_url="http://127.0.0.1"
    ) as client:
        assert client.get("/api/ventures").json()["total"] == 1
        assert client.get("/api/ideas").json()["total"] == 1
        assert client.get("/api/steps").json()["total"] == 1
    engine.dispose()


def test_cross_origin_missing_token_and_invalid_input_are_rejected(tmp_path):
    url = f"sqlite:///{tmp_path / 'console.db'}"
    upgrade_database(url)
    engine = create_db_engine(url)
    with TestClient(
        create_app(create_session_factory(engine), tmp_path / "requests"),
        base_url="http://127.0.0.1",
    ) as client:
        token = re.search(
            r'name="foundry-token" content="([^"]+)"', client.get("/").text
        )[1]
        body = {"title": "Bad", "description": "No mutation permitted"}
        assert client.post("/api/ideas", json=body).status_code == 403
        assert (
            client.post(
                "/api/ideas",
                json=body,
                headers={
                    "X-Foundry-Token": token,
                    "Origin": "https://untrusted.example",
                },
            ).status_code
            == 403
        )
        assert client.get("/", headers={"Host": "untrusted.example"}).status_code == 400
        assert (
            client.post(
                "/api/ideas",
                json={"title": " ", "description": " "},
                headers={"X-Foundry-Token": token},
            ).status_code
            == 400
        )
        assert client.get("/api/ideas").json()["total"] == 0
        assert client.get("/requests/../../etc/passwd").status_code == 404
    engine.dispose()
