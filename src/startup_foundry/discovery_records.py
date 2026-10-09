"""Discovery records: reusable sources, competition, idea revisions and relations.

ADR-0019. Source content and market-actor descriptions are data, never
instructions. Nothing here fetches a URL or executes a referenced file; a local
file is only read to compute its digest. Idea revisions are append-only, and
assessments stay attached to the revision they judged.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Annotated, Any, Literal, Self
from urllib.parse import urlsplit, urlunsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from startup_foundry.domain import (
    CriterionScore,
    Evidence,
    Idea,
    IdeaAssessment,
    IdeaMarketActor,
    IdeaOrigin,
    IdeaRelation,
    IdeaRelationKind,
    IdeaRevision,
    IdeaSource,
    IdeaSourceRole,
    MarketActor,
    MarketActorRelation,
    ReferenceSource,
    ScoringCriterion,
    SourceKind,
    Venture,
    Workspace,
    new_id,
)
from startup_foundry.errors import ConflictError, ReferenceError, ValidationError
from startup_foundry.portfolio import (
    IdeaDraft,
    PortfolioService,
    page_bounds,
    stable_id,
)
from startup_foundry.repository import SessionFactory
from startup_foundry.reviews import ReviewService
from startup_foundry.scoring import REVIEWED, ScoringService, canonical
from startup_foundry.snapshots import audit, transaction

JSON = dict[str, Any]
Identity = Annotated[str, Field(min_length=1, max_length=36)]
Reason = Annotated[str, Field(min_length=1, max_length=10000)]
LongText = Annotated[str, Field(max_length=20000)]
Label = Annotated[str, Field(max_length=160)]
Actor = Annotated[str, Field(min_length=1, max_length=200)]
SOURCE_SCHEMA = "foundry-source/v1"
ACTOR_SCHEMA = "market-actor/v1"
MAX_COMPARE = 20
# IdeaRevision columns a revision may change; anything omitted carries over.
REVISION_FIELDS = (
    "title",
    "cleaned_description",
    "narrowing_or_pivot",
    "target_customer",
    "business_model",
    "focused_mvp_scope",
    "estimated_mvp_weeks",
    "key_validation_test",
    "category",
    "venture_type",
    "cluster",
)


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


def _website(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    parts = urlsplit(value.strip())
    if parts.scheme.lower() not in {"http", "https"} or not parts.netloc:
        raise ValueError("website must be an http(s) URL")
    path = "" if parts.path == "/" else parts.path
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), path, parts.query, "")
    )


class SourceInput(Contract):
    """A local document or URL retained as reusable provenance."""

    kind: SourceKind
    title: Annotated[str, Field(min_length=1, max_length=500)]
    locator: Annotated[str, Field(min_length=1, max_length=4000)]
    publisher: Annotated[str, Field(max_length=240)] | None = None
    published_at: date | None = None
    retrieved_at: datetime | None = None
    content_digest: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")] | None = None
    notes: LongText | None = None
    idea_ids: list[Identity] = Field(default_factory=list, max_length=100)
    role: IdeaSourceRole = IdeaSourceRole.INSPIRATION
    link_note: Annotated[str, Field(max_length=10000)] | None = None


class MarketActorInput(Contract):
    name: Annotated[str, Field(min_length=1, max_length=240)]
    website: Annotated[str, Field(max_length=2000)] | None = None
    description: Annotated[str, Field(max_length=10000)] | None = None

    @field_validator("website")
    @classmethod
    def http_website(cls, value: str | None) -> str | None:
        return _website(value)


class ActorLinkInput(Contract):
    """One checked competitive/alternative/partner/benchmark observation."""

    actor_id: Identity | None = None
    actor: MarketActorInput | None = None
    relation: MarketActorRelation
    is_primary: bool = False
    note: Reason
    checked_on: date
    source_ids: list[Identity] = Field(default_factory=list, max_length=50)
    recorded_by: Actor = "local-operator"

    @model_validator(mode="after")
    def one_actor(self) -> Self:
        if (self.actor_id is None) == (self.actor is None):
            raise ValueError("Provide exactly one of actor_id or actor")
        return self


class IdeaRevisionInput(Contract):
    """Fields left null carry over; an empty optional field clears it."""

    title: Annotated[str, Field(min_length=1, max_length=300)] | None = None
    description: Annotated[str, Field(min_length=1, max_length=20000)] | None = None
    narrowing_or_pivot: LongText | None = None
    target_customer: LongText | None = None
    business_model: LongText | None = None
    focused_mvp_scope: LongText | None = None
    estimated_mvp_weeks: float | None = Field(
        default=None, gt=0, le=520, allow_inf_nan=False
    )
    key_validation_test: LongText | None = None
    category: Label | None = None
    venture_type: Label | None = None
    cluster: Label | None = None
    change_reason: Reason
    authored_by: Actor
    expected_revision_id: Identity | None = None
    carry_competition: bool = True


class IdeaRelationInput(Contract):
    source_idea_id: Identity
    target_idea_id: Identity
    kind: IdeaRelationKind
    rationale: Reason


class IdeaCreateInput(Contract):
    """JSON alternative to `idea create` flags with every revision field."""

    id: Identity | None = None
    title: Annotated[str, Field(min_length=1, max_length=300)]
    description: Annotated[str, Field(min_length=1, max_length=20000)]
    original_text: LongText | None = None
    target_customer: LongText | None = None
    business_model: LongText | None = None
    narrowing_or_pivot: LongText | None = None
    focused_mvp_scope: LongText | None = None
    estimated_mvp_weeks: float | None = Field(
        default=None, gt=0, le=520, allow_inf_nan=False
    )
    key_validation_test: LongText | None = None
    category: Label | None = None
    venture_type: Label | None = None
    cluster: Label | None = None
    parent_ids: list[Identity] = Field(default_factory=list, max_length=10)
    derivation_reason: Annotated[str, Field(max_length=10000)] | None = None
    origin: Literal["user_added", "generated_new", "generated_derived"] = "user_added"
    source_ids: list[Identity] = Field(default_factory=list, max_length=50)
    source_role: IdeaSourceRole = IdeaSourceRole.INSPIRATION
    source_note: Annotated[str, Field(max_length=10000)] | None = None
    authored_by: Actor | None = None


def _idea(session: Session, identity: str) -> tuple[Idea, IdeaRevision]:
    idea = session.get(Idea, identity)
    if idea is None:
        raise ReferenceError(f"Idea {identity!r} does not exist")
    revision = session.get(IdeaRevision, idea.current_revision_id)
    if revision is None:
        raise ReferenceError(f"Idea {identity!r} has no current revision")
    return idea, revision


def _require_sources(session: Session, identities: list[str]) -> list[str]:
    unique = list(dict.fromkeys(identities))
    for identity in unique:
        if session.get(ReferenceSource, identity) is None:
            raise ReferenceError(f"Source {identity!r} does not exist")
    return unique


def _file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1 << 20), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ValidationError(f"Source file could not be read: {path}") from exc
    return digest.hexdigest()


def _locate(payload: SourceInput) -> tuple[str, str | None]:
    """Return the stored locator and digest; content identity is in the locator."""
    parts = urlsplit(payload.locator)
    if parts.scheme.lower() in {"http", "https"}:
        if not parts.netloc:
            raise ValidationError("Source URL needs a host")
        digest = payload.content_digest
        if digest is None:
            return payload.locator, None
        separator = "&" if "#" in payload.locator else "#"
        return payload.locator + separator + "sha256=" + digest, digest
    if len(parts.scheme) > 1:
        raise ValidationError(
            "Source locator must be an http(s) URL or a local file path"
        )
    try:
        path = Path(payload.locator).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValidationError(
            f"Local source file does not exist: {payload.locator}"
        ) from exc
    if not path.is_file():
        raise ValidationError(f"Local source is not a regular file: {path}")
    digest = _file_digest(path)
    if payload.content_digest and payload.content_digest != digest:
        raise ValidationError("content_digest does not match the local file")
    return path.as_uri() + "#sha256=" + digest, digest


def _link_source(
    session: Session,
    idea_id: str,
    source_id: str,
    role: IdeaSourceRole,
    note: str | None,
) -> JSON:
    if session.get(Idea, idea_id) is None:
        raise ReferenceError(f"Idea {idea_id!r} does not exist")
    link = session.scalar(
        select(IdeaSource).where(
            IdeaSource.idea_id == idea_id,
            IdeaSource.source_id == source_id,
            IdeaSource.role == role,
        )
    )
    created = link is None
    if link is None:
        link = IdeaSource(idea_id=idea_id, source_id=source_id, role=role, note=note)
        session.add(link)
        session.flush()
    return {
        "idea_id": idea_id,
        "source_id": source_id,
        "role": link.role.value,
        "note": link.note,
        "created": created,
    }


def _actor_json(actor: MarketActor) -> JSON:
    return {
        "id": actor.id,
        "name": actor.name,
        "website": actor.website,
        "description": actor.description,
    }


def _link_json(link: IdeaMarketActor, actor: MarketActor) -> JSON:
    return {
        "link_id": link.id,
        "revision_id": link.idea_revision_id,
        "actor_id": actor.id,
        "name": actor.name,
        "website": actor.website,
        "relation": link.relation.value,
        "is_primary": link.is_primary,
        "note": link.note,
        "checked_on": link.checked_on.isoformat() if link.checked_on else None,
        "source_ids": list(link.source_ids or []),
    }


def _links(session: Session, revision_ids: list[str]) -> list[JSON]:
    if not revision_ids:
        return []
    return [
        _link_json(link, actor)
        for link, actor in session.execute(
            select(IdeaMarketActor, MarketActor)
            .join(MarketActor, IdeaMarketActor.market_actor_id == MarketActor.id)
            .where(IdeaMarketActor.idea_revision_id.in_(revision_ids))
            .order_by(
                IdeaMarketActor.is_primary.desc(),
                MarketActor.name,
                IdeaMarketActor.relation,
            )
        )
    ]


def _relations(
    session: Session, idea_id: str, within: set[str] | None = None
) -> list[JSON]:
    rows = session.scalars(
        select(IdeaRelation)
        .where(
            or_(
                IdeaRelation.source_idea_id == idea_id,
                IdeaRelation.target_idea_id == idea_id,
            )
        )
        .order_by(IdeaRelation.created_at, IdeaRelation.id)
    ).all()
    result = []
    for row in rows:
        outgoing = row.source_idea_id == idea_id
        other = row.target_idea_id if outgoing else row.source_idea_id
        if within is not None and other not in within:
            continue
        title = session.scalar(
            select(IdeaRevision.title)
            .join(Idea, Idea.current_revision_id == IdeaRevision.id)
            .where(Idea.id == other)
        )
        result.append(
            {
                "direction": "outgoing" if outgoing else "incoming",
                "kind": row.kind.value,
                "other_id": other,
                "other_title": title,
                "rationale": row.rationale,
            }
        )
    return result


def idea_projection(session: Session, idea: Idea, current: IdeaRevision) -> JSON:
    """Revisions, relations and competition for `idea show` and the console."""
    revisions = session.scalars(
        select(IdeaRevision)
        .where(IdeaRevision.idea_id == idea.id)
        .order_by(IdeaRevision.revision_number.desc())
    ).all()
    assessed = set(
        session.scalars(
            select(IdeaAssessment.idea_revision_id).where(
                IdeaAssessment.idea_revision_id.in_([r.id for r in revisions])
            )
        )
    )
    links = _links(session, [r.id for r in revisions])
    history = [
        {
            "revision_id": r.id,
            "revision_number": r.revision_number,
            "items": [x for x in links if x["revision_id"] == r.id],
        }
        for r in revisions
        if r.id != current.id
    ]
    return {
        "revisions": [
            {
                "revision_id": r.id,
                "revision_number": r.revision_number,
                "title": r.title,
                "change_reason": r.change_reason,
                "authored_by": r.authored_by,
                "created_at": r.created_at.isoformat(),
                "assessed": r.id in assessed,
                "current": r.id == current.id,
            }
            for r in revisions
        ],
        "relations": _relations(session, idea.id),
        "competition": [x for x in links if x["revision_id"] == current.id],
        "competition_history": [h for h in history if h["items"]],
    }


def venture_lineage(session: Session, venture: Venture) -> JSON | None:
    """Provenance a promoted venture inherits from its source idea (ADR-0020).

    Read-only: the idea keeps its sources, competition and evidence; the venture
    shows them and may cite that evidence in its map (see decision_maps).
    """
    if venture.source_idea_revision_id is None:
        return None
    source_revision = session.get(IdeaRevision, venture.source_idea_revision_id)
    idea = session.get(Idea, source_revision.idea_id) if source_revision else None
    if source_revision is None or idea is None:
        return None
    current = session.get(IdeaRevision, idea.current_revision_id) or source_revision
    sources = [
        {
            "id": source.id,
            "title": source.title,
            "locator": source.locator,
            "kind": source.kind.value,
            "role": link.role.value,
            "note": link.note,
        }
        for source, link in session.execute(
            select(ReferenceSource, IdeaSource)
            .join(IdeaSource, IdeaSource.source_id == ReferenceSource.id)
            .where(IdeaSource.idea_id == idea.id)
            .order_by(ReferenceSource.title, IdeaSource.role)
        )
    ]
    evidence_count = (
        session.scalar(
            select(func.count())
            .select_from(Evidence)
            .where(Evidence.workspace_id == idea.workspace_id)
        )
        or 0
    )
    evidence = [
        {"id": e.id, "summary": e.summary[:200], "kind": e.kind.value}
        for e in session.scalars(
            select(Evidence)
            .where(Evidence.workspace_id == idea.workspace_id)
            .order_by(Evidence.captured_at.desc(), Evidence.id)
            .limit(10)
        )
    ]
    return {
        "idea_id": idea.id,
        "idea_workspace_id": idea.workspace_id,
        "title": current.title,
        "source_revision_number": source_revision.revision_number,
        "current_revision_number": current.revision_number,
        "sources": sources,
        "competition": _links(session, [current.id]),
        "evidence_count": evidence_count,
        "evidence": evidence,
    }


class DiscoveryService:
    """Typed discovery records over the existing Foundry domain tables."""

    def __init__(self, factory: SessionFactory) -> None:
        self.factory = factory
        self.portfolio = PortfolioService(factory)

    # Sources -----------------------------------------------------------------

    def register_source(self, payload: SourceInput) -> JSON:
        locator, digest = _locate(payload)
        identity = stable_id(
            SOURCE_SCHEMA + ":" + canonical([payload.kind.value, locator, digest])
        )
        with transaction(self.factory) as session:
            source = session.get(ReferenceSource, identity)
            created = source is None
            portfolio = PortfolioService._portfolio(session)
            if source is None:
                source = session.scalar(
                    select(ReferenceSource).where(
                        ReferenceSource.portfolio_id == portfolio.id,
                        ReferenceSource.locator == locator,
                    )
                )
                if source is not None:
                    if source.kind != payload.kind or source.content_digest != digest:
                        raise ConflictError(
                            f"Locator is already registered as {source.kind.value} "
                            f"source {source.id}; link that source instead"
                        )
                    created = False
            if source is None:
                source = ReferenceSource(
                    id=identity,
                    portfolio_id=portfolio.id,
                    kind=payload.kind,
                    title=payload.title,
                    locator=locator,
                    publisher=payload.publisher,
                    published_at=payload.published_at,
                    retrieved_at=payload.retrieved_at or datetime.now(UTC),
                    content_digest=digest,
                    notes=payload.notes,
                )
                session.add(source)
                session.flush()
            links = [
                _link_source(session, idea, source.id, payload.role, payload.link_note)
                for idea in dict.fromkeys(payload.idea_ids)
            ]
            return {
                **PortfolioService._source(source),
                "created": created,
                "links": links,
            }

    def link_source(
        self, idea_id: str, source_id: str, role: IdeaSourceRole, note: str | None
    ) -> JSON:
        with transaction(self.factory) as session:
            _require_sources(session, [source_id])
            return _link_source(session, idea_id, source_id, role, note)

    def show_source(self, source_id: str) -> JSON:
        with self.factory() as session:
            source = session.get(ReferenceSource, source_id)
            if source is None:
                raise ReferenceError(f"Source {source_id!r} does not exist")
            linked = [
                {
                    "idea_id": link.idea_id,
                    "title": title,
                    "role": link.role.value,
                    "note": link.note,
                }
                for link, title in session.execute(
                    select(IdeaSource, IdeaRevision.title)
                    .join(Idea, Idea.id == IdeaSource.idea_id)
                    .join(IdeaRevision, Idea.current_revision_id == IdeaRevision.id)
                    .where(IdeaSource.source_id == source_id)
                    .order_by(IdeaSource.idea_id, IdeaSource.role)
                )
            ]
            return {
                **PortfolioService._source(source),
                "linked_ideas": len({x["idea_id"] for x in linked}),
                "links": linked,
            }

    # Market actors -----------------------------------------------------------

    @staticmethod
    def _actor(session: Session, payload: MarketActorInput) -> tuple[MarketActor, bool]:
        name = " ".join(payload.name.split())
        identity = stable_id(
            ACTOR_SCHEMA + ":" + name.casefold() + "|" + (payload.website or "")
        )
        actor = session.get(MarketActor, identity)
        if actor is not None:
            return actor, False
        portfolio = PortfolioService._portfolio(session)
        actor = session.scalar(
            select(MarketActor).where(
                MarketActor.portfolio_id == portfolio.id,
                func.lower(MarketActor.name) == name.lower(),
            )
        )
        if actor is not None:
            if payload.website in (None, actor.website):
                return actor, False
            raise ConflictError(
                f"Market actor {actor.name!r} already exists as {actor.id} with "
                f"website {actor.website or 'unset'}; reference it by actor_id"
            )
        actor = MarketActor(
            id=identity,
            portfolio_id=portfolio.id,
            name=name,
            website=payload.website,
            description=payload.description,
        )
        session.add(actor)
        session.flush()
        return actor, True

    def register_actor(self, payload: MarketActorInput) -> JSON:
        with transaction(self.factory) as session:
            actor, created = self._actor(session, payload)
            return {**_actor_json(actor), "created": created}

    def list_actors(self, *, query: str = "", limit: int = 50, offset: int = 0) -> JSON:
        page_bounds(limit, offset)
        statement = select(MarketActor)
        if query:
            statement = statement.where(
                or_(
                    MarketActor.name.icontains(query, autoescape=True),
                    MarketActor.description.icontains(query, autoescape=True),
                )
            )
        links = (
            select(func.count(IdeaMarketActor.id))
            .where(IdeaMarketActor.market_actor_id == MarketActor.id)
            .scalar_subquery()
        )
        with self.factory() as session:
            total = session.scalar(
                select(func.count()).select_from(statement.subquery())
            )
            rows = session.execute(
                statement.add_columns(links)
                .order_by(MarketActor.name, MarketActor.id)
                .limit(limit)
                .offset(offset)
            )
            return {
                "items": [{**_actor_json(a), "links": n or 0} for a, n in rows],
                "total": total,
                "limit": limit,
                "offset": offset,
            }

    def show_actor(self, actor_id: str) -> JSON:
        with self.factory() as session:
            actor = session.get(MarketActor, actor_id)
            if actor is None:
                raise ReferenceError(f"Market actor {actor_id!r} does not exist")
            rows = session.execute(
                select(IdeaMarketActor, IdeaRevision, Idea)
                .join(IdeaRevision, IdeaMarketActor.idea_revision_id == IdeaRevision.id)
                .join(Idea, Idea.id == IdeaRevision.idea_id)
                .where(IdeaMarketActor.market_actor_id == actor.id)
                .order_by(Idea.id, IdeaRevision.revision_number.desc())
            )
            return {
                **_actor_json(actor),
                "links": [
                    {
                        **_link_json(link, actor),
                        "idea_id": idea.id,
                        "idea_title": revision.title,
                        "revision_number": revision.revision_number,
                        "current_revision": idea.current_revision_id == revision.id,
                    }
                    for link, revision, idea in rows
                ],
            }

    def link_actor(self, idea_id: str, payload: ActorLinkInput) -> JSON:
        with transaction(self.factory) as session:
            idea, revision = _idea(session, idea_id)
            if payload.actor is not None:
                actor, _ = self._actor(session, payload.actor)
            else:
                found = session.get(MarketActor, payload.actor_id)
                if found is None:
                    raise ReferenceError(
                        f"Market actor {payload.actor_id!r} does not exist"
                    )
                actor = found
            sources = _require_sources(session, payload.source_ids)
            values: JSON = {
                "is_primary": payload.is_primary,
                "note": payload.note,
                "checked_on": payload.checked_on,
                "source_ids": sources,
            }
            link = session.scalar(
                select(IdeaMarketActor).where(
                    IdeaMarketActor.idea_revision_id == revision.id,
                    IdeaMarketActor.market_actor_id == actor.id,
                    IdeaMarketActor.relation == payload.relation,
                )
            )
            previous = None
            if link is None:
                link = IdeaMarketActor(
                    idea_revision_id=revision.id,
                    market_actor_id=actor.id,
                    relation=payload.relation,
                    **values,
                )
                session.add(link)
            else:
                previous = _link_json(link, actor)
                for key, value in values.items():
                    setattr(link, key, value)
            session.flush()
            current = _link_json(link, actor)
            changed = previous is not None and previous != current
            if previous is None or changed:
                # The link is revision-scoped and mutable; the audit keeps the
                # superseded observation rather than silently overwriting it.
                audit(
                    session,
                    idea.workspace_id,
                    link.id,
                    "idea_market_actor_updated"
                    if changed
                    else "idea_market_actor_linked",
                    payload.recorded_by,
                    {"idea_id": idea.id, "previous": previous, "current": current},
                )
            return {
                **current,
                "idea_id": idea.id,
                "revision_number": revision.revision_number,
                "created": previous is None,
                "updated": changed,
            }

    # Ideas -------------------------------------------------------------------

    def create_idea(self, payload: IdeaCreateInput) -> JSON:
        if payload.parent_ids and payload.origin == "generated_new":
            raise ValidationError("Ideas with parent_ids have origin generated_derived")
        identity = payload.id or new_id()
        draft = IdeaDraft(
            title=payload.title,
            description=payload.description,
            customer=payload.target_customer or "",
            validation_test=payload.key_validation_test or "",
            parent_ids=payload.parent_ids,
            derivation_reason=payload.derivation_reason or "",
            original_text=payload.original_text or "",
            category=payload.category or "",
            business_model=payload.business_model or "",
            narrowing_or_pivot=payload.narrowing_or_pivot or "",
            focused_mvp_scope=payload.focused_mvp_scope or "",
            estimated_mvp_weeks=payload.estimated_mvp_weeks,
            venture_type=payload.venture_type or "",
            cluster=payload.cluster or "",
            authored_by=payload.authored_by or "foundry-intake-v1",
        )
        with transaction(self.factory) as session:
            sources = _require_sources(session, payload.source_ids)
            self.portfolio._create(session, draft, identity, IdeaOrigin(payload.origin))
            for source in sources:
                _link_source(
                    session, identity, source, payload.source_role, payload.source_note
                )
        return self.portfolio.show_idea(identity)

    def revise(self, idea_id: str, payload: IdeaRevisionInput) -> JSON:
        with transaction(self.factory) as session:
            idea, current = _idea(session, idea_id)
            if (
                payload.expected_revision_id is not None
                and payload.expected_revision_id != current.id
            ):
                raise ConflictError(
                    f"Idea {idea.id} is at revision {current.revision_number} "
                    f"({current.id}); reload before revising"
                )
            before = {name: getattr(current, name) for name in REVISION_FIELDS}
            after = dict(before)
            for name in REVISION_FIELDS:
                value = getattr(
                    payload, "description" if name == "cleaned_description" else name
                )
                if value is not None:
                    after[name] = None if value == "" else value
            changed = [name for name in REVISION_FIELDS if after[name] != before[name]]
            if not changed:
                raise ValidationError(
                    "Revision changes no idea field; record evidence or a review"
                )
            number = (
                session.scalar(
                    select(func.max(IdeaRevision.revision_number)).where(
                        IdeaRevision.idea_id == idea.id
                    )
                )
                or 0
            ) + 1
            revision = IdeaRevision(
                idea_id=idea.id,
                revision_number=number,
                original_text=current.original_text,
                change_reason=payload.change_reason,
                authored_by=payload.authored_by,
                **after,
            )
            session.add(revision)
            session.flush()
            carried = 0
            if payload.carry_competition:
                for link in session.scalars(
                    select(IdeaMarketActor).where(
                        IdeaMarketActor.idea_revision_id == current.id
                    )
                ).all():
                    session.add(
                        IdeaMarketActor(
                            idea_revision_id=revision.id,
                            market_actor_id=link.market_actor_id,
                            relation=link.relation,
                            is_primary=link.is_primary,
                            note=link.note,
                            checked_on=link.checked_on,
                            source_ids=list(link.source_ids or []),
                        )
                    )
                    carried += 1
            idea.current_revision_id = revision.id
            workspace = session.get(Workspace, idea.workspace_id)
            assert workspace is not None
            if "title" in changed:
                workspace.title = revision.title[:240]
            if "cleaned_description" in changed:
                workspace.description = revision.cleaned_description
            receipt = {
                "idea_id": idea.id,
                "revision_id": revision.id,
                "revision_number": number,
                "previous_revision_id": current.id,
                "changed_fields": [
                    "description" if f == "cleaned_description" else f for f in changed
                ],
                "carried_competition": carried,
            }
            audit(
                session,
                idea.workspace_id,
                revision.id,
                "idea_revised",
                payload.authored_by,
                {**receipt, "change_reason": payload.change_reason},
            )
            session.flush()
        return {"receipt": receipt, "idea": self.portfolio.show_idea(idea_id)}

    def relate(self, payload: IdeaRelationInput) -> JSON:
        if payload.source_idea_id == payload.target_idea_id:
            raise ValidationError("An idea cannot be related to itself")
        with transaction(self.factory) as session:
            for identity in (payload.source_idea_id, payload.target_idea_id):
                _idea(session, identity)
            relation = session.scalar(
                select(IdeaRelation).where(
                    IdeaRelation.source_idea_id == payload.source_idea_id,
                    IdeaRelation.target_idea_id == payload.target_idea_id,
                    IdeaRelation.kind == payload.kind,
                )
            )
            created = relation is None
            if relation is None:
                relation = IdeaRelation(
                    source_idea_id=payload.source_idea_id,
                    target_idea_id=payload.target_idea_id,
                    kind=payload.kind,
                    rationale=payload.rationale,
                )
                session.add(relation)
                session.flush()
            elif relation.rationale != payload.rationale:
                raise ConflictError(
                    "This relation is already recorded with a different rationale"
                )
            return {
                "id": relation.id,
                "source_idea_id": relation.source_idea_id,
                "target_idea_id": relation.target_idea_id,
                "kind": relation.kind.value,
                "rationale": relation.rationale,
                "created": created,
            }

    # Comparison --------------------------------------------------------------

    def compare(self, idea_ids: list[str], scorecard_id: str = REVIEWED) -> JSON:
        identities = list(dict.fromkeys(i.strip() for i in idea_ids if i.strip()))
        if not 1 <= len(identities) <= MAX_COMPARE:
            raise ValidationError(f"Compare 1–{MAX_COMPARE} distinct idea IDs")
        reviews = ReviewService(self.factory)
        with self.factory() as session:
            card = ScoringService.read_card(session, scorecard_id)
            items = [
                self._compare_item(session, identity, scorecard_id, set(identities))
                for identity in identities
            ]
        for item in items:
            current = reviews.show(item.pop("workspace_id"))["current"]
            item["disposition"] = current["disposition"] if current else None
            item["investigation_stage"] = (
                current["investigation_stage"] if current else None
            )
        return {
            "scorecard_id": scorecard_id,
            "criteria": card["criteria"],
            "items": items,
            "limits": (
                "Latest assessment of each current revision; missing scores stay "
                "unknown. A stale_revision score judged an earlier revision."
            ),
        }

    @staticmethod
    def _compare_item(
        session: Session, identity: str, scorecard_id: str, cohort: set[str]
    ) -> JSON:
        idea, revision = _idea(session, identity)
        ordered = select(IdeaAssessment).where(
            IdeaAssessment.scorecard_id == scorecard_id
        )
        assessment = session.scalar(
            ordered.where(IdeaAssessment.idea_revision_id == revision.id)
            .order_by(IdeaAssessment.assessment_number.desc())
            .limit(1)
        )
        stale = False
        if assessment is None:
            assessment = session.scalar(
                ordered.join(IdeaRevision)
                .where(IdeaRevision.idea_id == idea.id)
                .order_by(
                    IdeaRevision.revision_number.desc(),
                    IdeaAssessment.assessment_number.desc(),
                )
                .limit(1)
            )
            stale = assessment is not None
        scores: JSON = {}
        assessed_revision = None
        if assessment is not None:
            assessed_revision = session.get(IdeaRevision, assessment.idea_revision_id)
            for score, criterion in session.execute(
                select(CriterionScore, ScoringCriterion)
                .join(ScoringCriterion)
                .where(CriterionScore.assessment_id == assessment.id)
            ):
                scores[criterion.key] = {
                    "raw": score.raw_score,
                    "weighted": score.weighted_contribution,
                    "rationale": score.rationale,
                }
        competition = _links(session, [revision.id])
        ventures = session.scalars(
            select(Venture.id)
            .join(IdeaRevision, Venture.source_idea_revision_id == IdeaRevision.id)
            .where(IdeaRevision.idea_id == idea.id)
            .order_by(Venture.id)
        ).all()
        return {
            "id": idea.id,
            "workspace_id": idea.workspace_id,
            "title": revision.title,
            "revision_id": revision.id,
            "revision_number": revision.revision_number,
            "target_customer": revision.target_customer,
            "assessment_id": assessment.id if assessment else None,
            "assessment_revision_number": assessed_revision.revision_number
            if assessed_revision
            else None,
            "stale_revision": stale,
            "total": assessment.overall_score if assessment else None,
            "grade": assessment.grade if assessment else None,
            "confidence": assessment.confidence.value if assessment else None,
            "scores": scores,
            "competition_count": len(competition),
            "primary_competitors": [
                x["name"]
                for x in competition
                if x["is_primary"] and x["relation"] == "competitor"
            ],
            "relations_in_set": _relations(session, idea.id, cohort),
            "ventures": list(ventures),
        }
