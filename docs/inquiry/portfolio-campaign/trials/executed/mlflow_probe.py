"""Bounded incumbent API probe; synthetic data, no model/provider calls."""
from __future__ import annotations

import json
import os
from pathlib import Path

os.environ['MLFLOW_DISABLE_TELEMETRY'] = 'true'
os.environ['MLFLOW_DISABLE_AGENT_HINT'] = 'true'
os.environ['MLFLOW_ENABLE_ASYNC_TRACE_LOGGING'] = 'false'

import mlflow
from mlflow.entities import AssessmentSource, AssessmentSourceType
from mlflow.genai.datasets import create_dataset
from mlflow.genai.scorers import scorer

ROOT = Path(__file__).resolve().parents[4]
STATE = ROOT / '.local/portfolio-campaign/mlflow-state'
STATE.mkdir(parents=True, exist_ok=True)
mlflow.set_tracking_uri('sqlite:///' + str(STATE / 'tracking.db'))
experiment_name = 'portfolio-incumbent-probe'
existing = mlflow.get_experiment_by_name(experiment_name)
if existing is None:
    mlflow.create_experiment(experiment_name, artifact_location=(STATE / 'artifacts').as_uri())
experiment = mlflow.set_experiment(experiment_name)

@mlflow.trace
def add_broken(a: int, b: int) -> int:
    return a + b + 1

@mlflow.trace
def add_fixed(a: int, b: int) -> int:
    return a + b

@scorer
def exact_answer(outputs, expectations) -> bool:
    return outputs == expectations['expected_answer']

assert add_broken(2, 3) == 6
trace_id = mlflow.get_last_active_trace_id()
assert trace_id
feedback = mlflow.log_feedback(
    trace_id=trace_id, name='review_accepts', value=False,
    source=AssessmentSource(source_type=AssessmentSourceType.HUMAN, source_id='synthetic-reviewer'),
    rationale='Synthetic fixture: expected five, got six; not an actual customer review.',
)
mlflow.log_expectation(trace_id=trace_id, name='expected_answer', value=5)
dataset = create_dataset(name='portfolio-regression-cases', experiment_id=experiment.experiment_id)
dataset.merge_records([{
    'inputs': {'a': 2, 'b': 3},
    'expectations': {'expected_answer': 5},
    'source': {'source_type': 'TRACE', 'source_data': {'trace_id': trace_id}},
}])
trace = mlflow.get_trace(trace_id)
assert trace is not None
assert any(a.name == 'review_accepts' and a.feedback.value is False for a in trace.info.assessments)
assert any(a.name == 'expected_answer' for a in trace.info.assessments)
results = {}
for name, fn in [('broken', add_broken), ('fixed', add_fixed)]:
    evaluation = mlflow.genai.evaluate(data=dataset, predict_fn=fn, scorers=[exact_answer])
    results[name] = {'run_id': evaluation.run_id, 'metrics': evaluation.metrics}
assert results['broken']['metrics']['exact_answer/mean'] == 0.0
assert results['fixed']['metrics']['exact_answer/mean'] == 1.0
output = {
    'id': 'T1', 'version': mlflow.__version__, 'status': 'passed',
    'scope': 'local synthetic trace-feedback-expectation-dataset-code-scorer API mechanics',
    'trace_id': trace_id, 'assessment_id': feedback.assessment_id,
    'dataset_id': dataset.dataset_id, 'results': results,
    'limitations': ['No real human review', 'No LLM judge', 'No customer dataset', 'No review-queue UI or deployed CI job'],
}
Path(__file__).with_name('mlflow-result.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(output,indent=2))
