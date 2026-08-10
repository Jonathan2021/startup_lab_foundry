# Agentic Startup Foundry

## 1. Project in one sentence

The **Agentic Startup Foundry** is an operating system for turning raw startup ideas into evidence-backed ventures: it helps evaluate and narrow ideas, plan execution, coordinate agents and humans, retain venture knowledge, and progressively automate repeated startup-building workflows.

Its most important design principle is that it should be **built alongside real ventures**, not designed in isolation.

---

## 2. Why build it

Modern AI makes generating plans, code, copy, research and outreach increasingly cheap. The bottleneck is moving from:

> "Here is an idea"

to:

> "Here is a validated, operating business with users, evidence, decisions, infrastructure, contacts and a clear next action."

A founder still has to decide:

- which idea deserves time;
- what assumptions are unproven;
- what competitors already exist;
- how to narrow the first product;
- what to build first;
- when an agent can act autonomously;
- when human review is required;
- what was tried before and why it failed;
- how several ventures should share useful infrastructure.

The Foundry provides persistent state around that process.

---

## 3. Strategic role

The Foundry has two roles.

### Internal bootstrap system

Initially, it is primarily **your own tool for launching other projects**.

That changes how it should be built:

1. Select a promising child venture.
2. Use the Foundry to move it forward.
3. When execution hits a repeated wall, implement the smallest Foundry capability that solves it.
4. Use the capability in the real venture.
5. Generalize it only when another venture encounters substantially the same need.

This is preferable to building a complete autonomous-startup platform from speculation.

### Possible standalone product

Once several ventures have been launched through it, the internal operating system may itself become a commercial product.

At that point its value is not merely "AI generates startup advice." Its stronger assets can be:

- accumulated venture history;
- user-specific preferences and decision patterns;
- integrations;
- contacts and outreach history;
- approval policies;
- reusable workflows;
- APIs used by other agents;
- provider-agnostic AI configuration;
- evidence of what actually worked across multiple ventures.

---

## 4. Objectives

### Product objectives

The Foundry should eventually help a founder:

1. capture one idea or a large backlog of ideas;
2. structure and deduplicate them;
3. research competitors and market context;
4. score opportunities with explicit assumptions;
5. narrow broad ideas into testable wedges;
6. define hypotheses and validation experiments;
7. produce a roadmap and rough budget;
8. execute tasks through agents where appropriate;
9. request human intervention for consequential decisions;
10. track contacts, outreach, domains, experiments and product state;
11. remember why decisions were made;
12. reuse infrastructure and lessons across ventures.

### Strategic objectives

The Foundry should create moats that do not depend on having a uniquely capable AI model:

- **workflow lock-in through useful accumulated state;**
- **personalization from repeated user corrections and decisions;**
- **partnership and distribution channels;**
- **deep integrations into development and business workflows;**
- **an API that other AI systems can call;**
- **bring-your-own-model / bring-your-own-key support;**
- **cross-venture operational memory;**
- **reusable agent and workflow templates.**

---

## 5. Non-goals

The first versions should **not** attempt to:

- create arbitrary companies autonomously from one prompt;
- replace general agent frameworks;
- provide every possible CRM, project-management, coding and marketing feature;
- support dozens of AI providers from day one;
- automate irreversible actions without approval;
- build an elaborate microservice architecture before there is product demand;
- optimize generic startup scores before real validation evidence exists.

The Foundry should remain a **thin coordination and memory layer** until real venture work proves that more is needed.

---

## 6. Recommended MVP

The first MVP should be deliberately small.

### Core entities

- **Idea**
- **Venture**
- **Assumption**
- **Evidence**
- **Decision**
- **Task**
- **Agent run**
- **Human approval**
- **Artifact**

### Minimum workflows

#### A. Idea triage

For an idea:

- retain the original note;
- create a cleaned description;
- identify likely customers;
- identify competitors;
- score it;
- show uncertainty in the score;
- propose one narrower first market;
- define the next validation action.

#### B. Venture workspace

Once an idea is selected:

- convert it into a venture;
- define objective and current stage;
- maintain hypotheses;
- maintain roadmap and tasks;
- attach evidence and artifacts;
- record important decisions and rationales.

#### C. Agent execution

Support one or two real agent workflows, for example:

- competitor research;
- customer-interview preparation.

Each run should retain:

- inputs;
- provider/model;
- outputs;
- sources;
- cost;
- human edits;
- acceptance/rejection.

#### D. Approval queue

Anything externally consequential should be reviewable before execution, such as:

- sending an email;
- publishing content;
- purchasing a domain;
- spending money;
- deleting data.

### MVP success criterion

The MVP is successful when it meaningfully advances **one real child venture** and saves or improves work compared with using independent chats, notes and scripts.

It does not need external customers yet.

---

## 7. Recommended development practice

### 7.1 Develop the Foundry alongside ventures

This is the most important rule.

Do not spend weeks implementing "what a startup platform probably needs." Instead:

> Venture need → narrow Foundry feature → actual use → feedback → reuse → generalization.

Example:

A child venture needs to contact 20 physiotherapists.

Do **not** immediately build a generic CRM and campaign engine.

First implement:

- contact records;
- outreach draft;
- approval;
- sent/not-sent state;
- response status.

If a second venture needs the same workflow, then extract a reusable outreach module.

---

### 7.2 Treat friction as product research

When a venture becomes blocked, record the blockage:

- what task was attempted;
- what information was missing;
- whether an agent or human failed;
- workaround used;
- time lost;
- whether the problem has occurred before;
- whether other ventures would benefit from solving it.

This creates an evidence-backed Foundry backlog.

---

### 7.3 Prefer modular monolith over premature platform engineering

Start with:

- one repository;
- one application;
- PostgreSQL;
- object storage if required;
- a background worker;
- a clean domain model;
- documented interfaces between modules.

Extract services only when scaling, security or ownership actually demands it.

---

### 7.4 Keep AI providers replaceable

The Foundry should represent a task independently from a specific provider.

Prefer an internal interface such as:

```text
Task
 ├─ provider policy
 ├─ model policy
 ├─ tools
 ├─ structured output schema
 ├─ evaluation policy
 └─ approval policy
```

Users should eventually be able to:

- choose a provider;
- supply their own API key;
- define cost/quality preferences;
- use local or enterprise models;
- route different tasks to different models.

Provider choice is not itself a moat, but avoiding model lock-in makes the rest of the product more durable.

---

### 7.5 Make state more valuable than prompts

Prompts are easy to reproduce.

The Foundry should accumulate harder-to-replace assets:

- interviews;
- historical decisions;
- rejected ideas;
- experiment results;
- outreach outcomes;
- user preferences;
- product analytics;
- contact relationships;
- execution history;
- approval policies;
- reusable datasets;
- integrations.

A user should remain because the system contains useful operating history, not because exporting is artificially difficult.

---

### 7.6 Keep humans in consequential loops

Automation should increase gradually.

A useful progression is:

1. agent proposes;
2. human approves;
3. agent executes a narrowly bounded action;
4. system records outcome;
5. repeated successful actions receive broader delegated authority.

The system should support this explicitly rather than treating human review as an exception.

---

### 7.7 Add APIs early enough to preserve architectural discipline

The Foundry's own UI should not be the only client.

As useful capabilities mature, expose stable APIs for:

- idea evaluation;
- venture state;
- tasks;
- approvals;
- agent execution;
- artifacts;
- evidence retrieval.

Later, third-party agents can depend on these APIs. That dependency can become part of the moat.

---

## 8. Suggested first child venture

**Agent EvalOps** is a particularly useful first child venture because it improves the Foundry itself.

The Foundry creates agent runs and human corrections. Agent EvalOps turns them into:

- evaluation cases;
- regression suites;
- model/provider comparisons;
- release gates;
- operational feedback.

The result is a productive loop:

```text
Foundry runs agents
        ↓
Humans review outcomes
        ↓
Agent EvalOps learns from failures
        ↓
Agents improve
        ↓
Foundry becomes more capable
        ↓
More ventures can be executed
```

---

## 9. Development stages

### Stage 0 — Internal notebook replacement

Goal: stop losing startup reasoning across chats and documents.

Build:

- ideas;
- evidence;
- scoring;
- decisions;
- ventures;
- tasks.

### Stage 1 — One useful execution workflow

Goal: prove that persistent venture state improves agent work.

Add:

- competitor-research agent;
- artifact storage;
- human review;
- basic run history.

### Stage 2 — Human-controlled execution

Goal: move from advice to action.

Add:

- approval queue;
- email drafting/sending integration;
- contacts;
- domain and external-action records;
- cost tracking.

### Stage 3 — Reusable cross-venture capabilities

Only generalize features proven across several ventures.

Examples:

- outreach;
- customer interviews;
- landing-page experiments;
- evaluation;
- analytics;
- deployment;
- payments.

### Stage 4 — External design partners

Add only what real external users require:

- organizations;
- permissions;
- provider credentials;
- export;
- privacy boundaries;
- billing experiment.

### Stage 5 — Ecosystem

Possible later capabilities:

- plugin/connector system;
- stable public API;
- workflow marketplace;
- partner-distributed venture templates;
- shared benchmarks;
- agent-to-agent integration.

---

## 10. What to measure

Internal metrics should include:

- time from idea to first validation experiment;
- percentage of ideas killed before unnecessary building;
- human hours per venture;
- agent runs accepted without edits;
- repeated failure categories;
- cost per validated assumption;
- time blocked by missing Foundry functionality;
- percentage of new features reused by a second venture;
- external actions requiring intervention;
- venture progress per week.

The Foundry should optimize **decision quality and useful execution**, not merely the number of generated artifacts.

---

## 11. Signs the project is going wrong

Warning signs include:

- weeks of Foundry work without advancing a child venture;
- building generic features no current venture needs;
- autonomous agents producing large quantities of low-value work;
- scores treated as truth rather than hypotheses;
- inability to reconstruct why a decision was made;
- architecture complexity growing faster than user value;
- provider-specific code leaking throughout the domain model;
- features added because they look impressive rather than because they remove repeated friction.

When this occurs, return to a concrete venture and ask:

> What exact next step is blocked today?

---

## 12. Definition of a strong first version

A strong first version is not a polished "company generator."

It is a system in which you can select an idea, understand why it was selected, launch a real validation sequence, delegate bounded work to agents, review the outputs, retain evidence and decisions, and continue the venture a month later without reconstructing its history from scratch.

That is enough to make the Foundry useful—and enough to discover what it should become next.
