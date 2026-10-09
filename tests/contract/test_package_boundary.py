"""Product-local package and learning-boundary checks."""

import hashlib
import json
import re
from pathlib import Path

import pytest

import startup_foundry
from startup_foundry.decision_commands import AGENT_CONTRACT_VERSION

FOUNDRY_ROOT = Path(__file__).parents[2]
KIT = FOUNDRY_ROOT / "scripts" / "agent-kit" / "foundry_agent.py"
VENDORED_KIT = FOUNDRY_ROOT / "tools" / "foundry_agent.py"
EXAMPLE_MANIFEST = FOUNDRY_ROOT / ".foundry" / "project.example.json"


def test_package_is_importable() -> None:
    assert startup_foundry.__version__ == "0.1.0"


def test_learning_state_is_outside_product_package() -> None:
    package_files = {
        path.name for path in Path(startup_foundry.__file__).parent.iterdir()
    }
    assert "ROADMAP.md" not in package_files
    assert "CERTIFICATION_STATUS.md" not in package_files


def test_agent_kit_release_metadata_is_consistent() -> None:
    """Venture repos vendor the kit and pin its hash/contract from the example."""
    kit = KIT.read_bytes()
    bridge = re.search(rb'^BRIDGE_VERSION = "([^"]+)"$', kit, re.MULTILINE)
    assert bridge is not None
    assert bridge[1].decode() == AGENT_CONTRACT_VERSION

    manifest = json.loads(EXAMPLE_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["kit_sha256"] == hashlib.sha256(kit).hexdigest()
    assert manifest["agent_contract_version"] == AGENT_CONTRACT_VERSION


def test_foundry_dogfoods_the_canonical_agent_kit_byte_for_byte() -> None:
    # tools/ is the copy this repository's own AGENTS.md runs.
    if not VENDORED_KIT.exists():
        pytest.skip("tools/ is not shipped in the sdist")
    assert VENDORED_KIT.read_bytes() == KIT.read_bytes()
