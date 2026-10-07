# Executable comparison protocols

Record FOUNDRY-CAMPAIGN-20261002-TRIALS:r1. Frozen before executing the probes.
Synthetic local inputs; agent operation; no learner credit or customer evidence.

## T1 — MLflow 3.16.1

Pin verified against PyPI metadata (published 2026-09-16). Isolated Python 3.13
environment, SQLite and local artifacts, telemetry disabled in the probe.
A deliberately wrong integer-addition function emits a trace; the agent records
synthetic human-source rejection and an expected answer. Create an evaluation
dataset, retain source trace provenance, evaluate bad and fixed versions with a
code scorer, and retrieve feedback. Assertions: trace/feedback/expectation persist;
dataset contains the case; bad score fails and fixed score passes; neither requires
an LLM. Failures and compatibility fixes remain in the attempt log. No real human
review or review-queue UI is simulated as completed. This tests API mechanics,
not judge accuracy, coverage of all EvalOps semantics, or user demand.

## T2 — changedetection.io 0.60.8

Pin verified against PyPI metadata (published 2026-09-28). Isolated environment.
First dependency resolution failed on a pinned prerelease; retry explicitly allows
prereleases and retains this setup friction. Exercise the installed upstream
HTML selection/text/ignore pipeline as a **component trial**, without a server or
notifications. Inputs: a local HTML document with a claim, a noisy timestamp and
an unrelated footer. Check: timestamp/footer-only change is ignored; claim change
is retained; absent selector produces empty output and must not be confused with
unchanged evidence. Save raw extracted strings and assertions. This does not test
scheduled crawling, browser rendering, authentication, notification delivery or
semantic legal/financial impact. Stop further setup if the 15-minute limit is hit.

## T3 — source reuse and Foundry recovery

Use canonical source IDs for multiple idea groups. Verify same IDs reuse the
same URL/claim revision; an intentionally stale source must signal revalidation,
and an unknown source must fail lookup. Existing `rg` is the baseline for exact
source recovery; no semantic retrieval benchmark or token-saving estimate.
Before any product change, record the current Foundry view for the separate T1
and T2 experiments. If both omit stored method/success/failure criteria (as the
previous inquiry also observed), add only faithful experiment reconstruction,
with a behavior test for two ventures and linked assumptions. Do not implement a
cache service, vector store, automated venture generator, or shared library.
