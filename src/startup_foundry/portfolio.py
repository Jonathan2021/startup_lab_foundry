"""Idea intake, lineage and promotion over the existing Foundry domain."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from startup_foundry.application import FoundryApplication, required_text
from startup_foundry.domain import (
    Artifact,
    ArtifactKind,
    Idea,
    IdeaOrigin,
    IdeaRelation,
    IdeaRelationKind,
    IdeaRevision,
    IdeaSource,
    IdeaSourceRole,
    Portfolio,
    ReferenceSource,
    SourceKind,
    Venture,
    VentureStage,
    Workspace,
    WorkspaceKind,
    new_id,
)
from startup_foundry.errors import ConflictError, ReferenceError, ValidationError
from startup_foundry.repository import SessionFactory, UnitOfWork

JSON = dict[str, Any]
CSV_NAMES = (
    "startup_ideas",
    "startup_generated_ideas",
    "startup_competition",
    "startup_market_report",
    "startup_scoring_guide",
    "startup_dashboard",
)


def stable_id(value: str) -> str:
    return str(uuid5(NAMESPACE_URL, value))


def page_bounds(limit: int, offset: int) -> None:
    if not 1 <= limit <= 500 or offset < 0:
        raise ValidationError("limit must be 1–500 and offset nonnegative")


@dataclass(frozen=True)
class IdeaDraft:
    title: str
    description: str
    customer: str = ""
    validation_test: str = ""
    parent_ids: list[str] = field(default_factory=list)
    derivation_reason: str = ""
    original_text: str = ""
    category: str = ""
    business_model: str = ""


class PortfolioService:
    def __init__(self, session_factory: SessionFactory) -> None:
        self.factory = session_factory

    @staticmethod
    def _portfolio(session: Session) -> Portfolio:
        portfolio = session.scalar(select(Portfolio).where(Portfolio.key == "default"))
        if portfolio is None:
            portfolio = Portfolio(
                id="portfolio-default", key="default", name="Foundry ventures"
            )
            session.add(portfolio)
            session.flush()
        return portfolio

    def _create(
        self,
        session: Session,
        draft: IdeaDraft,
        idea_id: str,
        origin: IdeaOrigin = IdeaOrigin.USER_ADDED,
    ) -> Idea:
        title = required_text("title", draft.title)
        description = required_text("description", draft.description)
        if len(title) > 300 or not idea_id or len(idea_id) > 36:
            raise ValidationError(
                "Idea title/id exceeds 300/36 characters or id is blank"
            )
        if session.get(Idea, idea_id):
            raise ConflictError(f"Idea {idea_id!r} already exists")
        parents = list(dict.fromkeys(draft.parent_ids))
        if parents and not draft.derivation_reason.strip():
            raise ValidationError("Derived ideas require a reason for the change")
        for parent in parents:
            if session.get(Idea, parent) is None:
                raise ReferenceError(f"Parent idea {parent!r} does not exist")
        workspace = Workspace(
            portfolio_id=self._portfolio(session).id,
            key="idea:" + idea_id,
            title=title[:240],
            kind=WorkspaceKind.IDEA,
            description=description,
        )
        session.add(workspace)
        session.flush()
        idea = Idea(
            id=idea_id,
            workspace_id=workspace.id,
            external_key=idea_id,
            origin=IdeaOrigin.GENERATED_DERIVED if parents else origin,
        )
        session.add(idea)
        session.flush()
        revision = IdeaRevision(
            idea_id=idea.id,
            revision_number=1,
            title=title,
            cleaned_description=description,
            original_text=draft.original_text or description,
            category=draft.category or None,
            target_customer=draft.customer or None,
            business_model=draft.business_model or None,
            key_validation_test=draft.validation_test or None,
            change_reason=draft.derivation_reason
            or "Initial intake; unvalidated hypothesis",
            authored_by="foundry-intake-v1",
        )
        session.add(revision)
        session.flush()
        idea.current_revision_id = revision.id
        for parent in parents:
            session.add(
                IdeaRelation(
                    source_idea_id=idea.id,
                    target_idea_id=parent,
                    kind=IdeaRelationKind.DERIVED_FROM,
                    rationale=draft.derivation_reason,
                )
            )
        session.flush()
        return idea

    @staticmethod
    def _summary(idea: Idea, revision: IdeaRevision) -> JSON:
        return {
            "id": idea.id,
            "workspace_id": idea.workspace_id,
            "title": revision.title,
            "description": revision.cleaned_description,
            "customer": revision.target_customer,
            "validation_test": revision.key_validation_test,
            "category": revision.category,
            "business_model": revision.business_model,
            "origin": idea.origin.value,
            "status": idea.status.value,
            "revision_id": revision.id,
            "revision": revision.revision_number,
            "change_reason": revision.change_reason,
        }

    def create_idea(self, draft: IdeaDraft, *, idea_id: str | None = None) -> JSON:
        identity = idea_id or new_id()
        with UnitOfWork(self.factory) as unit:
            assert unit.session is not None
            self._create(unit.session, draft, identity)
        return self.show_idea(identity)

    def list_ideas(self, *, query: str = "", limit: int = 50, offset: int = 0) -> JSON:
        page_bounds(limit, offset)
        statement = select(Idea, IdeaRevision).join(
            IdeaRevision, Idea.current_revision_id == IdeaRevision.id
        )
        if query:
            statement = statement.where(
                or_(
                    Idea.id.icontains(query, autoescape=True),
                    IdeaRevision.title.icontains(query, autoescape=True),
                    IdeaRevision.cleaned_description.icontains(query, autoescape=True),
                )
            )
        with UnitOfWork(self.factory) as unit:
            assert unit.session is not None
            total = unit.session.scalar(
                select(func.count()).select_from(statement.subquery())
            )
            rows = unit.session.execute(
                statement.order_by(IdeaRevision.title, Idea.id)
                .limit(limit)
                .offset(offset)
            )
            return {
                "items": [self._summary(i, r) for i, r in rows],
                "total": total,
                "limit": limit,
                "offset": offset,
            }

    def show_idea(self, idea_id: str) -> JSON:
        with UnitOfWork(self.factory) as unit:
            session = unit.session
            assert session is not None
            idea = session.get(Idea, idea_id)
            if idea is None:
                raise ReferenceError(f"Idea {idea_id!r} does not exist")
            revision = session.get(IdeaRevision, idea.current_revision_id)
            if revision is None:
                raise ReferenceError("Idea has no current revision")
            data = self._summary(idea, revision)
            from startup_foundry.reviews import ReviewService
            from startup_foundry.scoring import ScoringService

            data["review"] = ReviewService(self.factory).show(idea.workspace_id)
            data["scores"] = ScoringService(self.factory).show(idea.id)
            data["original_text"] = revision.original_text
            data["parents"] = [
                {
                    "id": row.target_idea_id,
                    "reason": row.rationale,
                    "kind": row.kind.value,
                }
                for row in session.scalars(
                    select(IdeaRelation)
                    .where(IdeaRelation.source_idea_id == idea.id)
                    .order_by(IdeaRelation.target_idea_id)
                )
            ]
            data["sources"] = [
                self._source(s)
                for s in session.scalars(
                    select(ReferenceSource)
                    .join(IdeaSource, IdeaSource.source_id == ReferenceSource.id)
                    .where(IdeaSource.idea_id == idea.id)
                    .order_by(ReferenceSource.title)
                )
            ]
            data["assessment"] = next(
                (
                    a.metadata_json
                    for a in session.scalars(
                        select(Artifact)
                        .where(
                            Artifact.workspace_id == idea.workspace_id,
                            Artifact.name.in_(
                                ["Campaign disposition", "Investigation disposition"]
                            ),
                        )
                        .order_by(Artifact.created_at.desc(), Artifact.id)
                    )
                ),
                None,
            )
            data["ventures"] = [
                v.id
                for v in session.scalars(
                    select(Venture).where(
                        Venture.source_idea_revision_id == revision.id
                    )
                )
            ]
            return data

    @staticmethod
    def _source(source: ReferenceSource) -> JSON:
        try:
            metadata = json.loads(source.notes or "{}")
        except ValueError:
            metadata = {}
        if not isinstance(metadata, dict):
            metadata = {}
        notes = source.notes
        if "rows" in metadata:
            notes = json.dumps(
                {
                    "authority": metadata.get("authority"),
                    "row_count": len(metadata["rows"]),
                    "columns": metadata["rows"][0] if metadata["rows"] else [],
                    "original_file": source.locator,
                    "content": "All raw rows retained in the database source record.",
                },
                indent=2,
            )
        return {
            "id": source.id,
            "title": source.title,
            "locator": source.locator,
            "kind": source.kind.value,
            "digest": source.content_digest,
            "notes": notes,
            "claim": metadata.get("claim"),
            "limits": metadata.get("limits"),
            "checked_on": metadata.get("checked_on"),
        }

    def list_sources(
        self, *, query: str = "", limit: int = 50, offset: int = 0
    ) -> JSON:
        page_bounds(limit, offset)
        statement = select(ReferenceSource)
        if query:
            statement = statement.where(
                ReferenceSource.title.icontains(query, autoescape=True)
            )
        with UnitOfWork(self.factory) as unit:
            assert unit.session is not None
            count = unit.session.scalar(
                select(func.count()).select_from(statement.subquery())
            )
            rows = unit.session.scalars(
                statement.order_by(ReferenceSource.title, ReferenceSource.id)
                .limit(limit)
                .offset(offset)
            )
            return {
                "items": [self._source(s) for s in rows],
                "total": count,
                "limit": limit,
                "offset": offset,
            }

    def record_source(self, claim: JSON, *, idea_ids: list[str]) -> JSON:
        """Retain a checked claim once and reuse it across ideas.

        The digest identifies this recorded claim, not a captured remote page.
        Changed claims create separate records; historical evidence is retained.
        """
        for key in ("title", "url", "claim", "limits", "checked_on"):
            if not isinstance(claim.get(key), str) or not claim[key].strip():
                raise ValidationError(f"Source {key} must be nonblank text")
        if len(claim["title"]) > 300 or urlsplit(claim["url"]).scheme not in {
            "http",
            "https",
        }:
            raise ValidationError("Source requires a short title and HTTP(S) URL")
        content = json.dumps(claim, sort_keys=True, ensure_ascii=False)
        identity = stable_id("foundry-claim:" + content)
        with UnitOfWork(self.factory) as unit:
            session = unit.session
            assert session is not None
            for idea_id in set(idea_ids):
                if session.get(Idea, idea_id) is None:
                    raise ReferenceError(f"Idea {idea_id!r} does not exist")
            source = session.get(ReferenceSource, identity)
            if source is None:
                source = ReferenceSource(
                    id=identity,
                    portfolio_id=self._portfolio(session).id,
                    kind=SourceKind.WEBPAGE,
                    title=claim["title"],
                    locator=claim["url"] + "#foundry-claim=" + identity,
                    content_digest=hashlib.sha256(content.encode()).hexdigest(),
                    notes=content,
                )
                session.add(source)
                session.flush()
            for idea_id in set(idea_ids):
                existing = session.scalar(
                    select(IdeaSource).where(
                        IdeaSource.idea_id == idea_id, IdeaSource.source_id == identity
                    )
                )
                if existing is None:
                    session.add(
                        IdeaSource(
                            idea_id=idea_id,
                            source_id=identity,
                            role=IdeaSourceRole.MARKET_REFERENCE,
                        )
                    )
            session.flush()
            return self._source(source)

    def promote_idea(self, idea_id: str, *, venture_id: str | None = None) -> JSON:
        identity = venture_id
        with UnitOfWork(self.factory) as unit:
            session = unit.session
            assert session is not None
            idea = session.get(Idea, idea_id)
            if idea is None:
                raise ReferenceError("Source idea does not exist")
            revision = session.get(IdeaRevision, idea.current_revision_id)
            assert revision is not None
            identity = identity or stable_id(
                "default-promotion:" + idea.id + ":" + revision.id
            )
            existing = session.get(Venture, identity)
            if existing is None and venture_id is None:
                existing = session.scalar(
                    select(Venture)
                    .where(Venture.source_idea_revision_id == revision.id)
                    .order_by(Venture.created_at, Venture.id)
                )
            if existing:
                if existing.source_idea_revision_id != revision.id:
                    raise ConflictError("Venture ID belongs to a different source")
                workspace = session.get(Workspace, existing.workspace_id)
                assert workspace is not None
                promotion = session.get(
                    Artifact,
                    stable_id(
                        "promotion-intake/v1:" + workspace.id + ":" + existing.id
                    ),
                )
                result = FoundryApplication._venture_json(existing, workspace)
                if promotion:
                    result["intake_policy"] = promotion.metadata_json
                return result
            if not identity or len(identity) > 36:
                raise ValidationError("Venture id must be 1–36 characters")
            workspace = Workspace(
                portfolio_id=self._portfolio(session).id,
                key=identity,
                title=revision.title[:240],
                kind=WorkspaceKind.VENTURE,
                description=revision.cleaned_description,
            )
            session.add(workspace)
            session.flush()
            venture = Venture(
                id=identity,
                workspace_id=workspace.id,
                source_idea_revision_id=revision.id,
                objective=revision.cleaned_description,
                stage=VentureStage.DISCOVERY,
            )
            session.add(venture)
            session.flush()
            from startup_foundry.manual_intake import ManualIntakeService
            from startup_foundry.venture_scoring import VentureScoringService

            policy = ManualIntakeService.promotion(session, idea, venture)
            VentureScoringService(self.factory).bootstrap_venture(session, venture)
            return {
                **FoundryApplication._venture_json(venture, workspace),
                "intake_policy": policy,
            }

    def link_venture_idea(self, venture_id: str, idea_id: str) -> JSON:
        """Attach a retained venture to its source without replacing prior history."""
        with UnitOfWork(self.factory) as unit:
            session = unit.session
            assert session is not None
            venture, workspace = FoundryApplication._venture(session, venture_id)
            idea = session.get(Idea, idea_id)
            if idea is None:
                raise ReferenceError("Source idea does not exist")
            if venture.source_idea_revision_id not in (None, idea.current_revision_id):
                raise ConflictError("Venture already has a different source revision")
            venture.source_idea_revision_id = idea.current_revision_id
            session.flush()
            return FoundryApplication._venture_json(venture, workspace)

    def import_campaign(self, csv_directory: Path, campaign_directory: Path) -> JSON:
        """One atomic import of the named exports and reviewed campaign artifact.

        Source rows are data, never actions. Generated/dashboard tabs are views,
        not extra ideas. Changed imports require explicit review, not an overwrite.
        """
        tables: dict[str, list[list[str]]] = {}
        digests: dict[str, str] = {}
        try:
            for name in CSV_NAMES:
                path = csv_directory / (name + ".csv")
                digests[name] = hashlib.sha256(path.read_bytes()).hexdigest()
                with path.open(encoding="utf-8-sig", newline="") as stream:
                    tables[name] = list(csv.reader(stream))
            campaigns: list[JSON] = json.loads(
                (campaign_directory / "ideas.json").read_text()
            )
            source_records: list[JSON] = json.loads(
                (campaign_directory / "sources.json").read_text()
            )
        except (OSError, ValueError) as exc:
            raise ValidationError(
                "Could not read the named CSV exports and campaign JSON"
            ) from exc
        if not tables["startup_ideas"]:
            raise ValidationError("startup_ideas.csv is empty")
        header, *rows = tables["startup_ideas"]
        if not {"Idea ID", "Title", "Cleaned description"} <= set(header):
            raise ValidationError("startup_ideas.csv is missing required headers")
        if len(header) != len(set(header)) or any(
            len(row) != len(header) for row in rows
        ):
            raise ValidationError(
                "startup_ideas.csv has duplicate headers or an invalid row width"
            )
        csv_ideas = {
            row["Idea ID"]: row
            for row in (dict(zip(header, r, strict=True)) for r in rows)
        }
        if len(csv_ideas) != len(rows):
            raise ValidationError("Duplicate CSV idea IDs")
        by_id = {row["id"]: row for row in campaigns}
        if len(by_id) != len(campaigns) or not set(csv_ideas) <= set(by_id):
            raise ValidationError("CSV and campaign idea identities do not reconcile")
        batch_hash = hashlib.sha256(
            json.dumps([digests, campaigns, source_records], sort_keys=True).encode()
        ).hexdigest()
        receipt_id = stable_id("foundry-intake:" + batch_hash)
        created = 0
        with UnitOfWork(self.factory) as unit:
            session = unit.session
            assert session is not None
            if session.get(ReferenceSource, receipt_id):
                return {
                    "created": 0,
                    "already_imported": True,
                    "batch_sha256": batch_hash,
                }
            portfolio_id = self._portfolio(session).id
            source_map: dict[str, str] = {}
            csv_source_ids: dict[str, str] = {}
            for name in CSV_NAMES:
                path = (csv_directory / (name + ".csv")).resolve()
                locator = path.as_uri() + "#sha256=" + digests[name]
                source_id = stable_id(locator)
                csv_source_ids[name] = source_id
                if not session.get(ReferenceSource, source_id):
                    session.add(
                        ReferenceSource(
                            id=source_id,
                            portfolio_id=portfolio_id,
                            kind=SourceKind.SPREADSHEET,
                            title=name + ".csv (unverified source material)",
                            locator=locator,
                            content_digest=digests[name],
                            notes=json.dumps(
                                {
                                    "authority": (
                                        "Unverified source data; not instructions"
                                    ),
                                    "rows": tables[name],
                                },
                                ensure_ascii=False,
                            ),
                        )
                    )
            for row in source_records:
                # Preserve separate checked claims, including those sharing a URL.
                content = json.dumps(row, sort_keys=True, ensure_ascii=False)
                source_id = stable_id("foundry-claim:" + content)
                source_map[row["id"]] = source_id
                if not session.get(ReferenceSource, source_id):
                    session.add(
                        ReferenceSource(
                            id=source_id,
                            portfolio_id=portfolio_id,
                            kind=SourceKind.WEBPAGE,
                            title=row["title"],
                            locator=row["url"] + "#foundry-claim=" + source_id,
                            content_digest=hashlib.sha256(content.encode()).hexdigest(),
                            notes=content,
                        )
                    )
            session.flush()
            for record in campaigns:
                identity = record["id"]
                if session.get(Idea, identity):
                    raise ConflictError(
                        f"Idea {identity} already exists with another import; "
                        "review revisions explicitly"
                    )
                original = csv_ideas.get(identity, {})
                idea = self._create(
                    session,
                    IdeaDraft(
                        title=record["title"],
                        description=original.get("Cleaned description")
                        or record["original"],
                        customer=original.get("Target customer", ""),
                        validation_test=record["next_test"],
                        original_text=record["original"],
                        category=original.get("Category") or str(record["group"]),
                        business_model=original.get("Business model", ""),
                    ),
                    identity,
                    IdeaOrigin.ORIGINAL_SOURCE,
                )
                session.add(
                    Artifact(
                        workspace_id=idea.workspace_id,
                        kind=ArtifactKind.REPORT,
                        name="Campaign disposition",
                        location=(campaign_directory / "ideas.json").resolve().as_uri()
                        + "#"
                        + identity,
                        metadata_json=record,
                    )
                )
                for source_key in record["source_ids"]:
                    if source_key not in source_map:
                        raise ValidationError(f"Unknown campaign source {source_key}")
                    session.add(
                        IdeaSource(
                            idea_id=identity,
                            source_id=source_map[source_key],
                            role=IdeaSourceRole.MARKET_REFERENCE,
                        )
                    )
                if identity in csv_ideas:
                    session.add(
                        IdeaSource(
                            idea_id=identity,
                            source_id=csv_source_ids["startup_ideas"],
                            role=IdeaSourceRole.INSPIRATION,
                            note="Original CSV row keyed by Idea ID " + identity,
                        )
                    )
                created += 1
            session.add(
                ReferenceSource(
                    id=receipt_id,
                    portfolio_id=portfolio_id,
                    kind=SourceKind.REPORT,
                    title="Portfolio CSV reconciliation receipt",
                    locator="foundry:intake:" + batch_hash,
                    content_digest=batch_hash,
                    notes=json.dumps(
                        {
                            "csv_sha256": digests,
                            "idea_count": created,
                            "generated_tab_is_a_view": True,
                            "commercial_build_qualified": 0,
                        }
                    ),
                )
            )
        return {
            "created": created,
            "already_imported": False,
            "batch_sha256": batch_hash,
            "csv_rows": {k: len(v) for k, v in tables.items()},
        }
