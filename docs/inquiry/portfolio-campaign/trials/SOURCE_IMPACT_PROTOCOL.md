# T6 — source revisions and affected decisions using ordinary files

Frozen before execution, 2026-10-02. Internal Foundry inquiry X-001, not a
customer validation or benchmark of a semantic-memory product.

Hypothesis: existing source IDs and idea→source links suffice to identify which
first-pass dispositions need review when a cited capability changes. A new
semantic impact service is unnecessary for this bounded job.

Use the campaign's real dependency links and **synthetic** revisions of its
`mlflow` and `change` source records. No live vendor claim is changed. Controls:

- Same semantic claim with a changed retrieval/footer field: no review queue.
- Changed claim: queue exactly the linked idea IDs, preserving the original
  claim, dispositions and both revision IDs. Queue means review, not refutation.
- Unknown source ID: report unmapped evidence; never guess its consumers.
- A contradictory later claim: retain both revisions and flag review; no
  automatic decision replacement.

Budget: one local script using JSON and SHA-256; no network, model or database
mutation. Write results to a new directory and refuse to overwrite it. Report
queue sizes and source fan-out. Success applies only to exact recorded links:
unrecorded dependencies, changed meaning detection and claim-level relevance
within a broad source still require editorial work. Do not infer human time or
token savings without a measured baseline.
