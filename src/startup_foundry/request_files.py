"""Register `requests/*.md` sections as open human requests linked to ventures.

ADR-0020 (package F08). A bounded, explicit operator operation: preview reads the
directory and plans; apply performs exactly that plan in one transaction. Files
are untrusted data: they are only read (no symlinks, regular UTF-8 files of at
most 100 KB, directly in the directory). Answers are never consumed here; an
answered section is only labelled `answered` until the reviewed intake flow
(`input submit`/`claim`/`complete`) records and interprets it.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from startup_foundry.domain import (
    HumanRequest,
    HumanRequestTarget,
    Venture,
    Workspace,
)
from startup_foundry.errors import ValidationError
from startup_foundry.human_inputs import HumanInputService
from startup_foundry.repository import SessionFactory
from startup_foundry.scoring import digest
from startup_foundry.snapshots import audit, snapshot, transaction

JSON = dict[str, Any]
MAPPING_FILE = "request-ventures.json"
MAX_FILES = 200
ACTOR = "request-file-sync"
REQUEST_HEADING = re.compile(r"^(#{1,2})[ \t]+(R\d{3,6})(?![\d.])\b[^\n]*$", re.M)
ANY_HEADING = re.compile(r"^(#{1,6})[ \t]", re.M)
RESPONSE = re.compile(
    r"^[ \t]*(?:\*\*)?(?:Response|My answer)\b[^\n:]*:(?:\*\*)?[ \t]*(.*)$",
    re.I | re.M,
)
TEMPLATE_ITEM = re.compile(r"^[ \t]*[-*][ \t]+[^:\n]*:[ \t]*$")
VENTURE_TOKEN = re.compile(
    r"\bv-[a-z0-9][a-z0-9-]{1,60}\b|\b[0-9a-f]{8}-[0-9a-f-]{27}\b"
)


def sections(content: str) -> list[JSON]:
    """`#`/`##` headings starting with an R-number, to the next peer heading."""
    found = []
    occurrences: dict[str, int] = {}
    headings = [(m.start(), len(m.group(1))) for m in ANY_HEADING.finditer(content)]
    for match in REQUEST_HEADING.finditer(content):
        level = len(match.group(1))
        end = next(
            (
                start
                for start, lvl in headings
                if start > match.start() and lvl <= level
            ),
            len(content),
        )
        key = match.group(2)
        occurrences[key] = occurrences.get(key, 0) + 1
        heading = match.group(0).lstrip("#").strip()
        title = re.split(r"\s+[—–]\s+", heading, maxsplit=1)
        text = content[match.start() : end].strip()
        first_response = RESPONSE.search(text)
        found.append(
            {
                "request_key": key,
                "occurrence": occurrences[key],
                "heading": heading[:300],
                "title": (title[1] if len(title) == 2 else heading)[:300],
                "text": text,
                # The question excludes answers, so answering is not a revision.
                "question": (
                    text[: first_response.start()] if first_response else text
                ).strip(),
            }
        )
    return found


def response_state(section: str) -> tuple[str, str]:
    """`answered` when the latest Response/My answer block has non-blank answers.

    A block is its marker line plus the following paragraph or list. Unfilled
    template items (`- Label:`) and blank lines are not answers.
    """
    blocks = list(RESPONSE.finditer(section))
    if not blocks:
        return "open", ""
    last = blocks[-1]
    lines = [last.group(1)]
    for line in section[last.end() :].splitlines()[1:]:
        if ANY_HEADING.match(line):
            break
        if not line.strip() and any(x.strip() for x in lines):
            break
        lines.append(line)
    answers = [line for line in lines if line.strip() and not TEMPLATE_ITEM.match(line)]
    text = "\n".join(answers)
    return ("answered" if answers else "open"), text


def read_mapping(path: Path | None) -> JSON:
    if path is None or not path.exists():
        return {"files": {}, "requests": {}, "ignore": []}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise ValidationError("Request mapping must be readable JSON") from exc
    if not isinstance(value, dict) or set(value) - {"files", "requests", "ignore"}:
        raise ValidationError(
            'Request mapping has only "files", "requests" and "ignore"'
        )
    ignore = value.setdefault("ignore", [])
    if not isinstance(ignore, list) or not all(isinstance(x, str) for x in ignore):
        raise ValidationError('"ignore" lists file names or FILE#RNNN entries')
    for group in ("files", "requests"):
        entries = value.setdefault(group, {})
        if not isinstance(entries, dict) or not all(
            isinstance(v, list) and all(isinstance(x, str) for x in v)
            for v in entries.values()
        ):
            raise ValidationError(group + " must map names to lists of venture IDs")
    return value


def request_files(directory: Path) -> list[str]:
    if not directory.is_dir():
        raise ValidationError("Requests directory does not exist")
    names = []
    for entry in sorted(os.scandir(directory), key=lambda e: e.name):
        if not entry.name.endswith(".md") or entry.name.startswith("."):
            continue
        info = entry.stat(follow_symlinks=False)
        if stat.S_ISREG(info.st_mode):
            names.append(entry.name)
    if len(names) > MAX_FILES:
        raise ValidationError(f"More than {MAX_FILES} request files; narrow the folder")
    return names


class RequestFileSync:
    def __init__(
        self, factory: SessionFactory, directory: Path, mapping: Path | None = None
    ) -> None:
        self.factory = factory
        self.directory = directory.resolve()
        self.mapping_path = mapping or self.directory / MAPPING_FILE
        self.reader = HumanInputService(factory, self.directory)

    def _ventures(self, session: Session) -> list[tuple[Venture, Workspace]]:
        return [
            (v, w)
            for v, w in session.execute(
                select(Venture, Workspace)
                .join(Workspace, Workspace.id == Venture.workspace_id)
                .order_by(Venture.id)
            ).all()
        ]

    @staticmethod
    def _match(
        name: str,
        section: JSON,
        mapping: JSON,
        ventures: list[tuple[Venture, Workspace]],
    ) -> list[JSON]:
        identities: dict[str, Venture] = {}
        for venture, _ in ventures:
            identities[venture.id] = venture
            alias = getattr(venture, "alias", None)
            if alias:
                identities[alias] = venture
        matched: dict[str, str] = {}

        def add(venture: Venture | None, via: str) -> None:
            if venture is not None and venture.id not in matched:
                matched[venture.id] = via

        for value in mapping["files"].get(name, []) + mapping["requests"].get(
            section["request_key"], []
        ):
            if value not in identities:
                raise ValidationError("Request mapping names unknown venture " + value)
            add(identities[value], "mapping")
        for token in VENTURE_TOKEN.findall(section["text"]):
            add(identities.get(token), "id")
        heading = section["heading"].lower()
        stem = "-" + name.lower().removesuffix(".md") + "-"
        for venture, workspace in ventures:
            title = workspace.title.strip().lower()
            if len(title) >= 4 and re.search(
                r"(?<!\w)" + re.escape(title) + r"(?!\w)", heading
            ):
                add(venture, "title")
            slug = venture.id.removeprefix("v-").lower()
            if (
                venture.id.startswith("v-")
                and len(slug) >= 4
                and "-" + slug + "-" in stem
            ):
                add(venture, "filename")
        return [{"venture_id": v, "via": via} for v, via in matched.items()]

    def _plan(self, session: Session) -> JSON:
        mapping = read_mapping(self.mapping_path)
        ventures = self._ventures(session)
        workspace_of = {v.id: v.workspace_id for v, _ in ventures}
        items = []
        claimed: set[str] = set()
        for name in request_files(self.directory):
            content, file_hash = self.reader.read_source(name)
            for section in sections(content):
                if (
                    name in mapping["ignore"]
                    or name + "#" + section["request_key"] in mapping["ignore"]
                ):
                    continue
                state, answer = response_state(section["text"])
                matches = self._match(name, section, mapping, ventures)
                item: JSON = {
                    "file": name,
                    "request_key": section["request_key"],
                    "occurrence": section["occurrence"],
                    "heading": section["heading"],
                    "state": state,
                    "ventures": matches,
                    "file_hash": file_hash,
                }
                if not matches:
                    items.append({**item, "action": "unlinked", "record_id": None})
                    continue
                record_id, assigned = self._identity(session, name, section, claimed)
                action: str = assigned
                claimed.add(record_id)
                sync = {
                    "file": name,
                    "request_key": section["request_key"],
                    "occurrence": section["occurrence"],
                    "heading": section["heading"],
                    "state": state,
                    "question_hash": digest(section["question"]),
                    "answer_hash": digest(answer),
                }
                targets = [workspace_of[m["venture_id"]] for m in matches]
                existing = session.get(HumanRequest, record_id)
                if existing is not None:
                    linked = set(
                        session.scalars(
                            select(HumanRequestTarget.workspace_id).where(
                                HumanRequestTarget.request_id == record_id
                            )
                        )
                    )
                    managed = (existing.source_diagnostics or {}).get("file_sync")
                    if (
                        action == "update"
                        and managed == sync
                        and set(targets) <= linked
                    ):
                        action = "unchanged"
                    elif action == "link" and set(targets) <= linked:
                        action = "unchanged"
                items.append(
                    {
                        **item,
                        "action": action,
                        "record_id": record_id,
                        "title": section["title"],
                        "question": section["question"][:20000] or section["heading"],
                        "targets": targets,
                        "sync": sync,
                    }
                )
        return {
            "directory": str(self.directory),
            "mapping_file": str(self.mapping_path)
            if self.mapping_path.exists()
            else None,
            "items": items,
            "counts": {
                action: sum(1 for i in items if i["action"] == action)
                for action in ["create", "update", "link", "unchanged", "unlinked"]
            },
        }

    @staticmethod
    def _identity(
        session: Session, name: str, section: JSON, claimed: set[str]
    ) -> tuple[str, Literal["create", "update", "link"]]:
        """Reuse the R-number unless another file or occurrence already owns it."""
        key = section["request_key"]
        suffix = hashlib.sha256(
            (name + "#" + str(section["occurrence"])).encode()
        ).hexdigest()[:6]
        for candidate in [key, key + "-" + suffix]:
            if candidate in claimed:
                continue
            existing = session.get(HumanRequest, candidate)
            if existing is None:
                if candidate == key and section["occurrence"] > 1:
                    continue
                return candidate, "create"
            managed = (existing.source_diagnostics or {}).get("file_sync") or {}
            if (
                managed.get("file") == name
                and managed.get("occurrence") == section["occurrence"]
            ):
                return candidate, "update"
            if candidate == key and existing.file_path == name and not managed:
                return candidate, "link"
        raise ValidationError("Cannot assign a unique request ID for " + key)

    def preview(self) -> JSON:
        with self.factory() as session:
            plan = self._plan(session)
        return {**plan, "applied": False, "items": [_public(i) for i in plan["items"]]}

    def apply(self) -> JSON:
        with transaction(self.factory) as session:
            plan = self._plan(session)
            for item in plan["items"]:
                if item["action"] in {"create", "update"}:
                    self._write(session, item)
                if item["action"] in {"create", "update", "link"}:
                    for workspace in item["targets"]:
                        exists = session.scalar(
                            select(HumanRequestTarget.id).where(
                                HumanRequestTarget.request_id == item["record_id"],
                                HumanRequestTarget.workspace_id == workspace,
                            )
                        )
                        if not exists:
                            session.add(
                                HumanRequestTarget(
                                    request_id=item["record_id"],
                                    workspace_id=workspace,
                                )
                            )
                    session.flush()
                    audit(
                        session,
                        item["targets"][0],
                        item["record_id"],
                        "request_file_synced",
                        ACTOR,
                        {
                            "action": item["action"],
                            "file": item["file"],
                            "state": item["state"],
                            "targets": item["targets"],
                        },
                    )
            return {
                **plan,
                "applied": True,
                "items": [_public(i) for i in plan["items"]],
            }

    @staticmethod
    def _write(session: Session, item: JSON) -> None:
        request = session.get(HumanRequest, item["record_id"])
        owner = item["targets"][0]
        definition = {
            "id": item["record_id"],
            "workspace_id": owner if request is None else request.workspace_id,
            "title": item["title"],
            "question": item["question"],
            "source_file": item["file"],
        }
        previous = (
            (request.source_diagnostics or {}).get("file_sync") if request else None
        )
        if request is None:
            request = HumanRequest(
                id=item["record_id"],
                workspace_id=owner,
                title=item["title"],
                question=item["question"],
                definition_revision=1,
                status="waiting_for_answer",
            )
        elif (
            previous and previous.get("question_hash") != item["sync"]["question_hash"]
        ):
            request.definition_revision += 1
        if request.definition_artifact_id is None or (
            previous and previous.get("question_hash") != item["sync"]["question_hash"]
        ):
            artifact = snapshot(
                session,
                definition["workspace_id"],
                "human-request/v1",
                {
                    "request_id": item["record_id"],
                    "revision": request.definition_revision,
                    "definition": definition,
                    "actor": ACTOR,
                },
            )
            request.definition_artifact_id = artifact.id
        request.title = item["title"]
        request.question = item["question"]
        # Status is never changed here; the reviewed intake flow owns it.
        request.source_diagnostics = {
            **(request.source_diagnostics or {}),
            "file_sync": item["sync"],
        }
        session.add(request)
        session.flush()


def _public(item: JSON) -> JSON:
    return {k: v for k, v in item.items() if k not in {"question", "sync"}}
