# Workspace revamp verification protocol

2026-10-05. Agent-owned product work under ADR-0010; no learning credit.
Hypothesis: explicit answer receipts/review ownership, independent venture scores,
and exact-revision fusion effects resolve the documented R006/P103 management
friction while retaining original evidence and holds.

Before implementation: root HEAD e6a83e470d052439e5c8d4a943428f5bbd132f7f;
Foundry HEAD 3b082507062838df4009d4b636c4f320436f3b41, both dirty. Effective
source/input hashes, row IDs/counts, Alembic head and dirty status are in ignored
`.local/revamp-2026-10-05/baseline.json`. Online backup `pre-revamp.db` passed
quick_check before migrations. The new input/scoring/proposal/module tests were
written before their implementations and failed collection (missing services).

Bounded criteria: deterministic duplicate/conflict/ownership/rollback tests;
SQLite migration parity, integrity and FK checks on rehearsal; repeat-zero
bootstrap; frozen original idea definitions/scores/drafts and legacy receipt IDs;
new replies reviewed with only specific input dependencies closed; R008/R009
quiet holds; real sports proposal pending. No venture-product algorithms, agents,
providers, external contacts or new learning slice. Full required regression,
lint/type/workflow checks and desktop/mobile console acceptance after integration.
Browser unavailability remains an explicit gap, never an HTTP-only visual pass.
