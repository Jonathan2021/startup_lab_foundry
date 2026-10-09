"""Bounded JSON command inputs; payloads are data, never executable commands."""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel
from pydantic import ValidationError as ContractError

from startup_foundry.errors import ValidationError

ModelT = TypeVar("ModelT", bound=BaseModel)
MAX_INPUT_BYTES = 100_000


def read_bounded(path: str, label: str) -> bytes:
    """Read one local command file; OSError is left to the caller's wording."""
    content = Path(path).read_bytes()
    if len(content) > MAX_INPUT_BYTES:
        raise ValidationError(f"{label} exceeds 100 KB")
    return content


def read_input(model: type[ModelT], path: str) -> ModelT:
    try:
        return model.model_validate_json(read_bounded(path, "JSON input"))
    except (OSError, ContractError, ValueError) as exc:
        raise ValidationError("Invalid JSON input: " + str(exc)) from exc
