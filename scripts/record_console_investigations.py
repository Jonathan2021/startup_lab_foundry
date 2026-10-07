"""Record the bounded 2026-10-02 continuation; no network or model calls.

This is campaign bookkeeping, not a generic idea-generation engine. Protocols were
written before the comparisons; DB transcription happens after them. Stable IDs
make an interrupted invocation resumable without replacing historical records.
"""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select

from startup_foundry.application import FoundryApplication
from startup_foundry.config import load_settings
from startup_foundry.domain import (
    Artifact,
    ArtifactKind,
    AssessmentOutcome,
    Assumption,
    AssumptionAssessment,
    AssumptionKind,
    ConfidenceLevel,
    Decision,
    DecisionKind,
    Evidence,
    EvidenceKind,
    Experiment,
    ExperimentStatus,
    Idea,
    WorkItem,
    WorkItemKind,
    WorkItemStatus,
    utc_now,
)
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import (
    UnitOfWork,
    create_db_engine,
    create_session_factory,
)
from startup_foundry.steps import StepService

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/inquiry/local-console-2026-10-02"
DRAFTS = [
    dict(
        id="D001",
        title="GPX transfer preflight",
        description=(
            "Explain changed road sections versus changed ETA conventions when "
            "a touring rider transfers a shaped route between planners."
        ),
        customer="Touring riders moving a shaped multi-day ride between apps",
        parent_ids=["N008"],
        derivation_reason=(
            "Separate cross-app transfer diagnosis from scenic-route generation."
        ),
        validation_test=(
            "R001: compare a specified before/after GPX and app settings; stop "
            "a new utility if an existing converter/editor explains the "
            "material mismatch."
        ),
        disposition="input_hold",
        rationale=(
            "Conversion and visual inspection are already supplied by "
            "incumbents. The bounded gpx.studio trial was inconclusive; a "
            "diagnostic miss and user value are unproven."
        ),
        venture="v-route-repair",
        assumption=(
            "A new generic GPX comparison/conversion utility is justified by a "
            "demonstrated incumbent gap."
        ),
        outcome=AssessmentOutcome.WEAKENED,
        decision=DecisionKind.NARROW,
        business_model=(
            "Possible open-source diagnostic/integration; paid support is an "
            "untested hypothesis."
        ),
    ),
    dict(
        id="D002",
        title="Source-linked decision review queue",
        description=(
            "Connect a changed external capability claim to the decisions "
            "depending on it, retaining the original evidence and the review "
            "resolution."
        ),
        customer=(
            "Teams maintaining evidence-dependent decisions; Foundry is the "
            "current internal user"
        ),
        parent_ids=["G002", "P088", "P174"],
        derivation_reason=(
            "Combine monitoring and decision provenance while reusing incumbent"
            " capture/diff capabilities."
        ),
        validation_test=(
            "Keep internal. Reopen commercial validation only with a real "
            "external user who repeatedly needs claim-to-decision review and "
            "rejects an incumbent plus a small script."
        ),
        disposition="internal_only",
        rationale=(
            "Distill already documents history, diffs and empty-selection "
            "errors; prior exact-link fanout worked with ordinary files. "
            "External demand and a sufficient integration gap remain unproven."
        ),
        venture="v-g002",
        assumption=(
            "A new monitoring platform is needed for version history, diffs and"
            " empty-selection detection."
        ),
        outcome=AssessmentOutcome.REFUTED,
        decision=DecisionKind.NARROW,
        business_model="Internal integration first; paid team workflow is unvalidated.",
    ),
    dict(
        id="D003",
        title="Portable work-sample receipt",
        description=(
            "Carry a bounded exercise, rubric, evidence, evaluator and limits "
            "to another decision-maker through an existing credential standard."
        ),
        customer=(
            "An issuer and receiving hiring/training decision-maker willing to "
            "assess one real exercise"
        ),
        parent_ids=["N003", "G005", "P106"],
        derivation_reason=(
            "Rescope broad skill certification into evidence portability and "
            "institutional acceptance."
        ),
        validation_test=(
            "R003: an issuer and recipient review a permitted real work sample "
            "using Open Badges; stop a platform build without acceptance or a "
            "consequential changed decision."
        ),
        disposition="access_hold",
        rationale=(
            "Open Badges already carries criteria and evidence. The unresolved "
            "job is acceptance of an exercise, not a new signed credential "
            "format."
        ),
        venture="portfolio-campaign",
        assumption=(
            "A new credential format is required to carry issuer, criteria and "
            "achievement evidence."
        ),
        outcome=AssessmentOutcome.REFUTED,
        decision=DecisionKind.DEFER,
        business_model=(
            "Possible integration/issuing service; buyer access and payment untested."
        ),
    ),
]
SOURCES = [
    dict(
        title="RouteConverter capabilities",
        url="https://www.routeconverter.com/",
        claim=(
            "The official site describes conversion/editing and visible "
            "position lists in the current desktop editor."
        ),
        limits=(
            "Vendor documentation only. Not installed or runtime-tested; no ETA"
            " diagnosis validated."
        ),
        checked_on="2026-10-02",
        ideas=["D001", "N008"],
    ),
    dict(
        title="RouteConverter route and track workflow",
        url="https://www.routeconverter.com/help/getting-started/",
        claim=(
            "The official guide explains route/track editing, splitting/merging"
            " and reducing points."
        ),
        limits=(
            "Documentation only; does not establish handling of the reported "
            "Liberty Rider/68 ETA mismatch."
        ),
        checked_on="2026-10-02",
        ideas=["D001", "N008"],
    ),
    dict(
        title="gpx.studio bounded anonymous editor observation",
        url="https://gpx.studio/app",
        claim=(
            "Two visits loaded the editor with HTTP 200. The retry showed "
            "File/Open/Export controls."
        ),
        limits=(
            "Inconclusive harness trial: no fixture imported, pair compared, or"
            " geometry export verified. See GPX_COMPARISON_RESULT.md."
        ),
        checked_on="2026-10-02",
        ideas=["D001", "N008"],
    ),
    dict(
        title="Distill change history and highlighted changes",
        url="https://distill.io/docs/web-monitor/change-history-and-highlighted-changes/",
        claim=(
            "Distill documents retained versions and visual/text comparisons of"
            " changes."
        ),
        limits=(
            "Documentation only; a claim-to-decision review workflow and buyer "
            "demand were not tested."
        ),
        checked_on="2026-10-02",
        ideas=["D002", "G002", "P088", "P174"],
    ),
    dict(
        title="Distill empty-selection behavior",
        url="https://distill.io/docs/web-monitor/config-and-advanced-monitor-options/",
        claim=(
            "The documentation describes ignoreEmptyText and a SELECTION_EMPTY "
            "error when the selection is empty."
        ),
        limits=(
            "No runtime test; not a guarantee about all selector drift or "
            "semantic changes."
        ),
        checked_on="2026-10-02",
        ideas=["D002", "P088", "P174"],
    ),
    dict(
        title="Open Badges evidence and criteria",
        url="https://openbadges.org/about/faq",
        claim=(
            "The official FAQ describes issuer, criteria and evidence as badge "
            "information."
        ),
        limits="No issuer/recipient adoption or work-sample validation was tested.",
        checked_on="2026-10-02",
        ideas=["D003", "N003", "G005", "P106"],
    ),
    dict(
        title="Open Badges 3.0 specification",
        url="https://www.imsglobal.org/spec/ob/v3p0/",
        claim=(
            "The specification defines verifiable achievement credentials "
            "including evidence."
        ),
        limits=(
            "Format capability only; no credential verifier was run and "
            "institutional acceptance remains untested."
        ),
        checked_on="2026-10-02",
        ideas=["D003", "N003", "G005", "P106"],
    ),
]


def main():
    engine = create_db_engine(load_settings().database_url)
    factory = create_session_factory(engine)
    portfolio, app = PortfolioService(factory), FoundryApplication(factory)
    steps = StepService(factory, ROOT / "requests")

    def exists(model, identity):
        with UnitOfWork(factory) as unit:
            return unit.session.get(model, identity) is not None

    report = {
        "date": "2026-10-02",
        "bookkeeping": (
            "Recorded after comparisons; prior frozen Markdown protocols retained."
        ),
        "ideas": [],
        "sources": [],
    }
    try:
        for row in DRAFTS:
            if not exists(Idea, row["id"]):
                portfolio.create_idea(
                    IdeaDraft(
                        **{
                            key: row[key]
                            for key in [
                                "title",
                                "description",
                                "customer",
                                "parent_ids",
                                "derivation_reason",
                                "validation_test",
                                "business_model",
                            ]
                        }
                    ),
                    idea_id=row["id"],
                )
        for raw in SOURCES:
            claim = {k: v for k, v in raw.items() if k != "ideas"}
            recorded = portfolio.record_source(claim, idea_ids=raw["ideas"])
            report["sources"].append({"id": recorded["id"], **raw})
        for row in DRAFTS:
            prefix = "console-" + row["id"].lower()
            assumption_id, work_id, evidence_id, assessment_id, decision_id = [
                prefix + "-" + s for s in ["a", "w", "e", "assessment", "decision"]
            ]
            if not exists(Assumption, assumption_id):
                app.add_assumption(
                    assumption_id=assumption_id,
                    venture_id=row["venture"],
                    statement=row["assumption"],
                    kind=AssumptionKind.VIABILITY,
                    importance=4,
                    uncertainty=5,
                )
            if not exists(WorkItem, work_id):
                app.add_work_item(
                    work_item_id=work_id,
                    venture_id=row["venture"],
                    title="Bounded comparison: " + row["title"],
                    kind=WorkItemKind.EXPERIMENT,
                    decision_id=None,
                    acceptance_criteria=(
                        "Retain counterevidence, limits and a concrete next gate."
                    ),
                    method=(
                        "Transcribed after execution from frozen PLAN.md and "
                        "GPX_COMPARISON_PROTOCOL.md/retry. Up to three primary "
                        "comparators per narrowed job. No paid calls, accounts "
                        "or messages."
                    ),
                    success_criteria=(
                        "A configured incumbent satisfies the specific job, or "
                        "a reproducible residual gap is observed."
                    ),
                    failure_criteria=(
                        "Access/harness limits are inconclusive. Vendor claims "
                        "cannot establish commercial demand."
                    ),
                    assumption_ids=[assumption_id],
                )
            if not exists(Evidence, evidence_id):
                linked = [s["id"] for s in report["sources"] if row["id"] in s["ideas"]]
                app.add_evidence(
                    evidence_id=evidence_id,
                    venture_id=row["venture"],
                    origin_work_item_id=work_id,
                    kind=EvidenceKind.MARKET_RESEARCH,
                    confidence=ConfidenceLevel.MEDIUM,
                    summary=row["rationale"]
                    + " Sources: "
                    + ", ".join(linked)
                    + ". Details: "
                    + str(OUT / "DERIVED_IDEAS.md"),
                )
            if not exists(AssumptionAssessment, assessment_id):
                app.assess_assumption(
                    assessment_id=assessment_id,
                    assumption_id=assumption_id,
                    evidence_ids=[evidence_id],
                    outcome=row["outcome"],
                    confidence=ConfidenceLevel.MEDIUM,
                    rationale=row["rationale"],
                )
            if not exists(Decision, decision_id):
                app.add_decision(
                    decision_id=decision_id,
                    venture_id=row["venture"],
                    kind=row["decision"],
                    summary=row["id"] + ": " + row["disposition"],
                    rationale=row["rationale"]
                    + " Next gate: "
                    + row["validation_test"],
                    assessment_ids=[assessment_id],
                )
            app.set_work_item_status(work_id, WorkItemStatus.DONE)
            with UnitOfWork(factory) as unit:
                experiment = unit.session.scalar(
                    select(Experiment).where(Experiment.work_item_id == work_id)
                )
                if experiment.status != ExperimentStatus.COMPLETE:
                    experiment.status = ExperimentStatus.COMPLETE
                    experiment.result_summary = row["rationale"] + (
                        " Completed bookkeeping for a bounded comparison, "
                        "not a passed commercial gate. GPX runtime "
                        "comparison inconclusive; other comparisons "
                        "documentary."
                    )
                    experiment.completed_at = utc_now()

            idea = portfolio.show_idea(row["id"])
            with UnitOfWork(factory) as unit:
                artifact_id = prefix + "-disposition"
                if not unit.session.get(Artifact, artifact_id):
                    unit.session.add(
                        Artifact(
                            id=artifact_id,
                            workspace_id=idea["workspace_id"],
                            name="Investigation disposition",
                            kind=ArtifactKind.REPORT,
                            location=(OUT / "DERIVED_IDEAS.md").as_uri()
                            + "#"
                            + row["id"],
                            metadata_json={
                                "disposition": row["disposition"],
                                "rationale": row["rationale"],
                                "demand_evidence": (
                                    "No commercially qualified venture; no "
                                    "payment/adoption observed."
                                ),
                                "decision_id": decision_id,
                            },
                        )
                    )
            runs = [
                steps.start("idea", row["id"], kind, request_key=prefix + "-" + kind)[
                    "id"
                ]
                for kind in ["readiness", "research_brief"]
            ]
            report["ideas"].append(
                {
                    "id": row["id"],
                    "parents": row["parent_ids"],
                    "disposition": row["disposition"],
                    "venture": row["venture"],
                    "assumption_id": assumption_id,
                    "work_item_id": work_id,
                    "evidence_id": evidence_id,
                    "assessment_id": assessment_id,
                    "decision_id": decision_id,
                    "step_run_ids": runs,
                }
            )
        report["idea_count"] = portfolio.list_ideas(limit=1)["total"]
        report["source_count"] = portfolio.list_sources(limit=1)["total"]
        (OUT / "investigation-records.json").write_text(
            json.dumps(report, indent=2) + "\n"
        )
        print(json.dumps(report, indent=2))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
