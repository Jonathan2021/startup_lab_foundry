"""One bounded query and URL contract for scoped detail navigation."""

from typing import Literal
from urllib.parse import urlencode, urlsplit

from fastapi import Request
from pydantic import BaseModel, ConfigDict, Field
from pydantic import ValidationError as ContractError

from startup_foundry.errors import ValidationError
from startup_foundry.scoring import ORIGINAL, REVIEWED


class DetailQuery(BaseModel):
    model_config = ConfigDict(extra="ignore")
    tab: Literal[
        "overview",
        "work",
        "evidence",
        "decisions",
        "history",
        "scores",
        "settings",
        "software",
        "outreach",
    ] = "overview"
    score_view: str = Field(default="reviewed", min_length=1, max_length=36)
    offset: int = Field(default=0, ge=0, le=1000000)
    limit: int = Field(default=30, ge=1, le=200)
    return_to: str | None = Field(default=None, max_length=6000)

    @classmethod
    def parse(cls, request: Request) -> "DetailQuery":
        try:
            return cls.model_validate(dict(request.query_params))
        except ContractError as exc:
            raise ValidationError("Invalid workspace query: " + str(exc)) from exc

    @property
    def card_id(self) -> str:
        return {"original": ORIGINAL, "reviewed": REVIEWED}.get(
            self.score_view, self.score_view
        )

    def back(self, kind: str) -> str:
        fallback = "/" + kind
        target = self.return_to or fallback
        if any(ord(c) < 32 or c == "\\" for c in target):
            return fallback
        try:
            parsed = urlsplit(target)
        except ValueError:
            return fallback
        return (
            target
            if (
                not parsed.scheme
                and not parsed.netloc
                and not parsed.fragment
                and parsed.path in {"/ideas", "/ventures"}
            )
            else fallback
        )

    def url(
        self,
        path: str,
        *,
        kind: str,
        tab: str | None = None,
        offset: int | None = None,
        fragment: str = "",
    ) -> str:
        values: dict[str, str | int] = {
            "score_view": self.score_view,
            "return_to": self.back(kind),
        }
        if tab and tab != "overview":
            values["tab"] = tab
        if tab == "history":
            values["limit"] = self.limit
            values["offset"] = offset if offset is not None else self.offset
        return path + "?" + urlencode(values) + ("#" + fragment if fragment else "")
