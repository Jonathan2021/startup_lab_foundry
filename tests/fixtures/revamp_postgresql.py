from pathlib import Path

from startup_foundry.application import FoundryApplication
from startup_foundry.config import load_settings
from startup_foundry.domain import Venture, VentureStage, WorkItem, WorkItemStatus
from startup_foundry.errors import ConflictError, ReferenceError, ValidationError
from startup_foundry.human_inputs import (
    ClaimInput,
    DependencyInput,
    HumanInputService,
    RequestInput,
    ResponseInput,
    ReviewResult,
    TargetChange,
)
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.proposals import FusionInput, ProposalService, ResolveInput
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.scoring import FACTORS, AssessmentInput, ScoringService
from startup_foundry.venture_scoring import (
    VentureAssessmentInput,
    VentureScoringService,
)
from startup_foundry.workspace_modules import ConfigInput, WorkspaceModuleService

f = create_session_factory(create_db_engine(load_settings().database_url))
p = PortfolioService(f)
FoundryApplication(f).create_venture(
    venture_id="v-foundry",
    name="Foundry",
    objective="Disposable",
    stage=VentureStage.DISCOVERY,
)
for i in ["pg-idea-a", "pg-idea-b"]:
    p.create_idea(IdeaDraft(title=i, description="Disposable fixture"), idea_id=i)
    p.promote_idea(i, venture_id="v-" + i)
    ScoringService(f).assess(
        AssessmentInput(
            idea_id=i,
            scores={k: 5 for k, *_ in FACTORS},
            rationale="Fixture",
            author="tester",
        )
    )
s = VentureScoringService(f)
assert s.bootstrap()["imported"] == 2
s.assess(
    VentureAssessmentInput(
        venture_id="v-pg-idea-a",
        expected_sequence=1,
        request_key="partial",
        scores={"problem": 3},
        rationale="Partial fixture",
        author="tester",
    )
)
assert s.show("v-pg-idea-a")["current"]["total"] is None
w = p.show_idea("pg-idea-a")["workspace_id"]
inputs = HumanInputService(f, Path("/tmp"))
inputs.register(
    RequestInput(
        id="R900",
        workspace_id=w,
        target_workspace_ids=[w],
        title="Feedback",
        question="Fixture?",
    )
)
response = inputs.submit(
    "R900",
    ResponseInput(
        expected_version=1, text="Defer", author="tester", submission_key="once"
    ),
)
c = inputs.claim(
    "R900", ClaimInput(expected_version=response["version"], actor="agent")
)
inputs.complete(
    "R900",
    ReviewResult(
        work_id=c["work_id"],
        response_id=c["response_id"],
        actor="agent",
        interpretation="User hold",
        outcome="deferred",
        rationale="Fixture",
    ),
)
assert inputs.show("R900")["status"] == "deferred"
WorkspaceModuleService(f).configure(
    "v-pg-idea-a",
    ConfigInput(expected_revision=0, actor="tester", modules=["software"]),
)
for request_id in ["R901", "R902"]:
    inputs.register(
        RequestInput(
            id=request_id,
            workspace_id=w,
            target_workspace_ids=[w],
            title=request_id,
            question="Exact input?",
        )
    )
with f.begin() as session:
    dependency = WorkItem(
        workspace_id=w,
        title="R902 dependency",
        kind="investigation",
        status=WorkItemStatus.BLOCKED,
        blocked_reason="human_input",
    )
    session.add(dependency)
    session.flush()
    dependency_id = dependency.id
inputs.link_dependency(
    "R902",
    DependencyInput(
        expected_version=inputs.show("R902")["version"],
        workspace_id=w,
        work_id=dependency_id,
        actor="operator",
        reason="R902 only",
    ),
)
response = inputs.submit(
    "R901",
    ResponseInput(
        expected_version=inputs.show("R901")["version"],
        text="R901 answer",
        author="operator",
        submission_key="one",
    ),
)
claim = inputs.claim(
    "R901", ClaimInput(expected_version=response["version"], actor="agent")
)
review = ReviewResult(
    work_id=claim["work_id"],
    response_id=claim["response_id"],
    actor="agent",
    interpretation="R901 only",
    outcome="sufficient",
    rationale="Fixture",
    changes=[
        TargetChange(
            workspace_id=w,
            expected_revision=0,
            next_action="Next",
            close_input_work_ids=[dependency_id],
        )
    ],
)
try:
    inputs.complete("R901", review)
    raise AssertionError("Cross-request closure accepted")
except ReferenceError:
    pass
try:
    inputs.complete("R901", review.model_copy(update={"outcome": "no_change"}))
    raise AssertionError("No-change mutations accepted")
except ValidationError:
    pass
assert (
    inputs.complete(
        "R901", review.model_copy(update={"outcome": "no_change", "changes": []})
    )["effects"]
    == []
)
with f() as session:
    assert session.get(WorkItem, dependency_id).status == WorkItemStatus.BLOCKED
proposals = ProposalService(f)
draft = FusionInput(
    name="PG composite",
    description="Fixture",
    source_idea_ids=["pg-idea-a", "pg-idea-b"],
    source_venture_ids=["v-pg-idea-a", "v-pg-idea-b"],
    result_venture_id="v-pg-composite",
    request_key="pg-fusion",
    rationale="Fixture",
    scope=[
        {
            "capability": "One trial",
            "treatment": "combined",
            "provenance": "Fixture",
            "reason": "Shared context",
        }
    ],
    alternatives=["Keep separate"],
)
x = proposals.create(draft)
assert (
    proposals.create(draft.model_copy(update={"request_key": "pg-other-key"}))["id"]
    == x["id"]
)
r = proposals.resolve(
    x["id"],
    ResolveInput(
        expected_version=x["version"],
        revision_id=x["revision_id"],
        action="accept",
        rationale="Disposable fixture",
        actor="operator",
        actor_kind="user",
        request_key="accept",
    ),
)
assert r["state"] == "applied"
with f.begin() as session:
    session.get(Venture, "v-pg-composite").objective = "Changed result scope"
reverse = ResolveInput(
    expected_version=r["version"],
    revision_id=x["revision_id"],
    action="reverse",
    rationale="Fixture reversal",
    actor="operator",
    actor_kind="user",
    request_key="reverse",
)
try:
    proposals.resolve(x["id"], reverse)
    raise AssertionError("Scope changed without reversal treatment")
except ConflictError:
    pass
assert (
    proposals.resolve(
        x["id"],
        reverse.model_copy(
            update={
                "activity_digest": proposals.show(x["id"])["activity_digest"],
                "downstream_treatment": "Preserve changed scope; hold composite",
            }
        ),
    )["state"]
    == "reversed"
)
print("revamp-postgresql-pass")
