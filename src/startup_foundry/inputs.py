"""Bounded JSON command inputs; payloads are data, never executable commands."""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel
from pydantic import ValidationError as ContractError

from startup_foundry.errors import ValidationError

ModelT = TypeVar("ModelT", bound=BaseModel)


def read_input(model: type[ModelT], path: str) -> ModelT:
    try:
        content = Path(path).read_bytes()
        if len(content) > 100_000:
            raise ValidationError("JSON input exceeds 100 KB")
        return model.model_validate_json(content)
    except (OSError, ContractError, ValueError) as exc:
        raise ValidationError("Invalid JSON input: " + str(exc)) from exc
