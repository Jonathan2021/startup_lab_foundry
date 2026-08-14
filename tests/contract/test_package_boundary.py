"""Product-local package and learning-boundary checks."""

from pathlib import Path

import startup_foundry


def test_package_is_importable() -> None:
    assert startup_foundry.__version__ == "0.0.1"


def test_learning_state_is_outside_product_package() -> None:
    package_files = {
        path.name for path in Path(startup_foundry.__file__).parent.iterdir()
    }
    assert "ROADMAP.md" not in package_files
    assert "CERTIFICATION_STATUS.md" not in package_files
