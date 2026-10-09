"""Bounded public contracts shared by local agent and human decision workflows."""

from __future__ import annotations

from typing import Annotated, Literal, Self
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, model_validator

from startup_foundry.domain import (
    AssessmentOutcome,
    ConfidenceLevel,
    EvidenceKind,
    WorkItemKind,
)

Identity = Annotated[str, Field(min_length=1, max_length=36)]
ShortText = Annotated[str, Field(min_length=1, max_length=300)]
Reason = Annotated[str, Field(min_length=1, max_length=10000)]
Actor = Annotated[str, Field(min_length=1, max_length=200)]
RequestKey = Annotated[str, Field(min_length=1, max_length=160)]
RecordKind = Literal[
    "work",
    "assumption",
    "assessment",
    "evidence",
    "decision",
    "experiment",
    "artifact",
    "review",
]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RecordRef(Contract):
    kind: RecordKind
    id: Identity


class MapNode(Contract):
    id: Annotated[str, Field(pattern=r"^[a-zA-Z0-9_-]{1,64}$")]
    kind: Literal["goal", "question", "alternative", "record"]
    title: ShortText
    detail: str = Field(default="", max_length=10000)
    ref: RecordRef | None = None

    @model_validator(mode="after")
    def reference_kind(self) -> Self:
        if (self.kind == "record") != (self.ref is not None):
            raise ValueError("Only record nodes have a required exact reference")
        return self


class MapEdge(Contract):
    model_config = ConfigDict(
        json_schema_extra={
            "allOf": [
                {
                    "if": {
                        "properties": {"kind": {"const": "may_lead_to"}},
                        "required": ["kind"],
                    },
                    "then": {
                        "required": ["condition", "outcome"],
                        "properties": {
                            "condition": {"type": "string", "pattern": r"\S"},
                            "outcome": {"type": "string"},
                        },
                    },
                }
            ],
            "examples": [
                {
                    "source": "trial",
                    "target": "pilot",
                    "kind": "may_lead_to",
                    "condition": "The bounded trial supports useful repeat use",
                    "outcome": "supported",
                }
            ],
        }
    )
    source: str = Field(min_length=1, max_length=64)
    target: str = Field(min_length=1, max_length=64)
    kind: Literal[
        "contributes_to",
        "tests",
        "may_lead_to",
        "revisits",
        "depends_on",
        "informs",
        "supports",
        "contradicts",
    ]
    condition: str = Field(
        default="",
        max_length=2000,
        description="For may_lead_to, supply a nonblank condition and an outcome.",
    )
    outcome: (
        Literal[
            "supported", "weakened", "refuted", "inconclusive", "blocked", "conflicting"
        ]
        | None
    ) = None

    @model_validator(mode="after")
    def branch_condition(self) -> Self:
        if self.kind == "may_lead_to" and (not self.condition or not self.outcome):
            raise ValueError("A possible branch needs a written condition and outcome")
        return self


class DecisionMapDraft(Contract):
    nodes: list[MapNode] = Field(default_factory=list, max_length=80)
    edges: list[MapEdge] = Field(default_factory=list, max_length=160)
    focus: list[str] = Field(default_factory=list, max_length=10)

    @model_validator(mode="after")
    def graph_rules(self) -> Self:
        ids = {n.id for n in self.nodes}
        if len(ids) != len(self.nodes):
            raise ValueError("Map node IDs must be unique")
        if len(set(self.focus)) != len(self.focus) or set(self.focus) - ids:
            raise ValueError("Focus must identify distinct existing nodes")
        seen: set[tuple[str, str, str]] = set()
        adjacency: dict[str, list[str]] = {identity: [] for identity in ids}
        for edge in self.edges:
            if edge.source not in ids or edge.target not in ids:
                raise ValueError("Map edge has a missing endpoint")
            key = (edge.source, edge.target, edge.kind)
            if key in seen:
                raise ValueError("Duplicate map relationship")
            seen.add(key)
            if edge.kind == "depends_on":
                adjacency[edge.source].append(edge.target)
        active: set[str] = set()
        complete: set[str] = set()

        def visit(node: str) -> None:
            if node in active:
                raise ValueError("Execution prerequisite cycle")
            if node in complete:
                return
            active.add(node)
            for child in adjacency[node]:
                visit(child)
            active.remove(node)
            complete.add(node)

        for node in sorted(ids):
            visit(node)
        return self


class WorkTreatment(Contract):
    work_id: Identity
    expected_version: int = Field(ge=1)
    action: Literal["keep", "pause", "cancel", "revise"]
    rationale: Reason
    title: ShortText | None = None
    description: str | None = Field(default=None, max_length=10000)

    @model_validator(mode="after")
    def revised_fields(self) -> Self:
        if self.action == "revise" and not (self.title or self.description):
            raise ValueError("A work revision must specify its change")
        if self.action != "revise" and (self.title or self.description):
            raise ValueError("Only a revision changes work content")
        return self


class MapInput(Contract):
    expected_head: Identity | None
    request_key: RequestKey
    actor: Actor
    rationale: Reason
    map: DecisionMapDraft
    work_treatments: list[WorkTreatment] = Field(default_factory=list, max_length=80)


class ContextInput(Contract):
    work_id: Identity
    expected_work_version: int = Field(ge=1)
    expected_head: Identity
    request_key: RequestKey
    actor: Actor
    budget_bytes: int = Field(default=24000, ge=512, le=100000)
    evidence_ids: list[Identity] = Field(default_factory=list, max_length=100)


class Finding(Contract):
    summary: Reason
    details: str = Field(default="", max_length=10000)
    sources: list[Annotated[str, Field(min_length=1, max_length=2000)]] = Field(
        default_factory=list, max_length=20
    )
    refs: list[RecordRef] = Field(default_factory=list, max_length=30)
    kind: EvidenceKind = EvidenceKind.OBSERVATION
    confidence: ConfidenceLevel = ConfidenceLevel.LOW
    epistemic_status: Literal["observation", "inference", "unknown"] = "observation"

    @model_validator(mode="after")
    def attributed(self) -> Self:
        if (
            not self.sources
            and not self.refs
            and self.epistemic_status == "observation"
        ):
            raise ValueError(
                "An observation requires a source; otherwise label inference or unknown"
            )
        for source in self.sources:
            parsed = urlsplit(source)
            if parsed.scheme not in {"http", "https", "observation", "document"}:
                raise ValueError("Source must be http(s), observation: or document:")
            if parsed.scheme in {"http", "https"} and (
                not parsed.netloc or parsed.username or parsed.password
            ):
                raise ValueError(
                    "Source URLs require a host and cannot contain credentials"
                )
        return self


class NextWork(Contract):
    title: ShortText
    description: Reason
    acceptance_criteria: Reason
    owner: Actor = "agent"
    kind: WorkItemKind = WorkItemKind.INVESTIGATION
    status: Literal["todo", "ready", "blocked"] = "ready"
    blocked_reason: str | None = Field(default=None, min_length=1, max_length=1000)

    @model_validator(mode="after")
    def block_reason(self) -> Self:
        if (self.status == "blocked") != bool(self.blocked_reason):
            raise ValueError("Blocked work requires a reason; other work has none")
        if self.owner in {"you", "human"} and self.status != "blocked":
            raise ValueError("Human input work must remain blocked until reviewed")
        return self


class AssessmentProposal(Contract):
    assumption_id: Identity
    outcome: AssessmentOutcome
    confidence: ConfidenceLevel
    rationale: Reason
    evidence_ids: list[Identity] = Field(default_factory=list, max_length=30)
    finding_indexes: list[Annotated[int, Field(ge=0, lt=30)]] = Field(
        default_factory=list, max_length=30
    )


class ResultInput(Contract):
    context_id: Identity
    request_key: RequestKey
    actor: Actor
    summary: Reason
    rationale: Reason
    limits: Reason
    outcome: Literal[
        "continue", "narrow", "hold", "stop", "inconclusive", "conflicting", "no_change"
    ]
    decision_scope: Literal["work", "venture"] = "work"
    next_action: Reason
    revisit_trigger: Reason | None = None
    narrowed_objective: Reason | None = None
    findings: list[Finding] = Field(default_factory=list, max_length=30)
    assessments: list[AssessmentProposal] = Field(default_factory=list, max_length=30)
    complete_work: bool = True
    next_work: NextWork | None = None
    work_treatments: list[WorkTreatment] = Field(default_factory=list, max_length=80)
    map: DecisionMapDraft | None = None
    chosen_branch: str | None = Field(default=None, max_length=64)
    supersedes_result_id: Identity | None = None
    reconciliation_rationale: Reason | None = None
    model: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def consistent_effects(self) -> Self:
        if self.outcome == "hold" and not self.revisit_trigger:
            raise ValueError("Hold requires a revisit trigger")
        if self.outcome in {"hold", "stop"} and self.next_work:
            raise ValueError("Hold/stop cannot queue continuation in the same result")
        if (
            self.outcome == "narrow"
            and self.decision_scope == "venture"
            and not self.narrowed_objective
        ):
            raise ValueError("Narrowing a venture requires its explicit new objective")
        if self.narrowed_objective and (
            self.outcome != "narrow" or self.decision_scope != "venture"
        ):
            raise ValueError("Only an explicit venture narrowing changes its objective")
        if bool(self.supersedes_result_id) != bool(self.reconciliation_rationale):
            raise ValueError("Reconciliation needs the prior result and rationale")
        return self


class ResolveResultInput(Contract):
    expected_result_digest: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
    expected_head: Identity
    expected_work_version: int = Field(ge=1)
    expected_review_revision: int = Field(ge=0)
    resolution: Literal["accept", "reject", "defer"]
    actor: Actor
    rationale: Reason
    coverage_action: Literal["reviewed", "accept_limitation"] | None = None
    coverage_rationale: Reason | None = None


class CaptureInput(Finding):
    """An explicitly attributed new observation; does not accept any decision."""

    request_key: RequestKey
    actor: Actor


class WorkClaimInput(Contract):
    expected_version: int = Field(ge=1)
    actor: Actor


class WorkReleaseInput(WorkClaimInput):
    rationale: Reason


class WorkCloseInput(Contract):
    """Cancel one exact active work item with an audited rationale (ADR-0020)."""

    work_id: Identity
    expected_version: int = Field(ge=1)
    actor: Actor
    rationale: Reason


class NewWorkInput(Contract):
    request_key: RequestKey
    actor: Actor
    rationale: Reason
    expected_head: Identity | None
    work: NextWork
