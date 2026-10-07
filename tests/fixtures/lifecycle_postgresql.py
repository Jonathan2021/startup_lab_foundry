"""Production-image lifecycle race/coverage check on disposable PostgreSQL."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

from sqlalchemy import func, select

from startup_foundry.agent_handoffs import AgentHandoffService
from startup_foundry.application import FoundryApplication
from startup_foundry.config import load_settings
from startup_foundry.decision_contracts import (
    ContextInput,
    MapInput,
    NewWorkInput,
    ResolveResultInput,
    ResultInput,
)
from startup_foundry.decision_maps import DecisionMapService
from startup_foundry.domain import Decision, VentureStage, WorkItem
from startup_foundry.errors import ConflictError
from startup_foundry.repository import create_db_engine, create_session_factory

factory = create_session_factory(create_db_engine(load_settings().database_url))
venture = FoundryApplication(factory).create_venture(
    venture_id=str(uuid4()),
    name="Synthetic lifecycle PostgreSQL",
    objective="Maintain an operating service",
    stage=VentureStage.OPERATING,
)
ws = str(venture["workspace_id"])
handoffs, maps = AgentHandoffService(factory), DecisionMapService(factory)
work = handoffs.create_work(
    ws,
    NewWorkInput.model_validate(
        {
            "expected_head": None,
            "request_key": "task",
            "actor": "fixture",
            "rationale": "A release needs review",
            "work": {
                "title": "Check the release",
                "description": "Check account boundaries",
                "acceptance_criteria": "Retain the release and result",
                "owner": "agent",
            },
        }
    ),
)
head = maps.revise(
    ws,
    MapInput.model_validate(
        {
            "expected_head": None,
            "request_key": "map",
            "actor": "fixture",
            "rationale": "Connect purpose and work",
            "map": maps.starter(ws),
        }
    ),
)
ctx = handoffs.prepare(
    ws,
    ContextInput(
        work_id=work["id"],
        expected_work_version=work["work"]["version_id"],
        expected_head=head["id"],
        request_key="context",
        actor="fixture",
    ),
)
results = [
    handoffs.submit(
        ws,
        ResultInput(
            context_id=ctx["id"],
            request_key=key,
            actor="fixture",
            summary="Hold this release",
            rationale="The synthetic boundary check failed",
            limits="Staging only",
            outcome="hold",
            revisit_trigger="Passing independent check",
            next_action="Hold the affected release",
        ),
    )
    for key in ["a", "b"]
]
barrier = Barrier(2)


def accept(result):
    choice = ResolveResultInput(
        expected_result_digest=result["digest"],
        expected_head=ctx["map_revision_id"],
        expected_work_version=ctx["work"]["version_id"],
        expected_review_revision=ctx["review_revision"],
        resolution="accept",
        actor="operator",
        rationale="Reviewed exact result",
    )
    barrier.wait(timeout=10)
    try:
        receipt = handoffs.resolve(result["id"], choice)
        assert handoffs.resolve(result["id"], choice) == receipt
        return "accepted"
    except ConflictError:
        return "conflict"


with ThreadPoolExecutor(max_workers=2) as pool:
    assert sorted(pool.map(accept, results)) == ["accepted", "conflict"]
with factory() as session:
    assert (
        session.scalar(
            select(func.count())
            .select_from(Decision)
            .where(Decision.workspace_id == ws)
        )
        == 1
    )
    assert session.get(WorkItem, work["id"]).status.value == "done"
assert not maps.show(ws)["stale_references"]
assert handoffs.resume(ws)["current_review"]["product_maturity"] == "operating"
print("lifecycle-postgresql-pass")
