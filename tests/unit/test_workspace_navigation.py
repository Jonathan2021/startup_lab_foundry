"""Bounded detail routes and score/list context survive every workspace link."""

import html
import re
from urllib.parse import parse_qs, quote, urlsplit

import pytest
from fastapi.testclient import TestClient

from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.web import create_app
from startup_foundry.workspace_modules import ConfigInput, WorkspaceModuleService


@pytest.fixture
def console(tmp_path):
    url = f"sqlite:///{tmp_path / 'navigation.db'}"
    upgrade_database(url)
    f = create_session_factory(create_db_engine(url))
    p = PortfolioService(f)
    p.create_idea(IdeaDraft(title="Navigation", description="Fixture"), idea_id="idea")
    p.promote_idea("idea", venture_id="v")
    WorkspaceModuleService(f).configure(
        "v", ConfigInput(expected_revision=0, actor="operator", modules=["software"])
    )
    with TestClient(
        create_app(f, tmp_path),
        base_url="http://127.0.0.1",
        raise_server_exceptions=False,
    ) as c:
        yield c


@pytest.mark.parametrize(
    "query", ["offset=bogus", "offset=-1", "offset=1000001", "limit=0", "limit=201"]
)
def test_invalid_detail_pagination_is_bounded(console, query):
    assert console.get("/ventures/v?tab=history&" + query).status_code in [400, 422]


def test_unknown_cards_fail_consistently_and_valid_empty_original_works(console):
    for path in [
        "/ventures/v",
        "/ideas/idea",
        "/ventures",
        "/ideas",
        "/api/ventures/v/scores",
    ]:
        assert console.get(path + "?score_view=does-not-exist").status_code == 404, path
        assert console.get(path + "?score_view=original").status_code == 200, path


def test_tabs_breakdown_modules_pagination_switch_and_back_keep_context(console):
    back = "/ventures?q=Navigation&sort=name&direction=asc&offset=30&disposition=pursue"
    initial = console.get(
        "/ventures/v?score_view=original&return_to=" + quote(back)
    ).text
    for label in ["Breakdown and history", "Software", "History", "Work and input"]:
        url = html.unescape(re.search(r'href="([^"]+)">' + label + r"</a>", initial)[1])
        assert parse_qs(urlsplit(url).query)["return_to"] == [back]
        assert parse_qs(urlsplit(url).query)["score_view"] == ["original"]
        later = console.get(url).text
        assert (
            html.unescape(re.search(r'class="back" href="([^"]+)"', later)[1]) == back
        )
    page = console.get(
        "/ventures/v?tab=history&limit=1&score_view=original&return_to=" + quote(back)
    ).text
    next_url = html.unescape(re.search(r'href="([^"]+)">Next</a>', page)[1])
    assert parse_qs(urlsplit(next_url).query)["return_to"] == [back]
    assert console.get(next_url).status_code == 200
    switch = html.unescape(re.search(r'<option value="([^"]+)" selected', initial)[1])
    assert parse_qs(urlsplit(switch).query)["return_to"] == [back]
    assert "tab" not in parse_qs(urlsplit(switch).query)


@pytest.mark.parametrize(
    "target",
    [
        "https://evil.example",
        "//evil.example",
        "/ventures/../evil",
        "/ventures\\evil",
        "/ventures?x=\nhttps://evil.example",
    ],
)
def test_malicious_return_target_is_rejected(console, target):
    page = console.get("/ventures/v?return_to=" + quote(target)).text
    assert re.search(r'class="back" href="([^"]+)"', page)[1] == "/ventures"
