"""T6: a disposable, explicit dependency-table comparison, not a service."""

import hashlib
import json
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT = Path(os.environ.get("FOUNDRY_TRIAL_OUTPUT", BASE / "trials/t6"))
OUT.mkdir(parents=True, exist_ok=False)
INPUT = Path(os.environ.get("FOUNDRY_TRIAL_INPUT", BASE / "revisions/r1"))
ideas = json.loads((INPUT / "ideas.json").read_text())
sources = json.loads((INPUT / "sources.json").read_text())
if isinstance(sources, dict):
    sources = sources["sources"]
by_id = {s["id"]: s for s in sources}


def consumers(source_id):
    return sorted(i["id"] for i in ideas if source_id in i["source_ids"])


def review(source_id, old_claim, new_claim):
    if source_id not in by_id:
        return {"status": "UNMAPPED", "review_ids": []}
    return {
        "status": "REVIEW_REQUIRED" if old_claim != new_claim else "UNCHANGED_CLAIM",
        "review_ids": consumers(source_id) if old_claim != new_claim else [],
    }


results = []
for source_id in ["mlflow", "change"]:
    source = by_id[source_id]
    claim = source["claim"]
    versions = [
        {"revision": "synthetic:r1", "claim": claim, "retrieval": "initial"},
        {"revision": "synthetic:r2", "claim": claim, "retrieval": "footer changed"},
        {"revision": "synthetic:r3", "claim": "SYNTHETIC CONTRADICTION: capability removed"},
    ]
    noise = review(source_id, versions[0]["claim"], versions[1]["claim"])
    changed = review(source_id, versions[0]["claim"], versions[2]["claim"])
    assert noise["review_ids"] == []
    assert changed["review_ids"] == consumers(source_id)
    assert changed["review_ids"]
    results.append({"source_id": source_id, "versions": versions,
                    "noise": noise, "contradiction": changed,
                    "decision_mutations": 0})
unknown = review("deliberately-unknown-control", "before", "after")
assert unknown["status"] == "UNMAPPED"
output = {
    "trial": "T6", "outcome": "PASSED_EXACT_DEPENDENCY_CONTROLS",
    "input_sha256": {f: hashlib.sha256((INPUT/f).read_bytes()).hexdigest()
                     for f in ["ideas.json", "sources.json"]},
    "cases": results, "unknown_control": unknown,
    "original_records_unchanged": True,
    "limits": ["changes supplied explicitly, not detected semantically",
               "source-level fan-out can overqueue individual claims",
               "unrecorded dependencies are invisible",
               "no measured time saving or external demand evidence"],
}
(OUT / "result.json").write_text(json.dumps(output, indent=2) + "\n")
print(json.dumps({"outcome": output["outcome"], "review_counts": {
    r["source_id"]: len(r["contradiction"]["review_ids"]) for r in results}}))
