"""Reviewable fusion snapshots and atomic, reversible local portfolio decisions."""

from __future__ import annotations

from typing import Any, Literal, cast

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from startup_foundry.domain import (
    Artifact,
    AuditEvent,
    Decision,
    DecisionStatus,
    Disposition,
    HumanRequest,
    HumanRequestDependency,
    HumanRequestTarget,
    Idea,
    IdeaAssessment,
    IdeaRevision,
    IdentityMixin,
    InvestigationStage,
    PortfolioProposal,
    ProductMaturity,
    ProposalParticipant,
    Venture,
    VentureStage,
    WorkItem,
    WorkItemStatus,
    Workspace,
    WorkspaceKind,
    WorkspaceReview,
)
from startup_foundry.errors import ConflictError, ReferenceError, ValidationError
from startup_foundry.portfolio import IdeaDraft, PortfolioService, stable_id
from startup_foundry.repository import SessionFactory
from startup_foundry.reviews import ReviewInput, ReviewService
from startup_foundry.scoring import digest
from startup_foundry.snapshots import audit, read_snapshot, snapshot, transaction

JSON = dict[str, Any]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ScopeItem(Contract):
    capability: str = Field(min_length=1, max_length=2000)
    treatment: Literal["retained", "combined", "deferred", "excluded", "added"]
    reason: str = Field(min_length=1, max_length=10000)
    provenance: str = Field(min_length=1, max_length=10000)


class WorkTreatment(Contract):
    work_id: str
    treatment: Literal["retain", "supersede", "cancel"] = "retain"
    reason: str = Field(min_length=1, max_length=10000)


class FusionInput(Contract):
    name: str = Field(min_length=1, max_length=240)
    description: str = Field(min_length=1, max_length=20000)
    customer: str = Field(default="", max_length=5000)
    source_idea_ids: list[str] = Field(min_length=1, max_length=10)
    source_venture_ids: list[str] = Field(min_length=1, max_length=10)
    result_venture_id: str = Field(min_length=1, max_length=36)
    request_key: str = Field(min_length=1, max_length=160)
    rationale: str = Field(min_length=1, max_length=20000)
    scope: list[ScopeItem] = Field(min_length=1, max_length=50)
    alternatives: list[str] = Field(min_length=1, max_length=20)
    evidence_links: list[str] = Field(default_factory=list, max_length=50)
    work_treatments: list[WorkTreatment] = Field(default_factory=list, max_length=100)
    next_work_title: str = Field(
        default="Prepare focused venture comparison",
        min_length=1,
        max_length=300,
    )
    actor: str = Field(default="agent", min_length=1, max_length=200)


class ReviseInput(Contract):
    expected_version: int = Field(ge=1)
    name: str = Field(min_length=1, max_length=240)
    description: str = Field(min_length=1, max_length=20000)
    rationale: str = Field(min_length=1, max_length=20000)
    actor: str = Field(min_length=1, max_length=200)
    scope: list[ScopeItem] | None = Field(default=None, max_length=50)
    alternatives: list[str] | None = Field(default=None, max_length=20)
    next_work_title: str | None = Field(default=None, min_length=1, max_length=300)
    work_treatments: list[WorkTreatment] | None = Field(default=None, max_length=100)


class SupersedeInput(Contract):
    expected_version: int = Field(ge=1)
    replacement: FusionInput


class ResolveInput(Contract):
    expected_version: int = Field(ge=1)
    revision_id: str
    action: Literal["accept", "reject", "reverse"]
    rationale: str = Field(min_length=1, max_length=20000)
    actor: str = Field(min_length=1, max_length=200)
    actor_kind: Literal["user", "agent"]
    delegation_id: str | None = None
    request_key: str = Field(min_length=1, max_length=160)
    activity_digest: str | None = None
    downstream_treatment: str | None = Field(default=None, max_length=20000)


class DelegationInput(Contract):
    revision_id: str
    delegate: str = Field(min_length=1, max_length=200)
    action: Literal["accept", "reject", "reverse"]
    reason: str = Field(min_length=1, max_length=20000)
    human_actor: str = Field(min_length=1, max_length=200)


# Words an accepted decision uses when it retires a still-pending proposal.
STALE_MARKERS = ("supersed", "historical", "lineage")


def proposal_staleness(session: Session, p: PortfolioProposal) -> str | None:
    """Why a still-proposed fusion is stale, or None (ADR-0020; read-only).

    Stale when its result venture already exists, or when a participant's
    workspace has an accepted decision, made after the proposal was created,
    that names the proposal and records it as superseded/historical lineage.
    The proposal and its history are unchanged; a human still resolves it.
    """
    if p.state != "proposed":
        return None
    content = ProposalService._content(session, p)
    result_venture = str(content["proposal"]["result_venture_id"])
    if session.get(Venture, result_venture) is not None:
        return "Result venture " + result_venture + " already exists"
    workspaces = set()
    for row in session.scalars(
        select(ProposalParticipant).where(ProposalParticipant.proposal_id == p.id)
    ):
        entity: Idea | Venture | None = (
            session.get(Idea, row.idea_id)
            if row.idea_id
            else session.get(Venture, row.venture_id)
            if row.venture_id
            else None
        )
        if entity is not None:
            workspaces.add(entity.workspace_id)
    if not workspaces:
        return None
    for decision in session.scalars(
        select(Decision)
        .where(
            Decision.workspace_id.in_(sorted(workspaces)),
            Decision.status == DecisionStatus.ACCEPTED,
            Decision.decided_at > p.created_at,
        )
        .order_by(Decision.decided_at.desc(), Decision.id)
    ):
        text = (decision.summary + "\n" + decision.rationale).lower()
        if (p.id in text or p.id[:8] in text) and any(
            marker in text for marker in STALE_MARKERS
        ):
            return "Accepted decision " + decision.id + " records it as historical"
    return None


def stale_proposals_for_venture(session: Session, venture_id: str) -> list[JSON]:
    rows = session.scalars(
        select(PortfolioProposal)
        .join(ProposalParticipant)
        .where(
            PortfolioProposal.state == "proposed",
            ProposalParticipant.venture_id == venture_id,
        )
        .distinct()
        .order_by(PortfolioProposal.created_at.desc())
    )
    return [
        {
            "id": p.id,
            "title": ProposalService._content(session, p)["proposal"]["name"],
            "reason": reason,
            "url": "/proposals/" + p.id,
        }
        for p in rows
        if (reason := proposal_staleness(session, p))
    ]


class ProposalService:
    def __init__(self, factory: SessionFactory) -> None:
        self.factory = factory

    @staticmethod
    def _get(session: Session, identity: str) -> PortfolioProposal:
        p = session.get(PortfolioProposal, identity)
        if not p:
            raise ReferenceError("Proposal missing")
        return p

    @staticmethod
    def _source_state(session: Session, payload: FusionInput, portfolio: str) -> JSON:
        states = []
        workspaces = set()
        participants: list[tuple[str, list[str], type[Idea] | type[Venture]]] = [
            ("idea", payload.source_idea_ids, Idea),
            ("venture", payload.source_venture_ids, Venture),
        ]
        for kind, ids, model in participants:
            if len(set(ids)) != len(ids):
                raise ValidationError("Duplicate source participant")
            for identity in sorted(ids):
                entity = cast(Idea | Venture | None, session.get(model, identity))
                if not entity:
                    raise ReferenceError("Source participant missing")
                w = session.get(Workspace, entity.workspace_id)
                if not w or w.portfolio_id != portfolio:
                    raise ReferenceError("Participants must belong to same portfolio")
                workspaces.add(w.id)
                revision = (
                    entity.current_revision_id
                    if isinstance(entity, Idea)
                    else entity.source_idea_revision_id
                )
                source_revision = (
                    session.get(IdeaRevision, revision) if revision else None
                )
                state = {
                    "kind": kind,
                    "id": identity,
                    "workspace_id": w.id,
                    "version": entity.version_id,
                    "workspace_version": w.version_id,
                    "title": w.title,
                    "revision_id": revision,
                    "objective": entity.objective
                    if isinstance(entity, Venture)
                    else source_revision.cleaned_description
                    if source_revision
                    else "",
                }
                states.append(state)
        reviews = []
        works: list[JSON] = []
        for workspace_id in sorted(workspaces):
            review = session.scalar(
                select(WorkspaceReview)
                .where(WorkspaceReview.workspace_id == workspace_id)
                .order_by(WorkspaceReview.revision.desc())
                .limit(1)
            )
            reviews.append(
                {
                    "workspace_id": workspace_id,
                    "id": review.id if review else None,
                    "revision": review.revision if review else 0,
                    "state": ReviewService._json(session, review) if review else None,
                }
            )
            works.extend(
                {
                    "id": x.id,
                    "workspace_id": workspace_id,
                    "version": x.version_id,
                    "status": x.status.value,
                    "title": x.title,
                    "owner": x.owner,
                }
                for x in session.scalars(
                    select(WorkItem)
                    .where(WorkItem.workspace_id == workspace_id)
                    .order_by(WorkItem.id)
                )
            )
        requests = [
            {
                "id": r.id,
                "version": r.version_id,
                "response_id": r.response_artifact_id,
                "review_id": r.review_artifact_id,
                "status": r.status,
            }
            for r in session.scalars(
                select(HumanRequest)
                .where(
                    HumanRequest.id.in_(
                        select(HumanRequestTarget.request_id).where(
                            HumanRequestTarget.workspace_id.in_(workspaces)
                        )
                    )
                )
                .order_by(HumanRequest.id)
            )
        ]
        if len({t.work_id for t in payload.work_treatments}) != len(
            payload.work_treatments
        ):
            raise ValidationError("Duplicate work treatment")
        work_map = {w["id"]: w for w in works}
        for treatment in payload.work_treatments:
            work = work_map.get(treatment.work_id)
            if not work:
                raise ReferenceError("Work treatment must belong to a source workspace")
            if treatment.treatment != "retain" and work["status"] not in {
                "todo",
                "ready",
                "blocked",
            }:
                raise ConflictError("Claimed/completed work can only be retained")
        return {
            "sources": states,
            "reviews": reviews,
            "work": works,
            "requests": requests,
        }

    @staticmethod
    def _next_idea(session: Session) -> str:
        ids = list(session.scalars(select(Idea.id).where(Idea.id.like("D%"))))
        numbers = [int(i[1:]) for i in ids if i[1:].isdigit()]
        return f"D{max(numbers, default=0) + 1:03d}"

    @staticmethod
    def _content(session: Session, p: PortfolioProposal) -> JSON:
        content = read_snapshot(
            session,
            p.revision_artifact_id,
            p.workspace_id,
            "portfolio-fusion-proposal/v1",
        )
        FusionInput.model_validate(content["proposal"])
        return content

    @staticmethod
    def _source_key(portfolio: str, payload: FusionInput) -> str:
        return digest(
            {
                "portfolio": portfolio,
                "kind": "fusion",
                "ideas": sorted(set(payload.source_idea_ids)),
                "ventures": sorted(set(payload.source_venture_ids)),
            }
        )

    @staticmethod
    def _semantic(payload: FusionInput) -> JSON:
        value = payload.model_dump(
            mode="json", exclude={"request_key", "actor", "result_venture_id"}
        )
        value["source_idea_ids"] = sorted(payload.source_idea_ids)
        value["source_venture_ids"] = sorted(payload.source_venture_ids)
        return value

    def create(self, payload: FusionInput) -> JSON:
        try:
            with transaction(self.factory) as session:
                return self._create(session, payload)
        except ConflictError:
            # A concurrent insert is protected by the pending-source unique key.
            # Re-read in a fresh transaction; equivalent requests can reuse it.
            with transaction(self.factory) as session:
                return self._create(session, payload)

    def _create(self, session: Session, payload: FusionInput) -> JSON:
        owner = session.get(Venture, "v-foundry")
        if not owner:
            raise ReferenceError("Foundry coordination venture required")
        workspace = session.get(Workspace, owner.workspace_id)
        assert workspace
        receipt_id = stable_id(
            "portfolio-fusion-request/v1:" + workspace.id + ":" + payload.request_key
        )
        receipt = session.get(Artifact, receipt_id)
        if receipt:
            if receipt.metadata_json["payload_digest"] != digest(
                payload.model_dump(mode="json")
            ):
                raise ConflictError("Request key reused with different proposal")
            return self._json(
                session, self._get(session, receipt.metadata_json["proposal_id"])
            )
        existing = session.scalar(
            select(PortfolioProposal).where(
                PortfolioProposal.portfolio_id == workspace.portfolio_id,
                PortfolioProposal.request_key == payload.request_key,
            )
        )
        if existing:
            if self._content(session, existing)["creation_digest"] != digest(
                payload.model_dump(mode="json")
            ):
                raise ConflictError("Seed key used with different proposal")
            return self._json(session, existing)
        state = self._source_state(session, payload, workspace.portfolio_id)
        source_key = self._source_key(workspace.portfolio_id, payload)
        pending = next(
            (
                p
                for p in session.scalars(
                    select(PortfolioProposal).where(
                        PortfolioProposal.portfolio_id == workspace.portfolio_id,
                        PortfolioProposal.state == "proposed",
                    )
                )
                if self._source_key(
                    workspace.portfolio_id,
                    FusionInput.model_validate(self._content(session, p)["proposal"]),
                )
                == source_key
            ),
            None,
        )
        if pending:
            draft = FusionInput.model_validate(
                self._content(session, pending)["proposal"]
            )
            if self._semantic(draft) != self._semantic(payload):
                raise ConflictError(
                    "These sources already have a pending proposal; explicitly "
                    "revise or supersede it"
                )
            pending.pending_source_key = source_key
            snapshot(
                session,
                workspace.id,
                "portfolio-fusion-request/v1",
                {
                    "proposal_id": pending.id,
                    "payload_digest": digest(payload.model_dump(mode="json")),
                },
                key=payload.request_key,
            )
            return self._json(session, pending)
        if session.get(Venture, payload.result_venture_id):
            raise ConflictError("Result venture ID already exists")
        content = {
            "proposal": payload.model_dump(mode="json"),
            "creation_digest": digest(payload.model_dump(mode="json")),
            "source_state": state,
            "source_digest": digest(state),
            "result_idea_id": self._next_idea(session),
            "previous_revision_id": None,
            "revision": 1,
        }
        artifact = snapshot(
            session, workspace.id, "portfolio-fusion-proposal/v1", content
        )
        p = PortfolioProposal(
            id=stable_id(
                "proposal:" + workspace.portfolio_id + ":" + payload.request_key
            ),
            portfolio_id=workspace.portfolio_id,
            workspace_id=workspace.id,
            revision_artifact_id=artifact.id,
            request_key=payload.request_key,
            pending_source_key=source_key,
            state="proposed",
        )
        session.add(p)
        session.flush()
        for identity in payload.source_idea_ids:
            session.add(
                ProposalParticipant(proposal_id=p.id, role="source", idea_id=identity)
            )
        for identity in payload.source_venture_ids:
            session.add(
                ProposalParticipant(
                    proposal_id=p.id, role="source", venture_id=identity
                )
            )
        audit(
            session,
            p.workspace_id,
            p.id,
            "proposal_created",
            payload.actor,
            {"revision_id": artifact.id},
        )
        snapshot(
            session,
            workspace.id,
            "portfolio-fusion-request/v1",
            {
                "proposal_id": p.id,
                "payload_digest": digest(payload.model_dump(mode="json")),
            },
            key=payload.request_key,
        )
        return self._json(session, p)

    def supersede(self, identity: str, payload: SupersedeInput) -> JSON:
        with transaction(self.factory) as session:
            p = self._get(session, identity)
            if p.state != "proposed" or p.version_id != payload.expected_version:
                raise ConflictError("Only the exact pending version can be superseded")
            if self._source_key(
                p.portfolio_id, payload.replacement
            ) != self._source_key(
                p.portfolio_id,
                FusionInput.model_validate(self._content(session, p)["proposal"]),
            ):
                raise ValidationError(
                    "Supersession must retain the source participant set"
                )
            p.state = "superseded"
            p.pending_source_key = None
            session.flush()
            replacement = self._create(session, payload.replacement)
            if replacement["id"] == p.id:
                raise ConflictError("Supersession needs a new request key")
            audit(
                session,
                p.workspace_id,
                p.id,
                "proposal_superseded",
                payload.replacement.actor,
                {
                    "replacement_id": replacement["id"],
                    "reason": payload.replacement.rationale,
                },
            )
            return replacement

    def revise(self, identity: str, payload: ReviseInput) -> JSON:
        with transaction(self.factory) as session:
            p = self._get(session, identity)
            if p.state != "proposed" or p.version_id != payload.expected_version:
                raise ConflictError(
                    "Proposal changed or resolved; refresh before editing"
                )
            prior = self._content(session, p)
            draft = FusionInput.model_validate(prior["proposal"])
            update = payload.model_dump(
                mode="json", exclude={"expected_version"}, exclude_none=True
            )
            draft = FusionInput.model_validate(
                {**draft.model_dump(mode="json"), **update}
            )
            state = self._source_state(session, draft, p.portfolio_id)
            content = {
                **prior,
                "proposal": draft.model_dump(mode="json"),
                "source_state": state,
                "source_digest": digest(state),
                "previous_revision_id": p.revision_artifact_id,
                "revision": prior["revision"] + 1,
                "result_idea_id": self._next_idea(session),
            }
            artifact = snapshot(
                session, p.workspace_id, "portfolio-fusion-proposal/v1", content
            )
            p.revision_artifact_id = artifact.id
            audit(
                session,
                p.workspace_id,
                p.id,
                "proposal_revised",
                payload.actor,
                {"revision_id": artifact.id, "reason": payload.rationale},
            )
            session.flush()
            return self._json(session, p)

    def delegate(self, identity: str, payload: DelegationInput) -> JSON:
        """Called by the local human operator; never inferred from answer text."""
        with transaction(self.factory) as session:
            p = self._get(session, identity)
            if p.revision_artifact_id != payload.revision_id:
                raise ConflictError("Delegation must identify current exact revision")
            artifact = snapshot(
                session,
                p.workspace_id,
                "fusion-delegation/v1",
                {"proposal_id": p.id, **payload.model_dump(mode="json")},
            )
            audit(
                session,
                p.workspace_id,
                p.id,
                "human_delegation_recorded",
                payload.human_actor,
                {"delegation_id": artifact.id},
            )
            return {"id": artifact.id}

    @staticmethod
    def _authority(
        session: Session, p: PortfolioProposal, payload: ResolveInput
    ) -> None:
        if not payload.rationale.strip() or not payload.actor.strip():
            raise ValidationError("Decision needs actor and rationale")
        if payload.actor_kind == "user":
            if payload.actor.lower().startswith(("agent", "codex")):
                raise ValidationError(
                    "Agent attribution requires verified human delegation"
                )
            return
        if not payload.delegation_id:
            raise ValidationError(
                "Agent resolution requires exact explicit human delegation receipt"
            )
        receipt = read_snapshot(
            session, payload.delegation_id, p.workspace_id, "fusion-delegation/v1"
        )
        delegated = DelegationInput.model_validate(
            {k: v for k, v in receipt.items() if k != "proposal_id"}
        )
        registered = session.scalar(
            select(AuditEvent.id).where(
                AuditEvent.entity_id == p.id,
                AuditEvent.event_type == "human_delegation_recorded",
                AuditEvent.actor == delegated.human_actor,
                AuditEvent.payload["delegation_id"].as_string()
                == payload.delegation_id,
            )
        )
        if (
            not registered
            or receipt["proposal_id"] != p.id
            or delegated.revision_id != payload.revision_id
            or delegated.action != payload.action
            or delegated.delegate != payload.actor
        ):
            raise ValidationError(
                "Delegation does not cover actor, action and exact revision"
            )

    def _after_create(self, session: Session) -> None:
        """Transaction fault-injection seam; no external effects."""

    def _apply(
        self,
        session: Session,
        p: PortfolioProposal,
        content: JSON,
        payload: ResolveInput,
    ) -> JSON:
        draft = FusionInput.model_validate(content["proposal"])
        idea_id = content["result_idea_id"]
        state = self._source_state(session, draft, p.portfolio_id)
        if digest(state) != content["source_digest"]:
            raise ConflictError(
                "Source state, work or answer changed; edit to refresh effects preview"
            )
        if session.get(Idea, idea_id) or session.get(Venture, draft.result_venture_id):
            raise ConflictError("Reserved result ID now occupied; refresh proposal")
        parent_service = PortfolioService(self.factory)
        idea = parent_service._create(
            session,
            IdeaDraft(
                title=draft.name,
                description=draft.description,
                parent_ids=draft.source_idea_ids,
                derivation_reason=payload.rationale,
                customer=draft.customer,
                validation_test=draft.next_work_title,
            ),
            idea_id,
        )
        workspace = Workspace(
            portfolio_id=p.portfolio_id,
            key=draft.result_venture_id,
            title=draft.name,
            kind=WorkspaceKind.VENTURE,
            description=draft.description,
        )
        session.add(workspace)
        session.flush()
        venture = Venture(
            id=draft.result_venture_id,
            workspace_id=workspace.id,
            source_idea_revision_id=idea.current_revision_id,
            objective=draft.description,
            stage=VentureStage.DISCOVERY,
        )
        session.add(venture)
        session.flush()
        session.add_all(
            [
                ProposalParticipant(proposal_id=p.id, role="result", idea_id=idea.id),
                ProposalParticipant(
                    proposal_id=p.id, role="result", venture_id=venture.id
                ),
            ]
        )
        self._after_create(session)
        next_work = WorkItem(
            workspace_id=workspace.id,
            title=draft.next_work_title,
            description=draft.description,
            kind="investigation",
            status=WorkItemStatus.READY,
            owner="agent",
            acceptance_criteria=(
                "Prepare bounded comparison; participation, external action"
                " and payer gates remain separate"
            ),
        )
        session.add(next_work)
        session.flush()
        changed = []
        work_map = {w["id"]: w for w in state["work"]}
        for t in draft.work_treatments:
            if t.work_id not in work_map:
                raise ReferenceError("Work treatment references foreign work")
            if t.treatment == "retain":
                continue
            w = session.get(WorkItem, t.work_id)
            assert w
            if w.status not in {
                WorkItemStatus.TODO,
                WorkItemStatus.READY,
                WorkItemStatus.BLOCKED,
            }:
                raise ConflictError("Cannot supersede claimed/completed work")
            w.status = WorkItemStatus.CANCELLED
            audit(
                session,
                w.workspace_id,
                w.id,
                "fusion_work_" + t.treatment,
                payload.actor,
                {
                    "proposal_id": p.id,
                    "target_work_id": next_work.id,
                    "reason": t.reason,
                },
            )
            changed.append(t.work_id)
        for old in state["reviews"]:
            ReviewService._append(
                session,
                ReviewInput(
                    workspace_id=old["workspace_id"],
                    expected_revision=old["revision"],
                    investigation_stage=InvestigationStage.COMPARISON,
                    product_maturity=old["state"]["product_maturity"]
                    if old["state"]
                    else ProductMaturity.CONCEPT,
                    disposition=Disposition.HOLD,
                    next_action="Continued in " + venture.id,
                    reason=payload.rationale + " · proposal " + p.id,
                    author=payload.actor,
                ),
            )
        for target in [workspace.id, idea.workspace_id]:
            ReviewService._append(
                session,
                ReviewInput(
                    workspace_id=target,
                    expected_revision=0,
                    investigation_stage=InvestigationStage.COMPARISON,
                    product_maturity=ProductMaturity.CONCEPT,
                    disposition=Disposition.PURSUE,
                    next_action=draft.next_work_title,
                    next_work_item_id=next_work.id if target == workspace.id else None,
                    reason=payload.rationale,
                    author=payload.actor,
                ),
            )
        for r in state["requests"]:
            if not session.scalar(
                select(HumanRequestTarget.id).where(
                    HumanRequestTarget.request_id == r["id"],
                    HumanRequestTarget.workspace_id == workspace.id,
                )
            ):
                session.add(
                    HumanRequestTarget(request_id=r["id"], workspace_id=workspace.id)
                )
        session.flush()
        result = {
            "idea_id": idea.id,
            "venture_id": venture.id,
            "workspace_id": workspace.id,
            "idea_workspace_id": idea.workspace_id,
            "work_id": next_work.id,
            "changed_work_ids": changed,
            "source_state": state,
        }
        result["initial_activity_context"] = self._activity_context(session, result)
        result["initial_activity_digest"] = digest(result["initial_activity_context"])
        return result

    @staticmethod
    def _activity_context(session: Session, result: JSON) -> JSON:
        from startup_foundry.domain import (
            Decision,
            Evidence,
            VentureAssessment,
        )

        ids = [result["workspace_id"], result["idea_workspace_id"]]
        records: JSON = {}
        idea = session.get(Idea, result["idea_id"])
        venture = session.get(Venture, result["venture_id"])
        assert idea and venture
        revision = session.get(IdeaRevision, idea.current_revision_id)
        assert revision
        records["idea_definition"] = {
            "id": idea.id,
            "version": idea.version_id,
            "revision_id": revision.id,
            "revision_number": revision.revision_number,
            "title": revision.title,
            "description": revision.cleaned_description,
            "customer": revision.target_customer,
            "validation_test": revision.key_validation_test,
        }
        records["venture_definition"] = {
            "id": venture.id,
            "version": venture.version_id,
            "objective": venture.objective,
            "source_revision_id": venture.source_idea_revision_id,
            "stage": venture.stage.value,
            "focus": venture.current_focus,
            "budget": str(venture.budget_limit)
            if venture.budget_limit is not None
            else None,
            "currency": venture.budget_currency,
        }
        records["workspace_definitions"] = [
            {
                "id": w.id,
                "version": w.version_id,
                "title": w.title,
                "description": w.description,
                "kind": w.kind.value,
            }
            for w in session.scalars(
                select(Workspace).where(Workspace.id.in_(ids)).order_by(Workspace.id)
            )
        ]
        records["requests"] = [
            {
                "id": r.id,
                "version": r.version_id,
                "definition_id": r.definition_artifact_id,
                "response_id": r.response_artifact_id,
                "review_id": r.review_artifact_id,
                "status": r.status,
            }
            for r in session.scalars(
                select(HumanRequest)
                .where(
                    HumanRequest.id.in_(
                        select(HumanRequestTarget.request_id).where(
                            HumanRequestTarget.workspace_id.in_(ids)
                        )
                    )
                    | HumanRequest.workspace_id.in_(ids)
                )
                .order_by(HumanRequest.id)
            )
        ]
        records["request_targets"] = [
            {
                "id": t.id,
                "request_id": t.request_id,
                "workspace_id": t.workspace_id,
                "work_id": t.work_item_id,
            }
            for t in session.scalars(
                select(HumanRequestTarget)
                .where(HumanRequestTarget.workspace_id.in_(ids))
                .order_by(HumanRequestTarget.id)
            )
        ]
        records["request_dependencies"] = [
            {
                "id": d.id,
                "version": d.version_id,
                "work_id": d.work_item_id,
                "satisfied_response_id": d.satisfied_response_id,
                "other_causes": d.other_causes,
            }
            for d in session.scalars(
                select(HumanRequestDependency)
                .where(
                    HumanRequestDependency.target_id.in_(
                        select(HumanRequestTarget.id).where(
                            HumanRequestTarget.workspace_id.in_(ids)
                        )
                    )
                )
                .order_by(HumanRequestDependency.id)
            )
        ]
        models: list[
            type[Evidence]
            | type[Decision]
            | type[Artifact]
            | type[WorkspaceReview]
            | type[WorkItem]
            | type[AuditEvent]
        ] = [
            Evidence,
            Decision,
            Artifact,
            WorkspaceReview,
            WorkItem,
            AuditEvent,
        ]
        for model in models:
            records[model.__tablename__] = [
                {"id": r.id, "version": getattr(r, "version_id", None)}
                for r in cast(
                    list[IdentityMixin],
                    list(
                        session.scalars(
                            select(model)
                            .where(model.workspace_id.in_(ids))
                            .order_by(model.id)
                        )
                    ),
                )
            ]
        records["scores"] = list(
            session.scalars(
                select(VentureAssessment.id)
                .where(VentureAssessment.venture_id == result["venture_id"])
                .order_by(VentureAssessment.id)
            )
        )
        records["idea_scores"] = list(
            session.scalars(
                select(IdeaAssessment.id)
                .where(
                    IdeaAssessment.idea_revision_id.in_(
                        select(IdeaRevision.id).where(IdeaRevision.idea_id == idea.id)
                    )
                )
                .order_by(IdeaAssessment.id)
            )
        )
        records["source_reviews"] = [
            r.id
            for r in session.scalars(
                select(WorkspaceReview)
                .where(
                    WorkspaceReview.workspace_id.in_(
                        [x["workspace_id"] for x in result["source_state"]["reviews"]]
                    )
                )
                .order_by(WorkspaceReview.id)
            )
        ]
        records["source_work"] = [
            {"id": r.id, "version": r.version_id}
            for r in session.scalars(
                select(WorkItem)
                .where(
                    WorkItem.workspace_id.in_(
                        [x["workspace_id"] for x in result["source_state"]["reviews"]]
                    )
                )
                .order_by(WorkItem.id)
            )
        ]
        return records

    @classmethod
    def _activity(cls, session: Session, result: JSON) -> str:
        return digest(cls._activity_context(session, result))

    def _reverse(
        self,
        session: Session,
        p: PortfolioProposal,
        content: JSON,
        payload: ResolveInput,
        result: JSON,
    ) -> None:
        activity = self._activity(session, result)
        if activity != result["initial_activity_digest"] and (
            payload.activity_digest != activity
            or not payload.downstream_treatment
            or not payload.downstream_treatment.strip()
        ):
            raise ConflictError(
                "Downstream activity exists; review digest and provide "
                "explicit state/work treatment"
            )
        # Never restore over a later source review. Such a source needs a new proposal.
        for old in result["source_state"]["reviews"]:
            latest = session.scalar(
                select(WorkspaceReview)
                .where(WorkspaceReview.workspace_id == old["workspace_id"])
                .order_by(WorkspaceReview.revision.desc())
                .limit(1)
            )
            assert latest
            if latest.revision != old["revision"] + 1:
                raise ConflictError(
                    "Source has later state; create a new explicit treatment "
                    "rather than replay old review"
                )
            prior = old["state"]
            ReviewService._append(
                session,
                ReviewInput(
                    workspace_id=old["workspace_id"],
                    expected_revision=latest.revision,
                    investigation_stage=prior["investigation_stage"]
                    if prior
                    else InvestigationStage.COMPARISON,
                    product_maturity=prior["product_maturity"]
                    if prior
                    else ProductMaturity.CONCEPT,
                    disposition=prior["disposition"] if prior else Disposition.PURSUE,
                    next_action=prior["next_action"]
                    if prior
                    else "Review reopened source",
                    next_work_item_id=prior["next_work_item_id"] if prior else None,
                    reason=payload.rationale,
                    author=payload.actor,
                ),
            )
        for old in result["source_state"]["work"]:
            if old["id"] in result["changed_work_ids"]:
                w = session.get(WorkItem, old["id"])
                assert w
                if w.version_id != old["version"] + 1:
                    raise ConflictError(
                        "Source work changed after fusion; explicit new treatment "
                        "required"
                    )
                w.status = WorkItemStatus(old["status"])
                audit(
                    session,
                    w.workspace_id,
                    w.id,
                    "fusion_work_reopened",
                    payload.actor,
                    {"proposal_id": p.id, "reason": payload.rationale},
                )
        for identity in [result["workspace_id"], result["idea_workspace_id"]]:
            current = session.scalar(
                select(WorkspaceReview)
                .where(WorkspaceReview.workspace_id == identity)
                .order_by(WorkspaceReview.revision.desc())
                .limit(1)
            )
            assert current
            ReviewService._append(
                session,
                ReviewInput(
                    workspace_id=identity,
                    expected_revision=current.revision,
                    investigation_stage=current.investigation_stage,
                    product_maturity=current.product_maturity,
                    disposition=Disposition.HOLD,
                    next_action=payload.downstream_treatment
                    or "Fusion reversed; source investigations reopened",
                    reason=payload.rationale,
                    author=payload.actor,
                ),
            )
        work = session.get(WorkItem, result["work_id"])
        assert work
        if work.status == WorkItemStatus.READY:
            work.status = WorkItemStatus.CANCELLED
            audit(
                session,
                work.workspace_id,
                work.id,
                "fusion_target_held",
                payload.actor,
                {"reason": payload.rationale},
            )

    def resolve(self, identity: str, payload: ResolveInput) -> JSON:
        with transaction(self.factory) as session:
            p = self._get(session, identity)
            old = session.get(
                Artifact,
                stable_id(
                    "portfolio-fusion-resolution/v1:"
                    + p.workspace_id
                    + ":"
                    + p.id
                    + ":"
                    + payload.request_key
                ),
            )
            if old:
                if old.metadata_json["payload_digest"] != digest(
                    payload.model_dump(mode="json")
                ):
                    raise ConflictError("Resolution key reused")
                return {
                    **old.metadata_json,
                    "id": old.id,
                    "state": p.state,
                    "version": p.version_id,
                }
            self._authority(session, p, payload)
            if (
                p.version_id != payload.expected_version
                or p.revision_artifact_id != payload.revision_id
            ):
                raise ConflictError("Proposal changed; review exact current revision")
            content = self._content(session, p)
            result = None
            if payload.action == "reverse":
                if p.state != "applied" or not p.resolution_artifact_id:
                    raise ConflictError("Only applied fusion can reverse")
                accepted = read_snapshot(
                    session,
                    p.resolution_artifact_id,
                    p.workspace_id,
                    "portfolio-fusion-resolution/v1",
                )
                result = accepted["result"]
                self._reverse(session, p, content, payload, result)
                p.state = "reversed"
            else:
                if p.state != "proposed":
                    raise ConflictError("Proposal already resolved")
                if payload.action == "accept":
                    result = self._apply(session, p, content, payload)
                    p.state = "applied"
                else:
                    p.state = "rejected"
            p.pending_source_key = None
            resolution = snapshot(
                session,
                p.workspace_id,
                "portfolio-fusion-resolution/v1",
                {
                    "proposal_id": p.id,
                    **payload.model_dump(mode="json"),
                    "payload_digest": digest(payload.model_dump(mode="json")),
                    "result": result,
                    "previous_resolution_id": p.resolution_artifact_id,
                    "state": p.state,
                },
                key=p.id + ":" + payload.request_key,
            )
            p.resolution_artifact_id = resolution.id
            audit(
                session,
                p.workspace_id,
                p.id,
                "fusion_" + p.state,
                payload.actor,
                {"resolution_id": resolution.id, "revision_id": payload.revision_id},
            )
            session.flush()
            return {
                **resolution.metadata_json,
                "id": resolution.id,
                "version": p.version_id,
            }

    @classmethod
    def _json(cls, session: Session, p: PortfolioProposal) -> JSON:
        content = cls._content(session, p)
        revisions = [
            {"id": a.id, **a.metadata_json}
            for a in session.scalars(
                select(Artifact)
                .where(
                    Artifact.workspace_id == p.workspace_id,
                    Artifact.name == "portfolio-fusion-proposal/v1",
                )
                .order_by(Artifact.created_at.desc())
            )
            if a.metadata_json.get("creation_digest") == content["creation_digest"]
        ]
        for index, revision in enumerate(revisions):
            prior = (
                revisions[index + 1]["proposal"] if index + 1 < len(revisions) else None
            )
            revision["differences"] = [
                {"field": key, "previous": prior.get(key), "current": value}
                for key, value in revision["proposal"].items()
                if prior and prior.get(key) != value
            ]
        resolution = (
            read_snapshot(
                session,
                p.resolution_artifact_id,
                p.workspace_id,
                "portfolio-fusion-resolution/v1",
            )
            if p.resolution_artifact_id
            else None
        )
        participants = [
            {"role": r.role, "idea_id": r.idea_id, "venture_id": r.venture_id}
            for r in session.scalars(
                select(ProposalParticipant).where(
                    ProposalParticipant.proposal_id == p.id
                )
            )
        ]
        current_activity = (
            cls._activity_context(session, resolution["result"])
            if resolution and resolution["result"]
            else None
        )
        initial_activity = (
            resolution["result"].get("initial_activity_context", {})
            if current_activity and resolution
            else {}
        )
        activity_changes = [
            {"field": key, "previous": initial_activity.get(key), "current": value}
            for key, value in (current_activity or {}).items()
            if initial_activity.get(key) != value
        ]
        from startup_foundry.workspace_records import work_reference

        treatments = {t["work_id"]: t for t in content["proposal"]["work_treatments"]}
        work_options = [
            {
                **w,
                "url": (work_reference(session, w["workspace_id"], w["id"]) or {})[
                    "url"
                ],
                "treatment": treatments.get(w["id"], {}).get("treatment", "retain"),
                "reason": treatments.get(w["id"], {}).get(
                    "reason", "Retain existing work"
                ),
            }
            for w in content["source_state"]["work"]
            if w["status"] in {"todo", "ready", "blocked", "in_progress"}
            or w["id"] in treatments
        ]
        stale_reason = proposal_staleness(session, p)
        return {
            "work_options": work_options,
            "id": p.id,
            "version": p.version_id,
            "revision_id": p.revision_artifact_id,
            "state": p.state,
            "stale_reason": stale_reason,
            "display_state": "stale_needs_resolution" if stale_reason else p.state,
            "content": content,
            "name": content["proposal"]["name"],
            "revisions": revisions,
            "resolution": resolution,
            "participants": participants,
            "activity_digest": digest(current_activity) if current_activity else None,
            "activity_changes": activity_changes,
        }

    def show(self, identity: str) -> JSON:
        with self.factory() as session:
            return self._json(session, self._get(session, identity))

    def list(
        self, *, workspace_id: str | None = None, state: str | None = None
    ) -> JSON:
        with self.factory() as session:
            statement = select(PortfolioProposal)
            if workspace_id:
                idea = session.scalar(
                    select(Idea.id).where(Idea.workspace_id == workspace_id)
                )
                venture = session.scalar(
                    select(Venture.id).where(Venture.workspace_id == workspace_id)
                )
                if not idea and not venture:
                    return {"items": []}
                statement = (
                    statement.join(ProposalParticipant)
                    .where(
                        (ProposalParticipant.idea_id == idea)
                        if idea
                        else (ProposalParticipant.venture_id == venture)
                    )
                    .distinct()
                )
            if state:
                statement = statement.where(PortfolioProposal.state == state)
            rows = session.scalars(
                statement.order_by(PortfolioProposal.created_at.desc()).limit(100)
            )
            return {
                "items": [
                    {
                        "id": p.id,
                        "version": p.version_id,
                        "state": p.state,
                        "name": self._content(session, p)["proposal"]["name"],
                        "stale_reason": stale,
                        "display_state": "stale_needs_resolution"
                        if stale
                        else p.state,
                    }
                    for p in rows
                    for stale in [proposal_staleness(session, p)]
                ]
            }
