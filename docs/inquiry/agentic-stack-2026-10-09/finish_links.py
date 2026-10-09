#!/usr/bin/env python3
"""Post-pass fixes: relink same-name conflicts by actor ID, flag primary competitors, export the comparison."""
from __future__ import annotations

import json
import re
import subprocess
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CLI = json.loads((REPO / ".foundry" / "project.json").read_text())["cli"]
ACTOR = "fable-agentic-stack-20261009"
rec = json.loads((HERE / "records.json").read_text())


def cli(*args: str, input_path: Path | None = None) -> dict:
    cmd = [*CLI, *args] + (["--input", str(input_path)] if input_path else [])
    done = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if done.returncode:
        raise SystemExit(f"CLI failed: {' '.join(args)}\n{done.stderr[-1200:]}")
    return json.loads(done.stdout)


# 1. Relink failures by actor_id (the conflict message carries the existing ID).
for key, message in list(rec.get("actor_failures", {}).items()):
    idea, name, relation = key.split(":", 2)
    match = re.search(r"already exists as ([0-9a-f-]{36})", message)
    if not match:
        print("cannot resolve", key); continue
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower())[:40]
    original = json.loads((HERE / "inputs" / f"actor-{idea}-{slug}-{relation}.json").read_text())
    payload = {k: v for k, v in original.items() if k != "actor"}
    payload["actor_id"] = match.group(1)
    payload["note"] = payload["note"] + " (Linked by actor ID: research passes disagreed on the website; first registration kept.)"
    path = HERE / "inputs" / f"actor-{idea}-{slug}-{relation}.byid.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    rec["actors"][key] = cli("idea", "link-actor", "--id", idea, input_path=path)
    del rec["actor_failures"][key]
    print("relinked", key)

# 2. Primary flags on AS10's main competitors/partner (re-sending a link updates it, audited).
primaries = {
    "Not Diamond Code": "competitor", "OmniRoute": "competitor", "CLIProxyAPI": "competitor",
    "Model Capacity plugin (TogetherWeOwn)": "competitor", "LiteLLM": "competitor",
    "Paperclip": "partner", "Tutti": "alternative", "OpenClaw": "alternative",
}
actors = {a["name"]: a for a in cli("market-actor", "list", "--limit", "500")["items"]}
for name, relation in primaries.items():
    candidates = [n for n in actors if n.lower().startswith(name.lower().split(" (")[0].lower())]
    if not candidates:
        print("no actor named", name); continue
    actor = actors[candidates[0]]
    existing = next((l for l in cli("idea", "show", "--id", "AS10")["competition"] if l["actor_id"] == actor["id"]), None)
    if existing is None:
        print("AS10 has no link to", candidates[0]); continue
    payload = {"actor_id": actor["id"], "relation": existing["relation"], "is_primary": True, "note": existing["note"],
               "checked_on": existing["checked_on"] or date.today().isoformat(), "source_ids": existing["source_ids"], "recorded_by": ACTOR}
    path = HERE / "inputs" / f"primary-AS10-{re.sub(r'[^a-z0-9]+','-',candidates[0].lower())[:40]}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    out = cli("idea", "link-actor", "--id", "AS10", input_path=path)
    print("primary", candidates[0], existing["relation"], "updated" if out.get("updated") else "unchanged")

# 3. Export the cohort comparison and the AS10 competition table for the report.
ids = ["AS10", "AS08", "AS01", "AS04", "AS02", "AS03", "AS09", "AS05", "AS06", "AS07"]
compare = cli("idea", "compare", "--ids", *ids)
(HERE / "compare.json").write_text(json.dumps(compare, indent=2, ensure_ascii=False))
as10 = cli("idea", "show", "--id", "AS10")
rec["as10_competition_count"] = len(as10["competition"])
(HERE / "records.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False, sort_keys=True))
print("compare items", len(compare["items"]), "| AS10 competition links", len(as10["competition"]), "| primaries", [l["name"] for l in as10["competition"] if l["is_primary"]])
for item in compare["items"]:
    print(f"  {item['id']}: total {item['total']} grade {item['grade']} competition {item['competition_count']} disposition {item['disposition']}")
