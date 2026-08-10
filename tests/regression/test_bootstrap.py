"""Green checks for agent-completed repository bootstrap behavior."""

import hashlib
from pathlib import Path

import startup_foundry

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def test_package_is_importable() -> None:
    assert startup_foundry.__version__ == "0.0.1"


def test_product_source_documents_are_preserved() -> None:
    expected_digests = {
        "docs/reference/README_startup_projects.md": (
            "904770a9916eeea703cf715171afff20b88854416d1864c456b8bc4c85bf6170"
        ),
        "docs/reference/agent_evalops_mlops_foundry_roadmap.docx": (
            "a7168c356cdf70da8367ba223a25f9d81155a64960f90d79c7056d4cbe255cc3"
        ),
        "foundry/docs/startup_foundry_project.md": (
            "f85bb90b7e1b6b354ec984409c80f53b9f2e51859d3d1a145021353ab96713dc"
        ),
        "agentevalops/docs/agent_evalops_project.md": (
            "976a3c41b316f6b8bd4f289703a7a743a789e6728bc253a44ff1147273416818"
        ),
    }
    for relative_path, expected_digest in expected_digests.items():
        document = REPOSITORY_ROOT / relative_path
        assert document.is_file()
        assert hashlib.sha256(document.read_bytes()).hexdigest() == expected_digest


def test_learning_state_is_outside_product_package() -> None:
    package_files = {
        path.name for path in Path(startup_foundry.__file__).parent.iterdir()
    }
    assert "ROADMAP.md" not in package_files
    assert "CERTIFICATION_STATUS.md" not in package_files
