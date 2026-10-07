from pathlib import Path
from startup_foundry.application import FoundryApplication
from startup_foundry.config import load_settings
from startup_foundry.domain import ArtifactKind, AssumptionKind, AssessmentOutcome, ConfidenceLevel, DecisionKind, EvidenceKind
from startup_foundry.repository import create_db_engine, create_session_factory
engine=create_db_engine(load_settings().database_url)
a=FoundryApplication(create_session_factory(engine))
report=Path('/home/jonathan/startup_lab/foundry/docs/inquiry/local-console-2026-10-02/REPORT.md')
a.add_assumption(assumption_id='console-local-operation-a',venture_id='v-foundry',statement='A permanent store, list operations and a local console can retain and operate the existing portfolio across process restarts.',kind=AssumptionKind.FEASIBILITY,importance=4,uncertainty=4)
a.add_evidence(evidence_id='console-local-operation-e',venture_id='v-foundry',origin_work_item_id=None,kind=EvidenceKind.EXPERIMENT_RESULT,confidence=ConfidenceLevel.HIGH,summary='250 ideas, five venture workspaces and 99 sources retained. Real browser browse/readiness and disposable create/derive/promote/blocked-agent workflows passed. Original databases unchanged. Technical support only; no measured commercial demand or token/time savings. Evidence: '+str(report.parent))
a.assess_assumption(assessment_id='console-local-operation-assessment',assumption_id='console-local-operation-a',evidence_ids=['console-local-operation-e'],outcome=AssessmentOutcome.SUPPORTED,confidence=ConfidenceLevel.HIGH,rationale='The bounded local operation criteria were observed. PostgreSQL deployment remains unverified this round; no Hindsight or commercial utility inference.')
a.add_decision(decision_id='console-local-operation-decision',venture_id='v-foundry',kind=DecisionKind.CONTINUE,summary='Use the permanent local console for ongoing venture investigations.',rationale='Observed inspection and path-reconstruction friction justified local product operation. Continue only evidence-driven capabilities; defer model training and remote deployment.',assessment_ids=['console-local-operation-assessment'])
a.add_artifact(artifact_id='console-local-operation-report',venture_id='v-foundry',work_item_id=None,kind=ArtifactKind.REPORT,name='Local console and venture continuation report',location=report.as_uri())
engine.dispose()
