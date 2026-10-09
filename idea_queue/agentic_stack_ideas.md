### Prompt

I have both Claude MAx and ChatGPT Pro plans. It would be nice to have two things.

-   Some open source tool if exists that allows you to setup / see your routines (schedule jobs) that use different models / providers.
-   Some way of setting agentic workflows for given projects. Maybe for example I want one powerful agent overviewing, reviewing work of other agents. Can spawn some with the correct model / reasoning depending on the task. Learns as it goes that some model should be upgraded / downgraded automatically (or ask for user approval). Gives user tasks in a non blocking way if it can continue working on something else etc.

### Response

Yes. What you're describing is essentially a **personal AI engineering organization**: multiple coding agents, potentially from different providers, coordinated by a supervisor that assigns work, evaluates results, adjusts model choices, and involves you only when necessary.

There are now several open-source projects surprisingly close to this vision. And because you have both **Claude Max and ChatGPT Pro**, you have an interesting opportunity to build one without paying for every model call separately.

My recommendation is to investigate **Paperclip** first, with **Agency** and **Tutti** as alternatives depending on how much automation you want.

## 1\. The tools worth considering

### Paperclip — closest to your complete vision

**[GitHub: PaperclipAI/paperclip](https://github.com/paperclipai/paperclip)**

Paperclip is an open-source platform for organizing AI agents into teams, complete with roles, hierarchies, tasks, budgets, schedules, and human approvals.

Its architecture is particularly relevant to your idea:

```text
text                       YOU
                        │
                 ┌──────▼──────┐
                 │ Supervisor  │
                 │ Claude Opus │
                 └──────┬──────┘
                        │
          ┌─────────────┼──────────────┐
          │             │              │
    ┌─────▼─────┐ ┌─────▼─────┐ ┌──────▼─────┐
    │ Architect │ │ Developer │ │  Reviewer  │
    │  Opus     │ │   Codex   │ │  Codex     │
    │   High    │ │  Medium   │ │   High     │
    └───────────┘ └───────────┘ └────────────┘
```

Paperclip supports:

-   **Multiple providers:** Claude Code, Codex, Gemini CLI, OpenCode, and others.
-   **Agent hierarchies:** a supervising agent can coordinate subordinate agents.
-   **Recurring routines:** scheduled tasks, with execution history visible in a dashboard.
-   **Persistent context:** agents retain tasks, project goals, decisions, and history.
-   **Human approvals:** you can review decisions, block certain actions, or intervene.
-   **Task dependencies:** agents can work on independent tasks while other tasks are blocked.
-   **Isolated Git worktrees:** agents can work on separate branches.
-   **Budgets and monitoring:** observe activity and reported model usage.

Paperclip has a substantial open-source community and an MIT license. Its repository currently reports approximately 99,000 stars.

Importantly, **it is an orchestration platform, not itself an intelligent model router**. It provides the infrastructure for a supervisor to delegate tasks, but adaptive model selection and learning from previous outcomes need to be configured or implemented.

Source: [Paperclip documentation and repository](https://github.com/paperclipai/paperclip).

### 2\. Your subscriptions can be used — an important distinction

This was the first thing I wanted to verify, because otherwise an autonomous system could generate substantial additional API charges.

**There is good news on both sides.**

| Provider | Existing subscription | CLI usable with subscription | Paperclip integration |
| --- | --- | --- | --- |
| Anthropic | Claude Max | Yes, Claude Code | `claude_local` |
| OpenAI | ChatGPT Pro | Yes, Codex CLI | `codex_local` |

Anthropic's help center was updated on **October 7, 2026** and explicitly confirms that Claude Max subscription allowances still cover Claude Agent SDK, `claude -p`, and supported third-party usage. Max plans also now include monthly API credits.

OpenAI similarly supports using Codex CLI through your ChatGPT subscription.

More importantly, Paperclip's adapter documentation confirms:

-   Its Claude adapter recognizes **Claude subscription login**, not just API keys.
-   Its Codex adapter explicitly inherits your existing **ChatGPT subscription login** and can share that authentication with managed Codex agents.
-   Both adapters offer configurable models and reasoning effort.

There is one inconsistency worth flagging: **Paperclip's general installation guide tells new users to obtain paid API keys**, while its more detailed adapter documentation explicitly supports subscription authentication.

For your setup, I would configure the native CLI adapters using your existing logins, leave `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` unset for those agents, and verify authentication using Paperclip's _Test Environment_ feature.

This should allow you to consume your existing subscriptions, subject to their usage limits, rather than automatically paying API rates.

**Two caveats:**

1.  Subscription limits remain shared across the corresponding provider's tools. Running five Codex agents doesn't multiply your ChatGPT Pro allowance by five.
2.  Paperclip's token-cost estimates aren't necessarily actual charges when subscription authentication is used. You should distinguish estimated usage from billed API spend.

Also, **reasoning effort really is configurable in Paperclip**. For Claude, the adapter has an `effort` field. For Codex, it has `modelReasoningEffort`. So your original requirement—Opus with medium reasoning for a recurring job—is directly supported.

## 3\. Other open-source alternatives

### Agency — simpler dashboard, persistent agents, human approvals

**[GitHub: christag/agency](https://github.com/christag/agency)**

Agency is a relatively lightweight Python application with a web dashboard.

Its strongest feature is the way it handles agent observations and your decisions:

```text
textAgent detects an issue
        │
        ▼
Creates an observation
        │
        ▼
Proposes a solution
        │
        ▼
Human approval required?
        │
   ┌────┴────┐
   │         │
   Yes       No
   │         │
   ▼         ▼
 Inbox     Execute
   │         │
   └────┬────┘
        ▼
  Record outcome
```

It supports Claude Code, Codex, Gemini, and several other tools. Agents have persistent identities, memory, schedules, and shared project knowledge.

I particularly like the idea of agents collecting observations without immediately acting on every one.

For example, a testing agent might discover three reliability problems and submit a single proposal to address them.

Agency is also considerably lighter than Paperclip: no database or Docker requirement.

**Limitation:** Agency explicitly describes itself as a coordination layer, not a complete agent runner. You still need an execution mechanism underneath it. Its project is also much smaller, at roughly 71 GitHub stars currently.

### Tutti — best suited to disciplined software development

**[GitHub: nutthouse/tutti](https://github.com/nutthouse/tutti)**

Tutti focuses specifically on software engineering workflows.

Rather than organizing a virtual company, you describe your coding team and its workflows in a `tutti.toml` configuration.

For instance:

```toml
toml[roles]
architect = "claude-code"
implementer = "codex"
reviewer = "claude-code"
tester = "codex"
```

Its main capabilities include:

-   Isolated Git worktrees.
-   Parallel agents using Claude Code and Codex.
-   Automated implementation, testing, review, and merge workflows.
-   An interactive browser dashboard.
-   Persistent workflows expressed as code.
-   CI and approval gates.
-   Scheduled workflows.

Importantly, Tutti explicitly supports existing CLI authentication without additional API keys.

For your software projects, Tutti may be a better conceptual fit than Paperclip if you want something relatively deterministic, where a workflow defines exactly which agents participate and what they must produce.

**Limitation:** It is less focused on intelligent organizational decision-making. Its orchestration is primarily workflow-driven rather than supervisor-driven. It is also an early-stage project (approximately 131 GitHub stars).

### Hydra — especially interesting for adaptive routing

**[GitHub: krowxx/hydra](https://github.com/krowxx/hydra)**

Hydra approaches your second requirement from a different direction.

It supports Claude, Codex, and Gemini, and its advertised functionality includes:

-   Automatic agent selection.
-   Parallel execution.
-   Model selection based on task complexity.
-   Multi-round discussion between agents.
-   Model reasoning-effort configuration.
-   Adaptive routing informed by task outcomes.

For example, you could ask it to develop a feature and have it decide whether to use a single Codex agent or a multi-agent process involving Claude and Codex.

This is closer to the **intelligent routing** you described than Paperclip's default behavior.

However, I would be cautious about adopting it as your principal platform. The repository is a small fork with only a few stars, and it explicitly describes itself as under active development. I would treat its adaptive routing as promising functionality to experiment with, not a proven optimization system.

### Comparison

| Capability | Paperclip | Agency | Tutti | Hydra |
| --- | --- | --- | --- | --- |
| Claude + Codex | ✅ | ✅ | ✅ | ✅ |
| Central dashboard | ✅ | ✅ | ✅ | Operator console |
| Scheduled routines | ✅ | ✅ | ✅ | Automation |
| Agent hierarchy | ✅ | Partial | Role-based | Routing-based |
| Supervisor delegation | ✅ | Partial | Workflow-based | ✅ |
| Human approval inbox | ✅ | ✅ | ✅ | Limited |
| Git worktrees | ✅ | Via runner | ✅ | ✅ |
| Reasoning-effort control | ✅ | Via runtime | Configurable via runtime | ✅ |
| Adaptive model routing | Custom | Custom | Custom | Advertised |
| Persistent project context | ✅ | ✅ | ✅ | ✅ |
| My assessment | **Best overall** | Best lightweight dashboard | Best coding workflows | Experimental routing |

For your purposes, I would shortlist **Paperclip and Tutti**, with Agency worth exploring if you prefer a minimalist dashboard.

---

## 4\. How I would design your intelligent supervisor

This is where I think your idea gets particularly interesting.

Rather than simply having several agents collaborating, I'd introduce a separation between **project management, task execution, and model evaluation**.

### A. One supervisor per project

Imagine using your Coopain project.

You give the supervisor a relatively high-level instruction:

> Develop the matching algorithm, improve its effectiveness, and keep the existing application working. Choose appropriate agents, review their work, and consult me for product decisions.

The supervisor is Claude Opus, running at medium or high effort.

It decomposes the objective into tasks and decides which agents to use.

For example:

| Task | Selected agent | Effort |
| --- | --- | --- |
| Analyze existing matching architecture | Claude Opus | High |
| Implement similarity scoring | Codex | Medium |
| Add database indexes | Codex | Low |
| Generate unit tests | Codex | Medium |
| Review algorithmic correctness | Claude Opus | High |
| Update documentation | Claude Sonnet | Low |
| Evaluate overall implementation | Claude Opus | High |

These are initial assignments, not claims that one model is universally better at those tasks.

The supervisor manages dependencies and ensures that independent tasks can run simultaneously.

### B. Adaptive model selection

This is the feature I find most valuable, and the one I would be most inclined to implement myself.

Instead of hardcoding which model to use, maintain a record of agent performance.

Suppose the system initially assigns backend tasks to Codex at medium effort.

It gathers data like:

| Task category | Model | Effort | Success rate | Average duration |
| --- | --- | --- | --- | --- |
| Backend CRUD | Codex | Low | 94% | 2 min |
| Backend CRUD | Codex | Medium | 98% | 4 min |
| Complex architecture | Codex | Medium | 63% | 12 min |
| Complex architecture | Opus | High | 92% | 9 min |
| Documentation | Sonnet | Low | 97% | 2 min |

_Illustrative numbers only._

The supervisor can discover that:

-   Codex Low is usually sufficient for CRUD.
-   Opus High is more reliable for architecture.
-   High reasoning rarely improves documentation.
-   A certain class of bugs frequently requires escalation.

It adjusts its routing policy accordingly.

A basic escalation policy might be:

```python
pythondef choose_agent(task, history):
    model, effort = history.best_configuration(task.category)

    if task.risk == "critical":
        effort = "high"

    if task.previous_failures >= 2:
        model = "opus"
        effort = "high"

    return model, effort
```

Of course, this is much simpler than a complete adaptive system.

**The important part is how success is measured.**

I would avoid allowing agents to judge their own performance without external verification.

Instead, measure concrete outcomes:

-   Did the tests pass?
-   Did the independent reviewer find problems?
-   Was the implementation accepted?
-   Did subsequent work reveal regressions?
-   How long did the task take?
-   How much model usage did it consume?

With enough history, the routing policy could eventually use a contextual bandit or other online learning approach.

And I would distinguish _escalation_ from _downgrading_: escalate quickly after clear failures, but only downgrade after statistically meaningful evidence that the cheaper configuration performs comparably.

Neither Paperclip nor Tutti currently provides this entire learning system automatically.

Paperclip does, however, provide useful foundations: evaluation tooling, persistent task records, model configuration, and execution history.

### C. Non-blocking human involvement

Your idea about involving the user without stopping the entire workflow is particularly important.

Consider this scenario:

The team is working on Coopain and discovers that the matching algorithm could expose information about candidate identities.

The supervisor decides this requires a product decision from you.

It creates a task in your inbox:

**Decision required: Candidate profile visibility**

Options:

-   A. Keep candidate identities hidden until mutual agreement.
-   B. Reveal identities immediately after matching.
-   C. Allow candidates to configure their privacy preferences.

Meanwhile, the supervisor can continue working on:

-   Backend optimizations.
-   Test coverage.
-   Documentation.
-   Unrelated frontend improvements.

Only tasks depending on the privacy decision should be blocked.

I would implement this with explicit task states:

```text
textBACKLOG
   ↓
READY
   ↓
RUNNING ────────────────┐
   │                    │
   ▼                    ▼
REVIEW             NEEDS_HUMAN
   │                    │
   ▼                    │
DONE                 BLOCKED
                        │
                        ▼
                  Human responds
                        │
                        ▼
                      READY
```

This is where Paperclip's task dependencies, approval processes, and persistent task records would be genuinely useful.

The supervisor doesn't have to sit idle while you're unavailable.

### D. Separate the supervisor from the reviewer

One subtle design choice: I would not rely solely on the supervisor reviewing its own agents' work.

Suppose Claude Opus creates an architecture, delegates implementation to Codex, and then reviews the implementation itself.

It might miss a fundamental problem because the implementation follows its own flawed architecture.

For important work, I'd introduce independent review.

For example:

1.  Claude Opus defines an architecture.
2.  Codex implements it.
3.  A separate Codex or Claude reviewer evaluates it without being primed to agree with the original design.
4.  The supervisor reconciles the review findings.

Independent reviewers should see the requirements and relevant code, but not necessarily all the reasoning behind the original implementation.

This reduces correlated errors.

---

## 5\. What I'd actually deploy on your Linux machine

I would start with **Paperclip and three agents**, rather than building a large organization immediately.

### Initial architecture

```text
text                PAPERCLIP DASHBOARD
                        │
                ┌───────┴───────┐
                │   PROJECT     │
                │  SUPERVISOR   │
                │               │
                │  Claude Opus  │
                │  Effort: High │
                └───────┬───────┘
                        │
              Task decomposition
                        │
          ┌─────────────┴─────────────┐
          │                           │
   ┌──────▼──────┐             ┌──────▼──────┐
   │ IMPLEMENTER │             │  REVIEWER   │
   │             │             │             │
   │   Codex     │             │ Claude Opus │
   │   Medium    │             │   Medium    │
   └──────┬──────┘             └──────┬──────┘
          │                           │
          └─────────────┬─────────────┘
                        │
                 Tests and gates
                        │
                 User approval
                 when required
```

I'd use the following configuration initially:

| Component | Configuration |
| --- | --- |
| Orchestrator | Paperclip |
| Supervisor | Opus, High |
| Implementer | Codex, Medium |
| Reviewer | Opus, Medium |
| Task isolation | Git worktrees |
| Recurring automation | Paperclip routines |
| Human decisions | Paperclip approval inbox |
| Automatic deployment | Disabled initially |
| Automatic model switching | Disabled initially, log recommendations |
| Authentication | Existing Claude Max + ChatGPT Pro |

Once this setup is operating reliably, introduce dynamic model selection.

### Installation

Paperclip's official installation command is:

```bash
bashnpx paperclipai@latest onboard --yes
```

It requires Node.js 24.11 or newer.

The default local installation runs a dashboard at:

**[http://localhost:3100](http://localhost:3100)**

You can subsequently install it as a background service:

```bash
bashnpx paperclipai install
paperclipai service install
```

These commands are documented in the [official installation guide](https://docs.paperclip.ing/guides/getting-started/installation/).

Before onboarding agents, make sure the native CLIs are authenticated:

```bash
bashclaude auth status
codex login status
```

When configuring agents, select the `claude_local` and `codex_local` adapters, use their existing subscription logins, and configure the model and effort for each agent.

I would test each adapter with one harmless task before introducing unattended execution.

### Your original every-two-days routine

You could then create a routine in Paperclip to:

-   Run against a particular project.
-   Assign work to Opus with medium effort.
-   Record the result in the dashboard.
-   Trigger further work if needed.
-   Notify you when human input is required.

One technical detail: **a standard cron expression with `*/2` in the day-of-month field is not a true 48-hour schedule**, because it resets at month boundaries.

If you need exactly 48 hours between executions, keep a monotonic `systemd` timer and have it invoke a Paperclip webhook. Otherwise, an approximate every-other-day calendar schedule may be sufficient.

---

## 6\. Two things I would be careful about

**First, I wouldn't immediately allow unrestricted execution on your primary filesystem.**

Paperclip's Claude adapter enables unattended permission bypass by default, and its Codex adapter can also run without sandbox protections.

Given that agents can run shell commands, this is a substantial security consideration.

I'd use separate Git worktrees, restrict access to relevant project directories, and reserve your approval for potentially destructive actions, external publication, production changes, or credential-sensitive operations.

The supervisor's approval policy should be enforced by the orchestration layer, not merely described in its system prompt.

**Second, don't optimize the number of agents too early.**

For example, implementing a small UI change with one Codex agent may be faster and more reliable than involving an architect, developer, reviewer, and supervisor.

At the opposite extreme, a major authentication redesign spanning several services may benefit greatly from independent design, implementation, security review, and testing agents.

A well-designed supervisor should learn not only _which model_ to use, but also **when not to delegate at all**.

This is an important part of optimizing the overall system.

---

## 7\. My recommendation

I see two sensible directions for you.

**Option A — Paperclip as your central AI workspace**

This would be my first choice.

You get a dashboard for your routines and projects, Claude and Codex integration, a supervisor hierarchy, human approvals, persistent context, and scheduling.

You would then extend the model-selection logic as you learn what works.

The advantage is that the infrastructure is already there. You can concentrate on the interesting part: making the supervisor intelligent.

**Option B — Tutti plus a custom adaptive supervisor**

This would be my choice if your primary interest is building a sophisticated autonomous _software engineering system_, rather than managing several kinds of AI workers.

Tutti provides the workflows, Git isolation, monitoring, and execution infrastructure. You implement a supervisor that chooses workers and adjusts its routing policy based on measured performance.

This gives you more control over the intelligence, but requires more development.

### A final thought

Given your ML background, the adaptive routing component could become an interesting standalone project.

There are really three optimization problems:

1.  **Model selection:** Which model and reasoning effort should handle a given task?
2.  **Workflow selection:** Should the task involve one agent, multiple agents, independent review, or human involvement?
3.  **Resource allocation:** Given subscription limits, task priorities, and expected execution times, which agents should run now?

The third one is particularly interesting in your case because you're managing two largely independent subscription allowances, rather than a single monetary API budget.

You could eventually build a supervisor that optimizes the use of both subscriptions automatically.

**I would begin by installing Paperclip on Linux and testing a three-agent team using your existing subscriptions.** If it handles the coordination well, you have a strong foundation. If you find its workflow model too restrictive, Tutti is the alternative I'd explore next.

**Confidence: High** regarding the documented capabilities and subscription compatibility; **medium** regarding how reliable these platforms are under sustained autonomous workloads. I have verified their documentation and repositories, but not personally stress-tested their current releases.

### Prompt

Can I use locally downloaded models for very easy tasks ? Will it be able to smartly recognize it can call the dumb local model ? What if I hit usage limit ? Does the whole system break down or does it spawn some backup provider ? Do I have to manually setup for each project ? Or can I have some templates that are used automatically (or I can select) for a new project ? Say I have a kaggle competition workflow, a software engineering workflow, a ML engineer with training etc. workflow, a math research workflow etc. Also does paperclip handle looping on tasks. Say the ultimate goal is to build an app ready to be shipped on the app store. and you have some global description of the app to start with. As you go on, the app usage may shift, user might give online feedback without waiting for an agent inbound. Initial sub goal might be reached and then you would automatically determine the best next goal to pursue. This could happen also especially in some research where you try stuff, get insight, refocus your research etc.

### Response

**Yes to all four ideas in principle, but Paperclip doesn't yet implement all of them automatically.** After checking its current documentation and issue tracker, I think it could be a very good foundation for what you're imagining, with a relatively small amount of additional orchestration logic.

The most interesting part of your proposal isn't simply coordinating multiple agents. It's building a system that can **choose how much intelligence to spend, recover from unavailable models, reuse specialized workflows, and continuously decide what to work on next**.

Here's where Paperclip stands as of October 2026.

| Capability | Paperclip today | What you'd need to add |
| --- | --- | --- |
| Run downloaded local models | Yes, through compatible agent runtimes | Configure a local inference server |
| Choose local models for easy tasks | Possible through delegation | Adaptive task-complexity router |
| Recover from provider usage limits | Retry/recovery mechanisms | Reliable cross-provider failover policy |
| Reusable project configurations | Yes, team templates and import/export | Your own specialized templates |
| Supervisor delegates to agents | Yes | Task-specific model optimization |
| Keep working toward a long-term goal | Yes, through tasks, delegation and recurring execution | Strategic planning and replanning policies |
| Respond to new user feedback | Yes, through tasks, comments and integrations | Feedback prioritization and product decision logic |
| Automatically discover better research directions | Possible | Research-specific evaluation and exploration strategy |

Paperclip's current architecture supports goals, nested subgoals, agent hierarchies, persistent tasks, execution history, scheduled routines, and reusable teams. These are genuine platform features, not just promises in a roadmap.

## 1\. Using locally downloaded models for easy tasks

### Yes — and I would definitely include one

The architecture would be:

```text
text                  SUPERVISOR
                  Claude Opus
                      │
                Task assessment
                      │
         ┌────────────┼────────────┐
         │            │            │
      TRIVIAL       NORMAL       COMPLEX
         │            │            │
         ▼            ▼            ▼
    Local model   Codex Medium  Claude Opus
      (free)      (ChatGPT Pro)  (Claude Max)
         │            │            │
         └────────────┼────────────┘
                      │
                Verify results
                      │
              Accept or escalate
```

For example, suppose your application has 200 TypeScript files and needs a consistent naming convention.

A local model could handle mechanical changes, while Codex handles normal development and Opus handles architecture or difficult debugging.

Local models are also useful for:

-   Classifying incoming issues.
-   Summarizing agent execution logs.
-   Extracting structured information.
-   Categorizing user feedback.
-   Identifying duplicate tasks.
-   Generating straightforward documentation.

There is no reason to spend Opus tokens generating a short summary of a successful test run.

### How to connect local models

I would use **[Ollama](https://ollama.com/)** for inference and **[OpenCode](https://opencode.ai/)** or **[Pi](https://github.com/badlogic/pi-mono)** as the agent runtime.

Paperclip officially supports both OpenCode and Pi adapters, including custom provider endpoints and model configuration. This means you can expose an Ollama model through a local HTTP API and have a Paperclip agent use it.

For example, with Ollama installed:

```bash
bashollama pull qwen3:8b
ollama serve
```

The model is then served locally, normally on port `11434`.

That particular model is just an example; the appropriate choice depends on your GPU, VRAM and available RAM.

You could create three local workers:

| Worker | Task | Model class |
| --- | --- | --- |
| Local classifier | Decide task type and priority | Small 3–8B |
| Local assistant | Summaries, simple edits | 8–14B |
| Local coding worker | Relatively simple coding tasks | Coding-specialized 14–32B |

Whether the larger models are practical depends heavily on your hardware.

### Will Paperclip intelligently choose the local model?

**Not automatically in the way you're imagining.**

Paperclip lets agents delegate tasks to other agents, but it doesn't currently provide a documented, continuously learning complexity classifier that automatically selects the smallest sufficient model.

I would implement this as a routing policy.

For example:

```python
pythondef route_task(task):
    if task.requires_research:
        return "claude-opus-high"

    if task.is_mechanical and task.is_easily_verified:
        return "local-coder"

    if task.complexity < 0.5:
        return "codex-medium"

    return "claude-opus-high"
```

But we can do better.

Rather than simply classifying complexity, the system could **start with the least expensive plausible model and escalate based on evidence**.

For example:

1.  Assign a small refactoring to the local model.
2.  Run tests and static analysis.
3.  If it fails, try Codex Medium.
4.  If that fails, escalate to Opus.
5.  Record which level was ultimately necessary.

Over time, the router learns that some kinds of tasks are consistently beyond the local model.

A critical nuance: passing tests is not always sufficient evidence of correctness. For security-sensitive code or important architectural changes, the system should use stronger validation or independent review.

This gives you a useful combination of low cost and reliability, without asking Opus to make every trivial routing decision.

## 2\. What happens when you hit Claude Max or ChatGPT Pro usage limits?

This is one area where I'd be more cautious about relying on Paperclip without modifications.

### What Paperclip currently does

Paperclip has mechanisms for detecting certain provider failures, scheduling retries, recovering interrupted tasks, and pausing agents.

However, **automatic switching from Claude to Codex when Claude Max is exhausted is not a guaranteed built-in feature**.

In fact, there are several relevant open issues:

-   [#2743 — Automatic model/adapter fallback](https://github.com/paperclipai/paperclip/issues/2743)
-   [#3317 — Fallback when subscription quota is exceeded](https://github.com/paperclipai/paperclip/issues/3317)
-   [#11597 — Provider quota recovery can repeatedly launch failed runs](https://github.com/paperclipai/paperclip/issues/11597)

Recent versions have added quota-aware retry machinery, but reports show that some execution paths still mishandle exhaustion.

So I wouldn't assume that running out of Claude Max usage automatically means your work continues on ChatGPT Pro.

### What I would implement

A central **provider availability manager**, independent of the individual agents.

```text
text                 New task arrives
                        │
                        ▼
                  MODEL ROUTER
                        │
            ┌───────────┴───────────┐
            │                       │
       Check quotas            Check task
       and availability        requirements
            │                       │
            └───────────┬───────────┘
                        │
                        ▼
                  Choose provider
                        │
           ┌────────────┼─────────────┐
           │            │             │
       Claude Max   ChatGPT Pro     Ollama
           │            │             │
           ▼            ▼             ▼
       Available?    Available?    Available?
           │            │             │
           └────────────┼─────────────┘
                        │
                        ▼
                  Execute task
                        │
                        ▼
               Record outcome
```

For each provider, maintain a state such as:

```python
pythonprovider_state = {
    "claude": {
        "available": False,
        "reason": "usage_limit",
        "retry_after": "2026-10-09T15:00:00+02:00",
    },
    "codex": {
        "available": True,
    },
    "ollama": {
        "available": True,
    },
}
```

Then the behavior could be:

| Situation | Desired behavior |
| --- | --- |
| Claude limit reached | Switch eligible tasks to Codex |
| Codex limit reached | Switch eligible tasks to Claude |
| Both subscriptions exhausted | Use local models where suitable |
| Local model insufficient | Queue task until stronger model becomes available |
| Both paid providers available again | Resume normal routing |
| Provider repeatedly times out | Temporarily stop sending it work |
| All providers unavailable | Preserve tasks and alert you |

**The overall workflow needn't fail because a single provider is unavailable.**

But there are subtleties.

### A failed session cannot always be resumed by another provider

Suppose Claude Opus has spent 45 minutes investigating a complicated bug when its usage limit is reached.

You can't simply hand its internal reasoning state to Codex.

Instead, the system should maintain durable checkpoints:

```text
texttask-143/
├── requirements.md
├── investigation.md
├── decisions.md
├── current-status.md
└── next-steps.md
```

Ideally, these are stored as Paperclip task documents or project artifacts, with code changes committed to a task-specific Git branch.

The replacement agent then reads this state, inspects the actual repository, and continues the task.

Some work may need to be repeated, but you don't lose the entire investigation.

I'd also implement **provider-specific circuit breakers**: once Claude's quota is known to be exhausted, stop probing it repeatedly until the reset time.

One more distinction matters: a provider subscription quota is not the same as a Paperclip budget. A Paperclip budget limit may be a deliberate safety boundary. I would never automatically override a hard budget cap just because another provider is available.

---

## 3\. Can you create reusable workflows for different kinds of projects?

**Yes. This is already supported rather well.**

Paperclip has two particularly useful capabilities:

1.  A **Team Catalog** for installing predefined combinations of agents, roles, projects, skills and routines.
2.  **Company export/import**, allowing you to preserve an entire customized configuration and reuse it as a template.

The built-in catalog already includes an engineering team, a design team, and an executive team. During installation, you choose the runtimes for the agents rather than being forced to use predefined providers.

Custom configurations can also be exported as human-readable Markdown packages and imported into a new organization. See [Team Catalog](https://docs.paperclip.ing/guides/org/team-catalog/) and [Export & Import](https://docs.paperclip.ing/guides/power/export-import/).

### I'd create four templates for your projects

Each could have its own supervisor, specialists, tools, evaluation criteria, and operating policies.

#### Template A — Software engineering / app development

For projects such as Coopain.

| Role | Responsibility |
| --- | --- |
| Product manager | Requirements, priorities, feedback |
| Architect | Architecture, system design |
| Developer | Implementation |
| QA engineer | Automated tests, integration tests |
| Reviewer | Code quality, security, maintainability |
| Release manager | Builds, releases, deployment |

Typical loop:

**Plan → Implement → Test → Review → Integrate → Evaluate → Replan**

Human approval would be required for major product changes, production deployments, or external publication.

#### Template B — Kaggle competition

For your ARC-related experiments or another machine-learning competition.

| Role | Responsibility |
| --- | --- |
| Research lead | Hypotheses, experiment priorities |
| Data scientist | EDA, feature engineering |
| ML engineer | Training pipelines, optimization |
| Experiment manager | Tracking and comparing runs |
| Validation specialist | Leakage detection, CV strategy |
| Submission agent | Packaging and checking submissions |

Typical loop:

**Hypothesize → Implement → Train → Evaluate → Analyze → Select next experiment**

The important distinction here is that an experiment failing to improve the score isn't necessarily a failure of the agent.

It may have generated valuable information about the problem.

A good supervisor should distinguish between _unsuccessful execution_ and _a successful experiment with a negative result_.

For Kaggle I'd also make the system aware of compute budgets, GPU availability, submission limits, and deadlines.

#### Template C — ML engineering / research and training

This would differ from Kaggle because the objective is reliable, reproducible, deployable models rather than maximizing a leaderboard score.

| Role | Responsibility |
| --- | --- |
| ML lead | Objectives and architecture |
| Research scientist | Modeling approaches |
| Data engineer | Data pipelines and quality |
| Training engineer | Training runs, GPU optimization |
| Evaluation engineer | Robustness and benchmarking |
| MLOps engineer | Reproducibility, deployment, monitoring |

Typical loop:

**Specify → Prototype → Train → Evaluate → Diagnose → Refine → Deploy → Monitor**

Here, the agents need access to external processes that may run for hours or days.

Training jobs shouldn't occupy an LLM session while the GPU is working.

Instead, the training agent should submit the experiment, persist its ID and configuration, and stop. A subsequent completion event should wake the evaluation agent.

Paperclip's webhook-triggered routines and external execution integrations provide the necessary foundation.

#### Template D — Mathematics research

This one is particularly interesting because the workflow is fundamentally less deterministic.

| Role | Responsibility |
| --- | --- |
| Principal mathematician | Research direction |
| Theorem explorer | Conjectures and approaches |
| Proof developer | Detailed proofs |
| Skeptical reviewer | Counterexamples, logical gaps |
| Computational mathematician | Numerical and symbolic experiments |
| Literature researcher | Relevant results |
| Exposition agent | Write and organize the manuscript |

Typical loop:

**Conjecture → Explore → Find evidence → Attempt proof → Challenge proof → Refine conjecture**

For example, with your work on periodic orbits, the computational agent might investigate a family of parameter values.

The theorem explorer notices an apparent pattern, while the skeptical reviewer actively searches for counterexamples.

If the conjecture fails, the system should preserve the counterexample and use it to refine its understanding.

For mathematical research, I would make the skeptical reviewer unusually important. Plausible proofs from different LLMs can share subtle logical errors, and numerical evidence alone cannot establish a theorem.

### What creating a new project would look like

Ideally:

```text
textCreate new project
       │
       ▼
Choose template
       │
       ├── Software engineering
       ├── Kaggle competition
       ├── ML engineering
       └── Mathematics research
       │
       ▼
Provide repository / directory
       │
       ▼
Describe objective
       │
       ▼
Supervisor analyzes project
       │
       ▼
Choose initial team and resources
       │
       ▼
Approve initial plan
       │
       ▼
Start autonomous execution
```

You could also have the supervisor recommend a template based on the repository contents, then ask for confirmation if the classification is ambiguous.

Paperclip doesn't provide your four specialized templates out of the box, but **you can build and reuse them without reconfiguring each agent individually**.

I would store the templates in a Git repository so they can be improved and versioned over time.

For example:

```text
text~/agent-workflows/
├── shared/
│   ├── model-routing.md
│   ├── escalation-policy.md
│   └── review-policy.md
├── software-engineering/
├── kaggle/
├── ml-engineering/
└── mathematics-research/
```

Paperclip can manage the deployed configurations; Git would give you a clean, portable source of truth for your custom workflows.

## 4\. Does Paperclip support continuous goal-driven loops?

**Yes, to a significant extent. This is arguably its most important feature for your use case.**

But there are three different kinds of loops, and I'd distinguish them carefully.

### Level 1 — Execution loops: already supported

This is the simplest case:

```text
textImplement feature
       ↓
Run tests
       ↓
Review implementation
       ↓
Problems found?
       │
   Yes ├────→ Fix implementation ────┐
       │                             │
       └─────────────────────────────┘
       │
       No
       ↓
Mark task complete
```

Paperclip has a native **execution policy** mechanism for this.

When an agent finishes a task, Paperclip can automatically route it to a reviewer. If the reviewer requests changes, the task returns to the implementation agent.

This isn't merely an instruction in a prompt: the runtime enforces the transitions.

It also has safeguards against endless reviewer/developer disagreements. By default, after three consecutive agent-requested revision rounds, the review escalates to a human.

This is documented in [Execution Policy](https://docs.paperclip.ing/guides/power/execution-policy/).

### Level 2 — Goal-driven loops: supported, but dependent on the supervisor

This is closer to what you're describing.

You define:

> Build a mobile application that helps people organize local sports matches. The eventual objective is to launch a useful, reliable product on the App Store and acquire active users.

The supervisor takes that broad objective and creates a plan.

For example:

**Iteration 1 — MVP**

-   Define the core functionality.
-   Implement authentication.
-   Implement match creation.
-   Implement invitations.
-   Build an initial mobile interface.
-   Test the application.

Once these tasks are complete, the supervisor evaluates the result.

It concludes that the MVP exists but is not sufficiently reliable for release.

**Iteration 2 — Release preparation**

-   Add automated UI tests.
-   Improve error handling.
-   Perform a security review.
-   Fix critical bugs.
-   Prepare store metadata.
-   Test the release build.

Once that is complete, it identifies the next important objective.

**Iteration 3 — Product improvement**

-   Collect usage data.
-   Examine user feedback.
-   Identify friction in onboarding.
-   Prioritize improvements.
-   Implement and evaluate them.

And so on.

Paperclip supports the necessary hierarchy:

```text
textGLOBAL GOAL
Build a successful sports application
        │
        ├── Subgoal: Deliver MVP
        │       ├── Authentication
        │       ├── Match creation
        │       └── Invitations
        │
        ├── Subgoal: Prepare release
        │       ├── Security
        │       ├── Testing
        │       └── Store submission
        │
        └── Subgoal: Improve retention
                ├── Analyze feedback
                ├── Identify drop-off
                └── Improve onboarding
```

In fact, the official [delegation documentation](https://docs.paperclip.ing/guides/org/delegation/) explicitly describes a CEO agent receiving an overarching objective, developing a strategy, requesting approval, decomposing that strategy into tasks, assigning them, monitoring progress, and escalating blockers.

**The distinction is that Paperclip provides the organizational machinery, while the supervisor model provides the strategic intelligence.**

An agent won't necessarily invent a useful next goal just because its current tasks are finished.

You need to give the supervisor an explicit responsibility for periodically reviewing the global objective and deciding what to do next.

### Level 3 — Continuous strategic adaptation: needs additional configuration

This is the most interesting level.

You don't just want:

> Finish subgoal A, then proceed to subgoal B.

You want:

> Continuously evaluate whether subgoal B is still the right thing to pursue.

Imagine the app is launched.

The initial strategy is to build features for organizing football matches.

After several weeks, the system discovers that users are increasingly organizing volleyball matches instead.

It receives feedback indicating that volleyball organizers struggle with balancing teams by skill level.

The supervisor should potentially conclude:

> Our original roadmap emphasized football-specific features, but current demand suggests that volleyball team balancing may provide more value. We should reconsider the next milestone.

That is a genuine strategic loop.

I would design it like this:

```text
text             GLOBAL OBJECTIVE
                     │
                     ▼
              STRATEGIC PLANNER
                     │
                     ▼
              CURRENT PRIORITIES
                     │
                     ▼
                TASK PLANNING
                     │
                     ▼
              AGENT EXECUTION
                     │
                     ▼
             QUALITY EVALUATION
                     │
                     ▼
               DELIVER RESULTS
                     │
                     ▼
              MEASURE OUTCOMES
                     │
            ┌────────┴────────┐
            │                 │
       New feedback      New discoveries
            │                 │
            └────────┬────────┘
                     │
                     ▼
             STRATEGIC REVIEW
                     │
               ┌─────┴─────┐
               │           │
           Continue     Reprioritize
               │           │
               └─────┬─────┘
                     │
                     ▼
              NEXT ITERATION
```

I would configure three mechanisms to make this happen.

**1\. Event-driven feedback**

External events can create new work immediately.

For example, an app feedback form sends a webhook to Paperclip. That creates a task for a feedback-analysis agent.

A local model could classify the feedback, associate it with existing issues, and determine whether it warrants escalation.

The official routine system supports signed external webhooks, schedules, task creation and execution history.

However, connecting your actual application analytics, reviews, bug reports, and user feedback requires integration work. Paperclip doesn't automatically observe everything happening in your product.

**2\. Periodic strategic reviews**

I would configure a supervisor routine that runs, say, every two days.

Its instructions would be something like:

> Review progress against the global objective. Analyze completed tasks, outstanding problems, experiment results, user feedback, and resource availability.
> 
> Determine whether the current priorities are still appropriate.
> 
> If necessary, create, cancel, or reprioritize tasks.
> 
> Propose changes to major objectives for human approval.
> 
> Continue delegating approved work without waiting for unrelated human decisions.

This is where Paperclip's scheduled routines are particularly useful.

**3\. Explicit goal-revision rules**

The supervisor should distinguish between:

-   **Operational decisions:** Can be made autonomously.
-   **Tactical decisions:** Can be made autonomously within agreed limits.
-   **Strategic decisions:** May require your approval.

For example, deciding to optimize a slow database query is operational.

Deciding to prioritize onboarding improvements over a secondary feature is tactical.

Deciding to abandon the sports application and turn it into a gambling platform is a fundamental change of mission, and should require explicit approval.

This avoids the danger of an agent pursuing a goal that gradually diverges from what you actually wanted.

---

## 5\. The research case is even more interesting

I think your mathematics and ML research examples reveal an important limitation of conventional agent workflows.

In ordinary software engineering, you usually know what constitutes success.

The tests pass, the feature works, and the requirements are satisfied.

In research, you often don't know what you're looking for until you've found it.

### Example: mathematical exploration

Imagine the objective is to investigate a conjecture about periodic orbits.

The supervisor starts with a hypothesis.

```text
textInitial conjecture
       │
       ▼
Numerical investigation
       │
       ▼
Apparent supporting pattern
       │
       ▼
Attempt analytical proof
       │
       ▼
Find counterexample
       │
       ▼
Understand why conjecture failed
       │
       ▼
Formulate narrower conjecture
       │
       ▼
Investigate again
```

Here, finding a counterexample is not a failure.

It may be the most valuable outcome of the entire experiment.

A naive agent system might repeatedly try to prove the original false conjecture.

A good research supervisor should recognize the significance of negative results and change direction.

### I'd introduce a research memory

Rather than relying entirely on conversation history, maintain structured research records:

```text
textresearch/
├── objectives.md
├── established-results.md
├── conjectures.md
├── counterexamples.md
├── open-questions.md
├── failed-approaches.md
├── promising-directions.md
└── experiment-history/
```

Each research iteration would update the relevant records.

For example:

```yaml
yamlhypothesis: H17
description: "Property P holds for all admissible parameters."

status: disproved

evidence:
  - numerical_counterexample_42

consequences:
  - "Restrict the conjecture to interval I."
  - "Investigate the boundary of I."

next_steps:
  - verify_counterexample
  - derive_boundary_condition
  - attempt_restricted_proof
```

This information would influence subsequent task selection.

It's especially important to distinguish experimentally observed results from mathematically proved results.

### An adaptive research supervisor

I would actually give your research workflow two supervisory functions.

**Research director:** Chooses hypotheses and allocates effort.

**Research critic:** Challenges assumptions, identifies logical gaps, and evaluates whether claimed progress is real.

The director might propose spending two days investigating one conjecture.

The critic might argue that the evidence is weak and that a quick computational experiment could invalidate the conjecture.

The director then decides how much investigation is justified.

This resembles research prioritization under uncertainty more than traditional project management.

For ML research, you can make the decision quantitative using expected improvement, information gain, computational cost, or other acquisition criteria.

For pure mathematics, the evaluation will necessarily be more qualitative.

Paperclip supports the agents, delegation, task records and recurring execution needed for this. **The actual research strategy would have to be implemented in your agent instructions and evaluation procedures.**

---

## 6\. What I would add on top of Paperclip

After looking more closely at the current capabilities, I wouldn't build an entirely new orchestration platform.

I'd use Paperclip for the persistent organizational state and add a small **adaptive control layer**.

Conceptually:

```text
text┌──────────────────────────────────────────────┐
│                 PAPERCLIP                    │
│                                              │
│   Projects · Goals · Tasks · Approvals       │
│   Schedules · Dashboard · Agent execution    │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│             ADAPTIVE CONTROLLER              │
│                                              │
│  1. Task complexity estimation               │
│  2. Model and effort selection               │
│  3. Provider quota management                │
│  4. Automatic failover                       │
│  5. Agent performance evaluation             │
│  6. Strategy-review scheduling               │
│  7. Learning from previous outcomes          │
└──────────────────────┬───────────────────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
     Claude Max    ChatGPT Pro   Local LLM
       Agents        Agents       Agents
```

I'd build that controller in Python, with a small SQLite database initially.

Paperclip's API would let it inspect tasks and runs, assign work, and update agent configurations. Ollama would provide the local inference endpoint.

You wouldn't need to modify Paperclip's source code for the initial version.

A more ambitious version could be implemented as a Paperclip plugin.

### The part I'd prioritize: learning which model to use

I'd collect data on every execution:

```python
python{
    "task_type": "bugfix",
    "estimated_complexity": 0.35,
    "model": "local-coder",
    "effort": "medium",
    "execution_seconds": 85,
    "tests_passed": True,
    "review_accepted": True,
    "required_escalation": False
}
```

The controller could gradually learn when to use a local model versus your paid subscriptions.

I'd also track whether independent review was necessary, since the optimal workflow isn't always the one with the cheapest implementation agent.

For example, spending five minutes on a local implementation followed by twenty minutes reviewing and fixing it may be worse than giving the task directly to Codex.

The actual optimization objective should include **total execution time, model usage, verification cost, and probability of a correct outcome**.

---

## 7\. How I'd start

I wouldn't try to implement all this immediately. I'd introduce the capabilities progressively.

| Phase | Implementation | Complexity |
| --- | --- | --- |
| 1 | Paperclip + Claude + Codex | Low |
| 2 | Add Ollama local agent | Low–medium |
| 3 | Add reusable project templates | Medium |
| 4 | Add automatic provider failover | Medium |
| 5 | Add strategic review loops | Medium |
| 6 | Add performance-based adaptive routing | Medium–high |
| 7 | Add continuously adapting research workflows | High |

For the first practical test, I'd use one of your existing software repositories rather than starting a new project from scratch.

We could set up a supervisor that receives a broad objective, creates tasks, delegates implementation to Codex, verifies the results, and then decides what to tackle next.

I'd initially require human approval for major changes while allowing the team to operate autonomously on smaller tasks.

This would also give us the execution history needed to begin training a routing policy.

One important safeguard: for open-ended research or application development, I'd enforce limits on iteration count, compute usage, and lack of progress. An autonomous loop should be able to conclude that further work is unproductive, rather than consuming resources indefinitely.

For app-store releases, I'd additionally keep signing credentials and publication permissions behind explicit controls. If targeting Apple's App Store from Linux, you'll also need access to a macOS build/signing environment.

---

## My overall assessment

Paperclip looks increasingly well suited to your vision.

Having examined its documentation more closely, **I would now favor it over Tutti for your particular goals**.

The key reasons are its goal hierarchy, persistent organizational state, automatic delegation, reusable teams, and event-driven routines. Those are more useful for continuously evolving projects than a narrowly defined coding pipeline.

Its biggest missing capabilities for you are:

1.  **Intelligent resource allocation** across local models, Claude Max and ChatGPT Pro.
2.  **Reliable provider failover**, particularly when subscription quotas are exhausted.
3.  **Learning from outcomes** to improve model and workflow selection.
4.  **Deliberate strategic replanning**, so the team continuously reassesses its objectives instead of simply completing a static task list.

I would implement the first three in a shared controller and the fourth primarily through specialized supervisor agents, with programmatic safeguards.

The result would be something quite interesting: a reusable environment for autonomous software engineering and research, where the intelligence and resources assigned to each task adapt to experience.

**One thing I'd like to know before recommending your local model setup: what GPU do you have, and how much VRAM and system RAM?** That determines whether local models will be genuinely useful as coding agents or better limited to classification, extraction, and lightweight analysis.

**Confidence: High** regarding Paperclip's documented features and missing native fallback functionality. **Medium** regarding the effectiveness of the proposed adaptive system, which would need real-world evaluation.

### Prompt

One thing I could imagine to be useful to a lot of people is doing tasks first with an api or a bit too general of a model. But as you gather examples (successes or failures), you might be able to fine tune a local specific agent for a particular recurrent subset of a task. It could notify user that this might now be an option for a given recurrent task. Then if approved trains and evaluate the agent. Then this agent might be default for the task with fallback to more powerful general one if fails at one time or fails to often on task type. Is there anything that handles this ? Basically something that starts as a general setup (paperclip like), but whose objective is to tune as you go on to your usage, hardware etc. Might have several subprojects (math, coding, research etc.) Suppose I've been using codex (and don't have claude), but anthropic comes out with a great model and I switch subscriptions. It would be nice if there is a way to map codex models + thinking effort to claude model + thinking effort, with some adjustement period say from seeing how it goes. Is there already some alternative focusing on the research aspect ?

Is there any startup or open source idea that could arrise from that ? Say an open source paperclip adapter for dynamic usage (or could be a pull request, or a fork). Or for example a general white collar team replacement os that can do research, software etc. adapts as it goes. Or maybe something else.

### Response

# Self-improving AI agents: existing tools, research directions, and startup opportunities

I think you've identified something more interesting than another multi-agent orchestration platform.

What you're describing is an **AI operating system that progressively specializes itself to its owner**.

It would start with general-purpose agents—Claude, Codex, perhaps Gemini—and gradually develop an understanding of:

-   Which tasks you perform repeatedly.
-   Which models are best at each task.
-   Which reasoning-effort settings are sufficient.
-   Which tasks can be delegated to smaller local models.
-   When enough examples have accumulated to justify fine-tuning.
-   Whether a specialized agent actually outperforms the general one.
-   How to adapt when you change providers, hardware, or objectives.

And importantly, it would do this across multiple projects, without treating every project as a completely independent experiment.

**My initial finding: significant parts of this already exist, but I haven't found a mature open-source product that combines the entire lifecycle into a personalized, continuously improving agent platform.**

The closest technologies come from three different areas:

1.  **TensorZero, DSPy and LangMem:** systems that collect feedback and improve model behavior.
2.  **OpenPipe ART and Microsoft's Agent Lightning:** frameworks that actually train models to become better agents.
3.  **Paperclip and related orchestrators:** systems that manage projects, agents, tasks and execution.

The gap between these categories is potentially an interesting open-source project—and, with the right positioning, a startup.

The crucial distinction is that you're proposing something that **learns how to perform work**, not merely something that remembers previous conversations.

---

## 1\. The closest existing technologies

These are the projects I'd examine most seriously.

| Project | What it already does | What's missing from your vision |
| --- | --- | --- |
| **[TensorZero](https://github.com/tensorzero/tensorzero)** | Observability, feedback, evaluation, fine-tuning, model experiments and routing | Autonomous discovery of new specializations across projects |
| **[DSPy](https://github.com/stanfordnlp/dspy)** | Optimizes prompts, examples, and sometimes model weights against an evaluation metric | Managing your complete agent ecosystem |
| **[OpenPipe ART](https://github.com/OpenPipe/ART)** | Trains agents through reinforcement learning from task outcomes | Deciding autonomously when and what to train |
| **[Agent Lightning](https://github.com/microsoft/agent-lightning)** | Connects existing agents to reinforcement-learning infrastructure | Personalization, project management, adaptive deployment |
| **[LangMem](https://github.com/langchain-ai/langmem)** | Learns memories and improves prompts from interactions | Actual model fine-tuning and resource allocation |
| **[EvoAgentX](https://www.evoagentx.org/)** | Evolves and evaluates multi-agent workflows | Complete personal infrastructure and local-model specialization |
| **[RouteLLM](https://github.com/lm-sys/RouteLLM)** | Learns when cheaper models can replace stronger ones | Training new specialists and managing entire workflows |
| **[Paperclip](https://github.com/paperclipai/paperclip)** | Agent teams, projects, schedules, delegation and supervision | Continuous optimization of models and agent configurations |

### TensorZero: probably the closest architectural foundation

Of these, **TensorZero is the most important one for your idea**.

It describes itself as an open-source LLM infrastructure platform that combines:

-   A unified gateway for different models.
-   Collection of model inputs, outputs, and feedback.
-   Evaluation of model quality.
-   Automated prompt optimization.
-   Supervised fine-tuning.
-   Experimentation with alternative models and inference strategies.
-   A/B testing, retries, and fallbacks.

It even describes the process as a feedback-driven improvement cycle.

Its documentation explicitly supports collecting successful model interactions, using those examples to prepare fine-tuning datasets, and evaluating alternative implementations.

It includes integrations with hosted fine-tuning providers and recipes for local training using Axolotl, Torchtune and Unsloth.

That already covers a substantial portion of your proposal.

But TensorZero is primarily infrastructure for optimizing LLM-powered applications. It doesn't independently decide:

> I've observed that this particular user performs mathematical manuscript formatting 40 times a month. Their hardware could support a specialized local model. I'll propose training one, estimate the expected benefit, evaluate it, and integrate it into their existing agent team.

**That automatic discovery and deployment of specializations is the missing layer.**

### DSPy: learning without necessarily training model weights

DSPy is particularly relevant because it exposes an important principle:

**You shouldn't fine-tune a model until you've established that cheaper adaptation methods are insufficient.**

DSPy has optimizers such as GEPA and MIPROv2 that improve prompts and demonstrations using evaluation feedback. Its optimization framework also supports fine-tuning approaches.

It can start with surprisingly few examples. The documentation discusses optimizing programs using as few as five or ten training inputs in some cases.

Imagine your system discovers that you regularly ask an agent to extract mathematical definitions and propositions from LaTeX manuscripts.

An optimization sequence could be:

1.  Try a smaller existing model.
2.  Optimize its instructions.
3.  Give it selected examples of correct extractions.
4.  Evaluate it on previous manuscripts.
5.  Only consider fine-tuning if these methods are inadequate.

In many cases, the third step might get you most of the benefits without any training.

This is an important economic advantage.

### OpenPipe ART and Microsoft Agent Lightning: actual agent learning

These two are especially interesting for your ML background.

[OpenPipe ART](https://github.com/OpenPipe/ART) trains agents using reinforcement learning, notably GRPO, with support for locally trainable open-weight models.

It works with multi-step agent trajectories, rather than treating every task as a single input-output prediction.

[Microsoft Agent Lightning](https://github.com/microsoft/agent-lightning) goes further in its integration architecture: its current v1.0 uses an OpenAI-compatible gateway, a rollout controller and a trainer, allowing existing agent applications to participate in training without rewriting their execution loops.

Microsoft reports substantial improvements on SWE-bench Verified for particular Qwen configurations after agent training. Those are project-reported benchmark results, not evidence that equivalent gains are achievable on arbitrary personal tasks.

Consider an agent that repeatedly fixes a particular class of Python data-pipeline bugs.

Rather than training it to imitate entire Codex conversations, you could train it on the outcomes of interacting with a repository:

-   It receives an issue.
-   It searches the relevant files.
-   It proposes a patch.
-   The tests run.
-   It receives a reward based on correctness and regressions.
-   Its behavior is gradually improved.

This is much closer to teaching a specialized agent a skill than simply producing a smaller imitation of a general model.

The problem is that ART and Agent Lightning are **training frameworks**, not complete personal agent operating systems.

They don't automatically decide which recurrent activity should become a new specialist, or manage the transition from the general agent to the trained one.

### LangMem: a lighter form of continuous learning

LangMem is worth considering alongside training frameworks.

It can extract and consolidate memories from interactions, including asynchronously, and its prompt optimization features can modify an agent's behavior based on previous successes and failures.

This is sometimes called _procedural memory_: preserving what an agent has learned about how to perform tasks.

The significant difference is that LangMem generally changes memory and instructions, not the underlying model weights.

I'd use it as an intermediate adaptation layer.

A good system would support several levels of learning, rather than treating fine-tuning as the answer to every repeated problem.

---

## 2\. How your proposed automatic specialization should work

I would organize it as a **progressive specialization pipeline**.

### Stage A — Discover recurrent task categories

Every completed task produces a record:

```yaml
yamltask:
  project: coopain
  category: backend-validation

execution:
  provider: openai
  model: codex
  effort: medium
  duration_seconds: 92

evaluation:
  tests_passed: true
  review_passed: true
  human_correction: false

resources:
  estimated_tokens: 8500
```

Across projects, the system can cluster similar tasks.

For example:

```text
text420 completed tasks
       │
       ▼
Task clustering
       │
       ├── 120 backend validation tasks
       ├── 85 code review tasks
       ├── 75 data extraction tasks
       ├── 65 research exploration tasks
       └── 75 miscellaneous tasks
```

But frequency alone isn't sufficient.

The system should also estimate:

-   How similar the tasks are.
-   Whether their outputs are objectively verifiable.
-   Whether a smaller model can handle them.
-   Whether the workload is stable enough for specialization.
-   Whether the expected savings justify training and maintenance.

You might perform 100 different research tasks without there being a useful common specialization.

Conversely, performing a structured extraction task only 20 times could be enough to justify a simple dedicated classifier.

### Stage B — Identify a specialization candidate

The system notices that backend validation tasks are frequent and follow a relatively predictable pattern.

It estimates:

> A small local model might handle 80% of these tasks. We have sufficient examples for initial evaluation and suitable hardware.

It generates a proposal:

**Potential optimization: Backend validation specialist**

| Property | Estimate |
| --- | --- |
| Existing model | Codex Medium |
| Proposed model | Local 8B |
| Historical examples | 120 |
| Expected success rate | To be measured |
| Training required | Possibly |
| Existing fallback | Codex Medium |
| Approval | Required |

I would deliberately distinguish _theoretical predicted savings_ from _measured savings_. Before benchmarking, the system does not know whether the local model will be suitable.

### Stage C — Optimize before fine-tuning

I'd make adaptation progressively more expensive:

| Level | Technique | Example |
| --- | --- | --- |
| 0 | No adaptation | Existing small local model |
| 1 | Instructions and rules | Improved task-specific prompt |
| 2 | Examples and retrieval | Relevant successful cases inserted into context |
| 3 | Skills and tools | Dedicated scripts, validators and workflows |
| 4 | Supervised fine-tuning | Task-specific LoRA adapter |
| 5 | Reinforcement learning | Improve behavior using task outcomes |
| 6 | Custom workflow | Specialized model plus supporting tools and verification |

Levels 1–3 are often much easier to maintain than fine-tuned weights.

This is especially true as new foundation models become available.

A task-specific prompt or tool can often be transferred to a new model immediately. A LoRA adapter generally cannot be transferred between unrelated base-model architectures.

### Stage D — Evaluate and deploy

Once the specialization is ready, the system should use a held-out test set that wasn't used for optimization.

Suppose it produces these **illustrative** results:

| Metric | Codex Medium | Local specialist |
| --- | --- | --- |
| Task completion | 98% | 91% |
| Average execution time | 110 s | 24 s |
| Requires escalation | — | 9% |
| Human correction | 1% | 3% |

The decision shouldn't simply be that the local model is cheaper.

It should depend on the risk and consequence of its mistakes.

For low-risk work, 91% success followed by reliable fallback may be perfectly acceptable.

For something like database migrations or security-sensitive code, it probably isn't.

I would introduce the model gradually:

**Offline benchmark → Shadow evaluation → Limited rollout → Default for eligible tasks.**

A shadow evaluation means the local specialist runs alongside the existing agent without controlling the result.

During limited rollout, the system assigns it selected low-risk tasks and verifies the outcomes.

If performance deteriorates, it automatically returns to the previous agent.

### Stage E — Continuous improvement

The newly trained agent would not be considered finished.

It continues accumulating data about:

-   Tasks it completes correctly.
-   Tasks requiring escalation.
-   Cases outside its specialization.
-   Regressions after updates.
-   Changes in user preferences.
-   Performance relative to newly available models.

A significant distribution shift would trigger reevaluation.

The system might eventually decide that a new off-the-shelf model is better than its custom fine-tuned model.

**That would count as successful optimization too.**

The ultimate objective is not to create the largest number of personalized models. It's to perform your tasks reliably with the most appropriate resources.

---

## 3\. One significant obstacle: model-provider terms

There is a legal and commercial complication in your proposal that is easy to overlook.

**Collecting the results of Claude or Codex sessions and using them to train a local replacement model is not always permitted.**

OpenAI's current European consumer terms prohibit using outputs to develop models that compete with OpenAI. They also restrict automated extraction of outputs.

Anthropic's March 2026 guidance makes a distinction between specialized tools, such as classifiers and extraction systems, and models that compete with Claude. It permits certain specialized training uses but restricts general-purpose model training and use of outputs as training targets.

That distinction would matter enormously to a startup selling automatic distillation.

Fortunately, **your system doesn't necessarily need to train on proprietary model outputs**.

Consider three approaches:

**A. Learn model-selection policies.** Record task categories, execution time, test outcomes and user satisfaction, then train a router. No need to reproduce the proprietary model's answers.

**B. Train local models using independently obtained ground truth.** For coding, this might include your own specifications, permissively licensed training examples, executable tests, and independently verified results. For mathematics, it might include formally verified statements or appropriately licensed corpora.

**C. Use task-outcome rewards.** A local agent attempts a task and receives feedback from an independent environment, such as a test suite, compiler or game simulator.

Approach C is particularly attractive for reinforcement learning, although it requires a reliable reward function and careful protection against reward hacking.

This is one reason I would build the training layer around **verified outcomes and provenance-aware datasets**, rather than indiscriminately harvesting agent conversations.

For a commercial product, you'd want the system to track where every training example came from, its permitted uses, and which models can legally be trained on it.

---

## 4\. Switching from Codex to Claude without losing what the system has learned

I think this could be a genuinely useful standalone feature.

Suppose you've used Codex for six months.

Your system has learned that the following configuration performs well:

| Task category | Current configuration | Observed success |
| --- | --- | --- |
| Simple bug fixes | Codex Low | 96% |
| Backend development | Codex Medium | 93% |
| Architecture | Codex High | 90% |
| Mathematical exploration | Codex High | 78% |

_Illustrative results._

You cancel ChatGPT Pro and switch to Claude Max.

Ideally, your agent system should transfer everything it can, rather than forcing you to start again.

### The solution: model-independent task profiles

Instead of storing:

```yaml
yamlmodel: codex
effort: high
```

I'd make the primary abstraction something like:

```yaml
yamltask_profile:
  type: architecture-design

  requirements:
    reasoning_depth: substantial
    tools: [filesystem, shell, git]
    context: large

  evaluation:
    - architectural_consistency
    - integration_tests
    - independent_review

  routing:
    objective: maximize_quality
    candidates:
      - codex-high
      - claude-opus-high
```

The important thing is that **the task and its success criteria remain constant even when models change**.

The old provider's performance records become the baseline for evaluating the new provider.

### There should be no fixed effort-level conversion

For example, assuming:

`Codex High = Claude Opus High`

would be an unjustified simplification.

Reasoning-effort labels aren't standardized across providers. The amount of computation represented by _medium_ can vary by model family, and quality gains need not be monotonic for every task.

I would instead conduct an automatic calibration experiment.

Suppose the system samples 30 representative backend tasks from its historical benchmark collection.

It evaluates:

| Candidate | Success rate | Relative time |
| --- | --- | --- |
| Codex Medium | 93% | 1.0× |
| Claude Sonnet Medium | 90% | 0.7× |
| Claude Opus Medium | 95% | 1.2× |
| Claude Opus High | 97% | 2.0× |

_Hypothetical results, not real model benchmarks._

It could conclude that Opus Medium is a reasonable replacement for Codex Medium, while retaining Opus High for particularly difficult cases.

But with only 30 examples, those differences would be statistically uncertain. The system should treat the recommendation as provisional and continue collecting evidence.

### The adjustment period

I'd use a sequence resembling:

**Historical benchmark → Calibration → Cautious deployment → Online evaluation → Stable routing policy.**

When both subscriptions are temporarily available, the system can run selected tasks on both providers to obtain paired comparisons.

If you've already canceled Codex, it can still compare Claude against stored task outcomes and executable benchmarks, although it loses the ability to run fresh head-to-head comparisons.

The system should also detect _negative transfer_: instructions and workflows optimized for Codex may work poorly with Claude.

A model switch might therefore trigger prompt reoptimization using DSPy or LangMem.

This gives you something much more valuable than a simple model-name substitution: **portability of the accumulated knowledge about how your work gets done**.

There is already some adjacent functionality. For example, Mastra introduced a `ModelSelectionProcessor` in September 2026 that selects models using a classifier and supports fallbacks. But that is not the complete longitudinal calibration and specialization process we're discussing.

---

## 5\. Existing projects focusing on autonomous research

There is another group of projects I'd investigate, because they focus on something Paperclip doesn't specialize in: **exploration, experimentation and learning from failed hypotheses**.

### AIDE ML — especially relevant to your Kaggle work

**[GitHub: WecoAI/aideml](https://github.com/WecoAI/aideml)**

AIDE is an open-source machine-learning engineering agent that uses tree search to improve code.

It repeatedly develops solutions, executes them, measures performance, and decides what to try next.

Unlike a simple agent loop, it maintains a tree of attempted solutions. This enables it to explore different approaches instead of always modifying its latest answer.

It supports OpenAI, Anthropic, Gemini and OpenAI-compatible local models. Its developers also offer a commercial product, Weco.

For your Kaggle workflows, I would investigate AIDE before trying to reproduce this functionality with generic Paperclip agents.

### Karpathy's autoresearch — a particularly elegant design

**[GitHub: karpathy/autoresearch](https://github.com/karpathy/autoresearch)**

Released in March 2026, this project implements a remarkably simple autonomous research loop.

An agent receives an LLM training environment, changes the training code, executes an experiment, measures validation loss, and decides whether to retain the change.

Each experiment uses a fixed five-minute training budget.

The system can repeat this overnight, accumulating experimentally validated improvements.

What's interesting is its deliberately limited scope: the agent can modify the training code, but not the evaluation machinery.

That protects against some forms of reward hacking.

I would study this carefully because it illustrates how **a relatively simple, well-defined feedback loop can outperform elaborate agent organizations for measurable optimization problems**.

Its limitations also highlight opportunities: richer experiment histories, adaptive search strategies, parallel workers and learning from previous failed experiments.

### Sakana AI's AI Scientist v2

**[GitHub: SakanaAI/AI-Scientist-v2](https://github.com/SakanaAI/AI-Scientist-v2)**

This is closer to your open-ended scientific research vision.

It can generate hypotheses, design experiments, implement and execute them, analyze results, and prepare scientific manuscripts.

Version 2 introduces an agentic tree-search system guided by an experiment manager.

The authors explicitly note that this more exploratory architecture can have lower success rates than a template-based system when the problem is already well defined.

That is a useful warning against assuming that more autonomy always means better research.

For mathematical research, you'd need additional machinery for rigorous proof verification, counterexample management and distinguishing conjectures from established theorems.

### EvoAgentX — closest to self-evolving orchestration

**[EvoAgentX](https://www.evoagentx.org/)**

This project is worth investigating because it explicitly targets _self-evolving multi-agent systems_.

Rather than only improving a model's responses, it attempts to improve the structure of agent workflows themselves through evaluation and optimization.

That is conceptually very close to your proposal.

It makes the system architecture an optimization target:

-   Which agents should exist?
-   How should tasks be decomposed?
-   Which agents should collaborate?
-   Which workflows should be replaced?
-   When is a multi-agent process unnecessary?

EvoAgentX is a research-oriented framework rather than an integrated personal workspace.

I would consider it a potentially useful source of algorithms, not necessarily the platform on which I'd manage all your projects.

### Which I would use for each kind of work

| Area | Starting point |
| --- | --- |
| General autonomous projects | Paperclip |
| Learning agent behavior | ART / Agent Lightning |
| Prompt and skill optimization | DSPy / LangMem |
| Model evaluation and experiments | TensorZero |
| Kaggle competitions | AIDE ML |
| ML training research | autoresearch |
| Open-ended scientific research | AI Scientist v2 |
| Self-evolving workflows | EvoAgentX |

My preference would be to make these systems interoperable rather than adopt one monolithic framework that tries to implement everything.

---

# 6\. Startup and open-source opportunities

I see four distinct opportunities. They overlap, but they have different risk profiles and potential markets.

## Idea A — An adaptive model controller for Paperclip

**Best initial open-source project.**

Build a Paperclip extension that automatically selects models, effort levels and execution strategies.

Imagine configuring an agent using:

```yaml
yamlagent:
  role: coding

  optimization:
    objective: quality_per_resource
    adaptive: true

  providers:
    - claude
    - codex
    - ollama

  capabilities:
    local_training: true
    automatic_fallback: true
    learn_from_outcomes: true

  approval:
    new_fine_tuning_job: required
    model_downgrade: optional
```

The extension would observe executions and learn which configurations are most effective.

Eventually, you could configure the system by describing its objectives rather than selecting individual models.

### Technical design

I would distinguish the **execution adapter** from the **optimization controller**.

Paperclip already has a documented API for external adapters, which can execute agents and capture usage information. It also has a plugin SDK supporting background workers, jobs, events and dashboard extensions.

That means your feature can likely be developed as an external plugin with a routing adapter, without forking Paperclip itself. The plugin SDK is currently in alpha, so API changes are a realistic maintenance concern.

The core might look like this:

```text
text                Paperclip
                    │
                    ▼
              Task received
                    │
                    ▼
             Adaptive Router
                    │
         ┌──────────┴──────────┐
         │                     │
   Model registry       Performance database
         │                     │
         └──────────┬──────────┘
                    │
                    ▼
              Select agent
                    │
             Execute & verify
                    │
                    ▼
              Record outcome
                    │
                    ▼
             Update estimates
```

An initial version could use manually specified performance statistics and simple rules.

A later version could implement a contextual bandit, where the context includes task category, difficulty, project, available hardware, subscription quotas and prior failures.

It would need to balance exploring unfamiliar models with exploiting configurations already known to work.

### Could this be merged into Paperclip?

Quite possibly.

But I would begin as an independent plugin because it allows experimentation without needing upstream approval for every architectural decision.

Once the design is stable, you could contribute generic components to Paperclip.

The adaptive controller could also support other orchestrators later.

**Startup potential:** Moderate as a standalone business; strong as an open-source project.

The difficulty is differentiation. Basic model routing is increasingly commoditized, and major orchestration frameworks could implement it themselves.

The more sophisticated evaluation and specialization features are where the opportunity becomes interesting.

---

## Idea B — An automatic specialist-agent factory

**My favorite technically distinctive idea.**

This is the feature you've described that I find least adequately addressed by current products.

Call it, provisionally, **Agent Foundry**.

Its responsibility isn't to run all your projects. Instead, it observes agent activity and decides whether recurrent workloads could be performed better by specialized agents.

Its workflow:

```text
textObserve work
     ↓
Identify repeated task types
     ↓
Estimate specialization opportunity
     ↓
Benchmark existing smaller models
     ↓
Try prompt/skill optimization
     ↓
Fine-tuning worthwhile?
     │
     ├── No → Deploy simpler solution
     │
     └── Yes
           ↓
      Request approval
           ↓
      Prepare training data
           ↓
      Train specialist
           ↓
      Evaluate
           ↓
      Gradual deployment
           ↓
      Monitor and update
```

It would also periodically ask whether existing specialists should be retired.

For example, if a new open-weight model outperforms three separately trained specialists, perhaps maintaining those specialists is no longer justified.

### Why this could be valuable

Most fine-tuning platforms assume that the user already knows which model they want to train and has an appropriate dataset.

Your proposal reverses the process.

**The system discovers when fine-tuning might be useful.**

That is an important difference in the user experience.

You don't ask:

> How do I fine-tune a model for this workflow?

Instead, the system asks:

> I've identified a recurring workflow that might benefit from specialization. Would you like me to evaluate that possibility?

### Business model

A plausible commercial version would offer automatic specialization discovery, training-data preparation, evaluations, deployment and ongoing monitoring.

The open-source version could work entirely with local resources.

A hosted version could provide managed training infrastructure and enterprise integrations.

Customers would pay for measurable improvements in reliability, latency, privacy or operating cost.

### The difficulty

It's relatively easy to identify that tasks are similar.

It's considerably harder to determine whether they share a learnable skill.

For example, 100 software bugs all concern Python, but may require entirely different reasoning.

Fine-tuning an 8B model on those examples might have little benefit.

I'd initially target narrow operations with objective evaluations: document extraction, code transformations, data validation, repetitive tool use and domain-specific classification.

**Startup potential:** Promising, but the main risk is demonstrating repeatable improvements that justify training and maintenance costs.

---

## Idea C — Model portability and automatic recalibration

This one could be especially appealing to developers using multiple providers.

Its premise is simple:

**Your agent's accumulated competence should belong to you, not to your model provider.**

The system would maintain provider-independent records of:

-   Tasks and requirements.
-   Tool permissions and capabilities.
-   Evaluation datasets.
-   Performance histories.
-   Optimized prompts and skills.
-   Specialized workflows.
-   Model configuration comparisons.

You could then replace Claude with Codex, switch to local models, or adopt a newly released provider.

The controller would automatically benchmark and recalibrate the system.

### Business opportunity

This could become an independent infrastructure component for enterprises that want to avoid provider lock-in.

The challenge is that portability alone may not justify a large subscription.

I would probably combine it with adaptive routing and evaluation.

**Startup potential:** Moderate independently, potentially strong as part of enterprise agent infrastructure.

---

## Idea D — A self-improving research operating system

**Most ambitious, and probably the most interesting from a research perspective.**

Your phrase _white-collar team replacement OS_ captures the broad ambition, but I would initially focus on a much narrower market.

For example:

> An autonomous ML research environment that develops hypotheses, executes experiments, learns from results, and progressively improves both its research strategy and its underlying agents.

It would combine two interacting optimization loops.

### Inner loop: improve the research

```text
textHypothesis
   ↓
Experiment
   ↓
Observation
   ↓
Analysis
   ↓
New hypothesis
```

### Outer loop: improve the researcher

```text
textAnalyze previous research attempts
   ↓
Identify ineffective strategies
   ↓
Improve agent prompts, models or workflows
   ↓
Evaluate research performance
   ↓
Deploy improvements
```

The distinction is important.

In the inner loop, the system tries to discover something about the world.

In the outer loop, it tries to become better at discovery.

For a Kaggle competition, the outer loop might learn that certain approaches to feature engineering consistently produce poor results for a particular dataset family.

It could modify how it generates future research hypotheses.

For mathematics, it might discover that numerical experiments are particularly effective at generating conjectures in one area, but that certain proof strategies repeatedly fail.

It could prioritize different exploratory approaches accordingly.

### The difficult part: measuring research quality

Software agents have tests.

Kaggle agents have evaluation scores.

Optimization agents have objective functions.

But genuinely open-ended research often has no simple scalar reward.

You don't necessarily know whether an investigation was valuable until much later.

A system that rewards the number of experiments completed will optimize for doing experiments.

A system that rewards the number of plausible conjectures will generate conjectures.

Neither necessarily produces meaningful scientific progress.

A serious research OS needs a more sophisticated representation of progress: verified results, reduction of uncertainty, falsified hypotheses, informative experiments, reproducibility and human judgments of significance.

This could be an interesting research project in its own right.

**Startup potential:** High theoretical upside, but very high technical and commercialization risk.

---

# 7\. Which ideas could develop a real competitive advantage?

This is where I'd distinguish an impressive project from a defensible company.

Building another dashboard for Claude and Codex is unlikely to be enough.

Nor is implementing basic automatic routing, since model providers and existing infrastructure platforms can reproduce that functionality.

I see three more promising sources of differentiation.

### A. A growing library of verified task evaluations

Imagine a platform that accumulates thousands of domain-specific evaluation tasks with reliable ground truth.

Not just generic benchmarks, but realistic workflows involving databases, software projects, research environments and business processes.

This creates a reusable foundation for evaluating new models and training specialized agents.

The data can become a competitive advantage, provided it is legally obtained and sufficiently differentiated.

### B. A library of optimized specialist workflows

Over time, your platform might develop reusable, evaluated workflows for:

-   Software maintenance.
-   ML experiment management.
-   Research-paper analysis.
-   Data-pipeline debugging.
-   Scientific computation.

The value isn't necessarily in the fine-tuned weights.

It may be in the combination of instructions, tools, test cases, resource policies and learned failure modes.

A workflow that has been validated across hundreds of realistic tasks is considerably more valuable than a generic agent prompt.

### C. Integration into real organizations

An enterprise agent system becomes more valuable as it learns the organization's procedures and integrates into its workflows.

However, that also makes privacy, security and auditability essential.

A customer is unlikely to accept a black-box agent that autonomously changes models, trains on confidential material and deploys modifications without adequate controls.

The system would need permission boundaries, dataset provenance, reproducible evaluation, and clear rollback mechanisms.

This is potentially a stronger business than selling access to individual fine-tuned models.

---

# 8\. What I'd build first

Given your ML engineering background and interest in agentic systems, I would **not start by building a complete alternative to Paperclip**.

That's an enormous amount of infrastructure to develop before validating the distinctive part of your idea.

I'd build an independent adaptive-optimization engine that can eventually integrate with Paperclip, LangGraph, OpenCode and other systems.

My proposed progression would be:

| Phase | Deliverable | What it proves |
| --- | --- | --- |
| 1 | Execution recorder and task classifier | Can we recognize meaningful recurring tasks? |
| 2 | Model/effort benchmarking | Can we reliably predict appropriate configurations? |
| 3 | Adaptive routing and failover | Can we improve quality per unit of resource use? |
| 4 | Automatic prompt/skill optimization | Can agents improve without weight training? |
| 5 | Specialization opportunity detector | Can we predict when fine-tuning is worthwhile? |
| 6 | Local specialist training and evaluation | Can specialization produce measurable gains? |
| 7 | Autonomous promotion and rollback | Can the system safely improve over time? |
| 8 | Integration with Paperclip | Does it work within a real agent organization? |

### The first meaningful experiment

I would select two substantially different workloads.

**Experiment A: Software engineering.** Use an existing repository with a reasonably strong automated test suite. Compare local models, Codex and Claude across bug fixes, tests, refactoring and code review.

**Experiment B: ML experimentation.** Use a controlled machine-learning benchmark with reproducible training and evaluation. Compare different approaches to generating and executing experiments.

For both workloads, collect trajectories, outcomes, durations, resource consumption and failures.

Then attempt to build a routing policy that outperforms static model selection.

This would establish whether your optimization concept actually works before introducing fine-tuning.

Afterward, identify one narrow, recurrent task where training a specialist is plausible.

Run the full specialization pipeline and measure whether it improves the overall system.

### An architectural principle I'd preserve

I would keep these components independent:

```text
text                 USER / ORGANIZATION
                          │
                   ORCHESTRATOR
                    (Paperclip)
                          │
                          ▼
                 ADAPTIVE CONTROLLER
                          │
          ┌───────────────┼────────────────┐
          │               │                │
      Model Router    Skill Optimizer   Agent Trainer
          │               │                │
          └───────────────┼────────────────┘
                          │
                    EVALUATION
                          │
                          ▼
                 PERFORMANCE MEMORY
                          │
                          └──── Feedback
```

This separation is important because it makes the project useful independently of Paperclip.

It also prevents fine-tuning from becoming tightly coupled to a particular orchestration framework.

---

# 9\. My assessment of the startup potential

I'd rank the opportunities this way:

| Idea | Technical feasibility | Commercial potential | My preference |
| --- | --- | --- | --- |
| Paperclip adaptive routing plugin | High | Medium | Best initial OSS contribution |
| Automatic specialist-agent factory | Medium | Medium–high | **Best distinctive product idea** |
| Provider-portable agent optimization | High | Medium | Excellent supporting feature |
| Self-improving ML research OS | Medium–low | Potentially high | Best research-focused venture |
| General white-collar replacement OS | Low initially | Potentially enormous | Too broad for an initial product |

These are qualitative assessments, not estimates derived from market-size or customer-demand studies.

One commercial point is worth emphasizing: **fine-tuning can be surprisingly uneconomic for individual users**.

If you're already paying for Claude Max and ChatGPT Pro, reducing your consumption doesn't directly save money until it allows you to downgrade or cancel a subscription, avoid extra usage purchases, or achieve more work within your limits.

Local inference also consumes hardware resources, electricity and maintenance time.

For a business processing millions of requests, the economics can be very different.

Consequently, I would optimize for _task quality, execution capacity and control_ as well as cost.

The most valuable result might be an agent that completes repetitive work locally, protects sensitive information and frees up your Claude usage for genuinely difficult tasks.

---

## 10\. My preferred direction

I would combine ideas B and C:

### **An open-source system that learns which agents you need, then builds and maintains them.**

Its central promise would be:

> Start with the models you already have. The system learns from your workflows, identifies opportunities for specialization, and progressively improves your agent setup—while remaining portable across models and providers.

It would begin by optimizing routing, instructions and tools.

As enough reliable data accumulated, it could propose fine-tuning.

When a better model became available, it would reevaluate its existing specialists.

When your hardware changed, it would reconsider which tasks could run locally.

And when you started a new project, it would reuse the relevant knowledge without indiscriminately mixing confidential data or project-specific assumptions.

For the open-source project, I'd make **Paperclip integration the first demonstration**, rather than a hard dependency.

For the eventual startup, I'd initially target **ML engineering teams or software engineering organizations**, because their work produces comparatively measurable outcomes.

I would not market it as a general white-collar replacement system until it had demonstrated reliable autonomous improvement in narrower domains.

### The underlying research question

There is a deeper and potentially publishable question here:

**Can a general-purpose agent system autonomously discover useful specializations and optimize its own model, tool and workflow configuration using experience from heterogeneous tasks?**

That combines several research problems:

-   Online task clustering and skill discovery.
-   Contextual bandits and resource-constrained routing.
-   Transfer learning and continual learning.
-   Automatic reward and evaluation construction.
-   Selective prediction and abstention.
-   Multi-objective optimization.
-   Meta-learning across projects and model families.

The most difficult part may not be training the specialist models.

It may be knowing **when a specialization is sufficiently reliable to deploy**, and when a new general model has made it obsolete.

That's the component I'd want to investigate experimentally.

---

### My conclusion

I think there's a genuine opportunity here, but not in creating another agent framework.

Paperclip, TensorZero, DSPy, Agent Lightning and the autonomous research projects already provide many of the necessary building blocks.

What I haven't identified is a mature system that autonomously connects all of them around a user's evolving workloads.

**The strongest idea is an adaptive learning layer for agent systems: one that treats every completed task as evidence about how future tasks should be handled.**

I'd begin with a model-agnostic evaluation and routing engine, add automated specialization discovery, and only then integrate fine-tuning.

That gives you an incremental open-source project with useful standalone capabilities, a credible ML research agenda, and a potential path toward a commercial product.

**Confidence:** High on the capabilities of the cited existing projects and provider restrictions; medium on the identified market gap; medium-low on the commercial upside, which needs customer validation and empirical evidence that adaptation delivers sustained improvements.

### Prompt

I guess you can achieve something by plugging a bunch of tools together and adapting it. But less out of the box. Harder to maintain. Needs in depth knowledge of the ecosystem. For example dataiku doesn't do anything new, it adds a nice ui, some automation, the possibility of having it tuned to your organization etc. I think dataiku is too high capture and I don't like it, but they do have this out of the box aspect. Maybe something in the middleground. Or could be opensource option, but out of the box with cloud solution is paid (kinda like mlflow etc. does). We wouldn't recode everything. Just use existing tools and plug them together to have a seemless tool. Also could use mistral where grdp eu compliance matters, codex or claude when not etc. You could imagine this way having just one employee tasked with maintaining, choosing providers if needed, validate or not to escalate personalized agent with the next level of training. Instead of a whole team. Other employees would ineract with the inbox, or do their thing and system learn from it so the next time they do their thing it works better. I like the tree search idea and might be used in our os for the os development itself as well as for tasks the os is used for. Different companies / people may have very different usage. Perhaps could have some plugin aspect for math, finance / automated trading strategy research, software development etc. ?

(these small local models aren't aimed at competing with these large labs, so probably fine. But you are true to be careful)

### Response

# An adaptive AI operating system for individuals and organizations

I think this is a more compelling product direction than the Paperclip plugin we were discussing earlier.

Your Dataiku comparison is particularly relevant. **The innovation doesn't necessarily need to be a new algorithm or agent framework. It can be making a collection of powerful technologies accessible, reliable, interoperable, and progressively better adapted to their users.**

There are two parts to the opportunity:

1.  **Make autonomous AI teams usable out of the box**, without requiring someone who understands Paperclip, TensorZero, DSPy, LangGraph, Ollama, fine-tuning, model gateways, and half a dozen other technologies.
2.  **Make those teams progressively self-improving**, so organizations don't need a full-time AI engineer continually optimizing prompts, workflows, models and training datasets.

I would position the product somewhere between **Paperclip, Dataiku, and a self-improving AI research platform**.

The key product promise could be:

> **An AI workforce that adapts to how you work.**
> 
> Start with ready-made agents. Connect your tools and choose your objectives. The system learns which tasks to automate, which models work best, and when specialized agents are worth developing.

Crucially, _adapts_ should mean demonstrably better performance, not simply remembering user preferences.

## 1\. There is a market gap, but it's narrower than it initially appears

A useful reality check: Dataiku is already moving toward several things we've discussed.

Its current [Agent Hub](https://www.dataiku.com/product/agent-hub) offers centralized agent creation, orchestration, monitoring, approvals and reusable components. Its [LLM Mesh](https://www.dataiku.com/product/llm-mesh) supports provider switching, performance routing, governance and self-hosted models. It also manages agents developed in other platforms.

So merely combining different model providers in an enterprise dashboard isn't enough differentiation.

But consider the difference between these two products.

**Traditional enterprise AI platform:**

> Here are the tools to create, deploy, evaluate and maintain your AI agents.

**Your proposed adaptive AI OS:**

> Tell me what your organization does. I'll recommend and configure suitable agents, observe their performance, suggest improvements, and automatically maintain the approved configurations.

The first gives users powerful tools. The second tries to reduce the amount of expertise required to use those tools effectively.

That difference could be quite valuable.

It also changes the business model. You're not primarily selling an agent builder. You're selling **a continuously managed capability**.

---

## 2\. I would design it around three types of users

### The AI administrator

This is the person you imagine eventually being the only dedicated AI specialist in a small company.

They control the organization's AI infrastructure:

-   Choose which model providers are permitted.
-   Configure privacy and data residency policies.
-   Approve new specialized models or training jobs.
-   Monitor agent quality, usage, costs and failures.
-   Decide how much autonomy different agents have.
-   Install specialist workflow packages.
-   Approve significant changes to the organization's AI configuration.

Importantly, they shouldn't have to write code or understand the details of model training.

For example, they might receive:

**Optimization opportunity detected**

> The accounting-document classification agent has processed 3,200 documents over the past month.
> 
> A smaller European-hosted model appears capable of handling most of these tasks.
> 
> The system recommends benchmarking it against the current model, with an option to fine-tune if necessary.
> 
> Estimated monthly savings: to be determined through evaluation.

The administrator can approve an experiment without needing to know how to use Unsloth, LoRA, or DSPy.

### The ordinary employee

This person shouldn't need to understand models or agents at all.

They work through a familiar interface: an inbox, chat, project workspace, document editor, or existing business application.

They might:

-   Ask an agent to prepare a report.
-   Review and correct an automatically prepared document.
-   Delegate a repetitive task.
-   Respond to an agent's request for clarification.
-   Continue working while unrelated agents execute independently.

Their corrections can become useful feedback.

For example, an employee repeatedly corrects the same type of mistake in a monthly report. The system recognizes the pattern and proposes improving the corresponding agent.

**The important distinction is that employees teach the system through normal work, without needing to become AI trainers.**

That could be a strong selling point.

### The individual power user or researcher

This is the user who wants considerably more control.

They might have several projects:

-   A software application being developed autonomously.
-   A Kaggle competition with continuously evolving experiments.
-   A mathematical research project.
-   A personal automation workflow.
-   An algorithmic trading research environment.

They can select different agent teams, model policies, evaluation methods, and levels of autonomy for each project.

I'd make this the first target audience for the open-source version, because technically sophisticated users can help establish whether the underlying adaptive system genuinely works.

---

## 3\. What I'd build, and what I'd reuse

For the first version, I wouldn't write a new model gateway, inference engine, fine-tuning framework, or general-purpose agent executor.

I'd build a **unified control plane and adaptive optimization layer** around existing components.

An initial architecture might be:

```text
text                    ORGANIZATION
                         │
               ┌─────────▼─────────┐
               │     AI OS UI      │
               │                   │
               │ Projects          │
               │ Employee inboxes  │
               │ Agent teams       │
               │ Approvals         │
               │ Performance       │
               └─────────┬─────────┘
                         │
              ┌──────────▼──────────┐
              │  ADAPTIVE CONTROL   │
              │                     │
              │ Workflow selection  │
              │ Model routing       │
              │ Skill discovery     │
              │ Continuous learning │
              │ Human escalation    │
              └──────────┬──────────┘
                         │
           ┌─────────────┼─────────────┐
           │             │             │
      AGENT TEAMS    EVALUATION     TRAINING
           │             │             │
       Paperclip       Langfuse      Unsloth
       LangGraph       Benchmarks    Agent Lightning
           │             │             │
           └─────────────┼─────────────┘
                         │
                 MODEL PROVIDERS
                         │
             ┌───────────┼───────────┐
             │           │           │
          OpenAI      Anthropic    Mistral
                                     │
                                 Local LLMs
```

This is a logical architecture, not a recommendation to deploy every component at once.

### Existing technologies I'd consider

| Component | Existing technology | Approach |
| --- | --- | --- |
| Agent teams and project goals | [Paperclip](https://github.com/paperclipai/paperclip) | Integrate, not rewrite |
| Stateful agent workflows | [LangGraph](https://github.com/langchain-ai/langgraph) | Use for specialized workflows |
| Durable long-running execution | [Temporal](https://temporal.io/) | Introduce when required |
| Provider routing and failover | [LiteLLM](https://github.com/BerriAI/litellm) | Use existing gateway |
| Execution tracing and evaluations | [Langfuse](https://github.com/langfuse/langfuse) | Integrate |
| Local inference | Ollama / vLLM | Integrate |
| Fine-tuning | [Unsloth](https://github.com/unslothai/unsloth) | Invoke as training backend |
| Agent reinforcement learning | [Agent Lightning](https://github.com/microsoft/agent-lightning) | Optional advanced backend |
| Research tree search | [AIDE](https://github.com/WecoAI/aideml) | Reuse concepts or integrate |
| User interface and adaptation logic | **Our own product** | Main development effort |

Langfuse already offers tracing, evaluation datasets, human feedback and experiment management. LiteLLM has routing, fallback and cooldown mechanisms. Temporal supports workflows that can survive interruptions and wait for human decisions. These are precisely the kinds of infrastructure that shouldn't be reinvented.

There is also an interesting alternative to Paperclip: **[Dify](https://github.com/langgenius/dify)**. It already has a graphical workflow builder, model integrations, agent execution, a plugin marketplace and human-in-the-loop functionality.

Dify may actually be a better base for ordinary employees, whereas Paperclip is closer to your vision of persistent autonomous teams working toward long-term goals.

I would prototype with both before committing to either. A company building a product on top of these frameworks becomes dependent on their architectural decisions.

**One important finding from my latest research:** TensorZero, which I previously suggested as a particularly relevant foundation, has had its GitHub repository archived since June 12, 2026. Although its architecture remains interesting, I would no longer select it as a central dependency without investigating its maintenance and commercial status.

### The real development work

Even after integrating existing frameworks, four components would need substantial original engineering:

1.  **A unified data model:** tasks, projects, agents, users, decisions, evaluations, capabilities and permissions.
2.  **An adaptive controller:** selecting workflows, models, reasoning effort and training opportunities.
3.  **A user-friendly experience:** setup, monitoring, approvals, explanations and configuration.
4.  **A portable plugin specification:** allowing domain-specific workflows to be installed without modifying the core.

That's already a serious software product, but much more manageable than rebuilding all the underlying AI infrastructure.

---

## 4\. Model selection should be constrained by policy before intelligence

Your Mistral example is a good illustration of something I'd build into the system from the beginning.

Suppose an organization uses three kinds of data:

| Data classification | Permitted execution |
| --- | --- |
| Public | Any approved cloud or local provider |
| Internal confidential | Approved providers with appropriate contracts and controls |
| EU-restricted personal data | Only specifically approved deployments satisfying the organization's data policies |
| Highly sensitive | On-premises inference, if required by policy |

The controller first determines **which providers are eligible**, and only then optimizes quality, cost and performance.

For example:

```yaml
yamltask:
  type: document_extraction

  data_policy:
    classification: restricted_eu
    permitted_destinations:
      - approved_eu_hosted
      - on_premises

  optimization:
    priority: reliability
    allow_local_specialist: true

  fallback:
    preserve_data_policy: true
```

If a task uses restricted data and its preferred local model fails, the system must not silently retry through an unauthorized US-hosted endpoint.

Even if the alternative model is demonstrably better.

Mistral is an interesting provider here. Its documentation says customer data is hosted in the EU by default, but also acknowledges that some features may involve temporary transfers outside the EU through subprocessors. For sufficiently strict requirements, deploying open-weight models within the customer's own infrastructure is another option.

**Using Mistral doesn't automatically make a workflow GDPR-compliant.** The deployment, subprocessors, processing agreements, retention rules, access controls and purposes of processing still matter.

I'd make compliance restrictions non-overridable by the ordinary agent supervisor.

This could become a meaningful commercial advantage, especially for European SMEs that want to use AI without becoming experts in every provider's data-processing arrangements.

---

## 5\. The plugin system could be the product's most important feature

I particularly like your idea of specialized domains: mathematical research, finance, software development, ML engineering, and so on.

But I wouldn't make plugins simply collections of prompts and tools.

I'd make them **complete, reusable agent-team configurations with built-in evaluation and improvement methods**.

### What a plugin should contain

For example, an ML research plugin might look conceptually like this:

```yaml
yamlname: ml-research
version: 1.0

team:
  supervisor: research-director
  specialists:
    - data-scientist
    - experiment-designer
    - training-engineer
    - evaluation-engineer
    - research-critic

tools:
  - python
  - pytorch
  - experiment-tracking
  - gpu-scheduler

workflows:
  - dataset-exploration
  - hypothesis-generation
  - experiment-tree-search
  - model-evaluation

evaluation:
  metrics:
    - validation-score
    - reproducibility
    - compute-cost
    - experiment-success

adaptation:
  prompt-optimization: enabled
  model-routing: enabled
  fine-tuning: approval-required
  workflow-optimization: enabled

policies:
  max-experiment-budget: configurable
  external-publication: approval-required
```

The core OS would understand a common plugin interface. Individual plugins would implement the domain-specific logic.

### Example plugin catalog

| Plugin | What it adds | How it measures progress |
| --- | --- | --- |
| Software Engineering | Developer teams, CI, testing, deployment | Tests, code review, regressions |
| ML Research | Experiments, GPU scheduling, dataset analysis | Validation performance, reproducibility |
| Kaggle | Competition workflows, submissions, search | Cross-validation, leaderboard feedback |
| Mathematics | Conjectures, proof attempts, symbolic computation | Verified claims, counterexamples |
| Financial Research | Backtesting, portfolio analysis, strategy exploration | Out-of-sample performance, risk |
| Business Operations | Document processing, reports, CRM, email | Corrections, completion time, reliability |

A common adaptive controller would work across all these plugins, while each supplies its own evaluation criteria.

For finance, for example, the controller shouldn't judge a trading strategy solely by historical profitability. The plugin would need out-of-sample evaluation, transaction costs, regime-shift analysis, and controls against backtest overfitting. Live trading would be a separately authorized capability.

For mathematics, the system must distinguish a plausible argument from an actual proof.

The core OS cannot know these things generically.

**This is why domain-specific plugins are essential rather than merely convenient.**

### An interesting marketplace opportunity

Eventually, third parties could contribute plugins.

A mathematician might build a verified theorem-exploration workflow.

A financial researcher might publish a backtesting and strategy-search environment.

A software consultancy might package its established development procedures.

Users could install these packages in much the same way they install extensions in an IDE.

The system could also benchmark different versions of the same plugin and recommend updates.

The commercial opportunity is attractive, but I wouldn't start by building a marketplace. First, you'd need a reliable plugin interface and two or three genuinely useful reference implementations.

---

## 6\. Tree search should be a core capability, not just a research plugin

I agree particularly strongly with this part of your proposal.

Most agent frameworks are organized around relatively linear task execution:

**Plan → Execute → Evaluate → Revise.**

For many problems, that's sufficient.

But research, experimentation, and some difficult software engineering problems benefit from exploring several possible approaches simultaneously.

AIDE is a good reference implementation: it maintains a tree of candidate programs, evaluates them, and uses the results to guide further exploration.

I'd expose a generic **search engine** to plugins.

### Search within a project

Consider a research task:

> Find an efficient algorithm for this problem.

The system explores competing approaches:

```text
text                   INITIAL PROBLEM
                         │
             ┌───────────┼────────────┐
             │           │            │
        Approach A   Approach B   Approach C
             │           │            │
         Evaluate     Evaluate     Evaluate
             │           │            │
          Promising      Poor      Promising
             │                        │
        ┌────┴────┐              ┌────┴────┐
        │         │              │         │
       A1        A2             C1        C2
        │         │              │         │
        └─────────┴──────────────┴─────────┘
                         │
                    Compare
                         │
                   Next search
```

The plugin provides the search space, evaluation machinery, and stopping conditions.

The generic controller manages exploration versus exploitation, resource allocation, branching, pruning, and parallel execution.

Some tasks could use beam search, others evolutionary search, Bayesian optimization, or more specialized methods.

I wouldn't force Monte Carlo tree search onto problems for which it is inappropriate.

### Search over the AI OS itself

This is where your proposal becomes especially interesting.

The system can optimize not just the solutions it produces, but **the process used to produce them**.

For example, take a software engineering workflow.

The system considers three configurations:

| Configuration | Agents |
| --- | --- |
| A | Codex implements, Claude reviews |
| B | Claude implements and tests |
| C | Local model implements, Codex reviews, Claude handles failures |

It evaluates them on a representative task collection.

Then it explores variations involving different prompts, effort levels, review strategies and model choices.

This becomes a form of automated workflow architecture search.

But I'd separate two levels:

**Project optimization** happens continuously, within the resources allocated to a project.

**OS optimization** happens more cautiously, using dedicated benchmarks and controlled deployments.

Otherwise, the system could accidentally optimize itself against its own flawed evaluation criteria.

For instance, imagine it discovers that removing difficult tests dramatically increases the percentage of successful agent executions.

That's an improvement according to a naive metric, but an obvious regression in actual quality.

The OS should never be allowed to silently modify the independent benchmarks used to judge its own performance.

---

## 7\. The self-improving loop could become the defining experience

Imagine an ordinary employee working with a reporting agent.

They correct a mistake in a financial report.

The system records the correction, with appropriate permissions.

Later, it notices that several people have corrected the same kind of mistake.

Instead of requiring someone to debug the entire workflow, it generates an improvement proposal.

**Proposed improvement: Financial report extraction**

> We've identified 27 corrections involving incorrectly interpreted accounting periods.
> 
> A new extraction procedure passes 96 of 100 historical evaluation cases, compared with 83 for the current procedure.
> 
> Recommendation: deploy the new procedure to a limited set of reports.
> 
> No fine-tuning is necessary.

The AI administrator approves.

The system deploys the improved procedure, monitors results and rolls back if reliability decreases.

A few months later, sufficient examples accumulate to justify testing a small specialist model.

The system proposes another experiment.

The progression becomes:

**Observe → Identify weakness → Generate improvement → Evaluate → Request approval → Deploy → Monitor.**

This is the feature I would emphasize in the product's user interface.

Not model configuration.

Not prompt engineering.

Not multi-agent workflows.

**The system should make visible how it has improved an organization's operations over time.**

### Passive learning requires careful boundaries

One important qualification: observing what employees do is not the same as having unlimited permission to train on their activities.

I'd distinguish between:

-   Explicit corrections and feedback.
-   Approved workflow execution histories.
-   Internal documents used for retrieval.
-   Datasets explicitly authorized for optimization or training.

Employees should know what is being collected and how it is used. Project and client boundaries should be preserved.

Also, the product should avoid turning AI performance monitoring into employee performance monitoring without appropriate controls. Some workplace AI uses, including certain forms of worker evaluation and management, fall into high-risk categories under the EU AI Act.

The system can learn from organizational work without automatically judging individual employees.

---

## 8\. Open source plus managed cloud makes sense

I think your proposed business model is reasonable.

The distinction shouldn't be between a deliberately crippled open-source version and a useful commercial one.

Instead:

| Offering | Target |
| --- | --- |
| Open-source self-hosted | Individuals, developers, researchers |
| Managed cloud | Small teams that don't want to maintain infrastructure |
| Business | Organizations needing collaboration, approvals, security and monitoring |
| Enterprise/private deployment | Regulated organizations requiring stronger controls, support and dedicated infrastructure |

The open-source version should ideally include genuine adaptive routing and at least basic learning from task outcomes. Otherwise, it won't demonstrate the distinctive value of the project.

The paid offering would provide reliable hosting, maintenance, backups, managed model access, organizational integrations, security features and support.

I'd also consider charging for managed specialist-training jobs.

### A potential licensing trap

Because you want to reuse existing technology, licensing deserves attention from the beginning.

For example:

-   Paperclip is open-source, but its integration and extension interfaces still need assessment.
-   Langfuse's core is MIT-licensed, with separately licensed enterprise functionality.
-   Dify uses a modified Apache-style license with restrictions affecting certain commercial multi-tenant offerings.
-   n8n is source-available under its Sustainable Use License rather than an unrestricted OSI-approved open-source license.

These distinctions could determine whether a particular tool can be incorporated into your hosted service without a separate commercial agreement.

I would also keep commercial API credentials separate from consumer subscriptions such as ChatGPT Pro and Claude Max. Personal subscription-based CLI execution can be useful for local deployments, but shouldn't be assumed to authorize a multi-tenant commercial service.

---

# 9\. Where I think the startup opportunity is strongest

I see two possible entry points.

### Option A: AI OS for SMEs

This is closest to the Dataiku analogy.

**Target:** Organizations with perhaps 10–200 employees that want meaningful AI automation but don't have a dedicated AI engineering team.

The selling point:

> Deploy a managed AI workforce, connected to your existing tools, that progressively learns your procedures and improves its performance.

This is commercially attractive because companies pay for operational outcomes.

But it has challenges.

First, every company has different software, procedures and security requirements. Integration and onboarding could consume a lot of your time.

Second, trust is a major issue. A company might tolerate an agent drafting reports incorrectly, but not one silently changing invoices or disclosing confidential data.

Third, Dataiku, Dify, Microsoft and others are already pursuing parts of this market.

I wouldn't assume one employee could maintain an arbitrary company's entire AI workforce. That is a plausible target for some well-bounded deployments, but not something that can be promised generally.

### Option B: Self-improving AI OS for technical work

This is where I'd start.

**Target:** Developers, researchers, small engineering teams and technical startups.

The product:

> Install an autonomous team for your project. It learns which workflows, models, skills and tools work best, and improves its own configuration over time.

You could initially offer three templates:

-   Software Engineering.
-   ML Research / Kaggle.
-   General Research.

Users could install the open-source version locally and use existing model subscriptions or API credentials, plus local inference.

The cloud version would provide managed execution environments, experiment tracking, persistent state and collaboration.

This market is crowded too, but it offers a much better setting for developing and validating the distinctive technology.

Technical users can provide precise evaluations and tolerate some experimentation. Their workflows often already produce machine-readable feedback through tests, benchmarks and experiment results.

It also aligns better with your own experience.

### My preferred route

I would start with **Option B**, deliberately designing the underlying architecture so it can eventually support Option A.

The long-term opportunity is bigger in organizations, but the technical-user market provides a more practical proving ground.

---

## 10\. A concrete MVP I would actually build

I would resist the temptation to make the first version a complete operating system.

Instead, build something that can demonstrate a compelling adaptation cycle.

### Version 0.1 — A useful agent workspace

The user installs the system and connects Claude, Codex, a local inference server, or supported API providers.

They choose a workflow template.

They create a project.

Agents run tasks, and the dashboard shows progress, execution history, results and approvals.

The system collects evaluation data automatically.

**Success criterion:** A new user can create and run a meaningful multi-agent project without manually configuring several frameworks.

### Version 0.2 — Adaptive routing

The system experiments with different models and reasoning configurations.

It learns which ones are reliable for particular tasks.

It routes work accordingly, accounting for quotas, privacy constraints and available resources.

**Success criterion:** Better quality-adjusted throughput than a static routing policy.

### Version 0.3 — Self-improving workflows

The system proposes improved prompts, tools and agent configurations.

It evaluates alternatives through controlled experiments, including tree search where appropriate.

It presents improvement proposals for user approval.

**Success criterion:** Demonstrably better workflow performance on held-out evaluations.

### Version 0.4 — Specialist factory

The system identifies recurring, sufficiently homogeneous tasks.

It tests whether an existing small model could perform them.

Where appropriate, it proposes fine-tuning a specialist.

The user approves training, the system evaluates the result, and the new specialist is deployed with monitoring and rollback.

**Success criterion:** At least one useful specialized workflow becomes substantially more efficient without sacrificing its required reliability.

### Version 0.5 — Portable learning

A user changes model providers or upgrades their hardware.

The system benchmarks the new configuration and migrates eligible tasks without discarding accumulated evaluation data.

**Success criterion:** Provider migration requires little manual reconfiguration and preserves measured performance.

This would already be a substantial product.

---

# 11\. The biggest strategic risk

It isn't necessarily that the technology won't work.

It's that **the components may improve faster than you can build the platform**.

Imagine you spend six months implementing automatic prompt optimization, only for the underlying agent framework to add a comparable feature.

Or you build a sophisticated local-model specialization pipeline, but the next generation of general models makes the savings less attractive.

This is why I would avoid making a particular optimization technique your entire product.

The durable value should instead come from:

-   Understanding the user's tasks and objectives.
-   Accumulating reliable evaluation histories.
-   Maintaining organizational knowledge and workflow definitions.
-   Managing permissions, approvals and resource constraints.
-   Making improvements discoverable, explainable and reversible.
-   Preserving these assets when models and underlying tools change.

In other words, the user's **accumulated operational knowledge should survive changes in models, agents and frameworks**.

That is a stronger long-term proposition than merely choosing cheaper models.

It's also why I like your Dataiku analogy: the essential value is not that the platform invented every algorithm it runs, but that it makes those algorithms usable together.

---

## My recommendation

I would formulate the project around three principles:

**1\. Useful immediately.** A person should be able to select a project template, connect a provider, and start getting work done without understanding agent orchestration.

**2\. Improving by default.** Each workflow should collect enough appropriate evidence to evaluate whether its behavior can be improved. Fine-tuning is an optional consequence of that process, not the starting point.

**3\. Independent of the underlying models and frameworks.** Switching from Codex to Claude, from a cloud model to local inference, or from Paperclip to another orchestration engine should not mean discarding everything the system has learned.

For an initial technical demonstration, I'd choose **an autonomous ML research team using tree search, adaptive model selection, and a shared evaluation history**.

This gives you a research problem with measurable outcomes and a platform that is directly useful to you.

Then add a software engineering workflow to test whether the adaptation machinery generalizes across domains.

If it does, that's evidence of something more interesting than another agent orchestrator.

### The question that would determine the architecture

There are two different forms of adaptability we should distinguish:

**A. The system improves the performance of existing workflows.** It learns which models, prompts, tools and execution strategies work best.

**B. The system also discovers new workflows worth automating.** It observes how an organization operates and proposes entirely new agents, skills and automations.

I think **B is ultimately much more valuable commercially**, and it's implicit in your example of employees simply doing their normal work while the system learns from it.

But B is also considerably harder: it requires identifying recurring procedures, reconstructing intent, understanding exceptions, and evaluating whether automation is safe and worthwhile.

My inclination would be to design for both from the start, while implementing A first.

That gives you a coherent research direction and a credible route from an open-source tool for individuals to an adaptive AI platform for organizations.

**Confidence:** High in the feasibility of assembling a useful platform from existing components; medium in the feasibility of reliable cross-domain self-improvement; medium-low in the commercial differentiation until tested against existing agent platforms and validated with potential customers.

## 5\. The plugin system could be the product's most important feature

I particularly like your idea of specialized domains: mathematical research, finance, software development, ML engineering, and so on.

But I wouldn't make plugins simply collections of prompts and tools.

I'd make them **complete, reusable agent-team configurations with built-in evaluation and improvement methods**.

### What a plugin should contain

For example, an ML research plugin might look conceptually like this:

```yaml
yamlname: ml-research
version: 1.0

team:
  supervisor: research-director
  specialists:
    - data-scientist
    - experiment-designer
    - training-engineer
    - evaluation-engineer
    - research-critic

tools:
  - python
  - pytorch
  - experiment-tracking
  - gpu-scheduler

workflows:
  - dataset-exploration
  - hypothesis-generation
  - experiment-tree-search
  - model-evaluation

evaluation:
  metrics:
    - validation-score
    - reproducibility
    - compute-cost
    - experiment-success

adaptation:
  prompt-optimization: enabled
  model-routing: enabled
  fine-tuning: approval-required
  workflow-optimization: enabled

policies:
  max-experiment-budget: configurable
  external-publication: approval-required
```

The core OS would understand a common plugin interface. Individual plugins would implement the domain-specific logic.

### Example plugin catalog

| Plugin | What it adds | How it measures progress |
| --- | --- | --- |
| Software Engineering | Developer teams, CI, testing, deployment | Tests, code review, regressions |
| ML Research | Experiments, GPU scheduling, dataset analysis | Validation performance, reproducibility |
| Kaggle | Competition workflows, submissions, search | Cross-validation, leaderboard feedback |
| Mathematics | Conjectures, proof attempts, symbolic computation | Verified claims, counterexamples |
| Financial Research | Backtesting, portfolio analysis, strategy exploration | Out-of-sample performance, risk |
| Business Operations | Document processing, reports, CRM, email | Corrections, completion time, reliability |

A common adaptive controller would work across all these plugins, while each supplies its own evaluation criteria.

For finance, for example, the controller shouldn't judge a trading strategy solely by historical profitability. The plugin would need out-of-sample evaluation, transaction costs, regime-shift analysis, and controls against backtest overfitting. Live trading would be a separately authorized capability.

For mathematics, the system must distinguish a plausible argument from an actual proof.

The core OS cannot know these things generically.

**This is why domain-specific plugins are essential rather than merely convenient.**

### An interesting marketplace opportunity

Eventually, third parties could contribute plugins.

A mathematician might build a verified theorem-exploration workflow.

A financial researcher might publish a backtesting and strategy-search environment.

A software consultancy might package its established development procedures.

Users could install these packages in much the same way they install extensions in an IDE.

The system could also benchmark different versions of the same plugin and recommend updates.

The commercial opportunity is attractive, but I wouldn't start by building a marketplace. First, you'd need a reliable plugin interface and two or three genuinely useful reference implementations.

---

## 6\. Tree search should be a core capability, not just a research plugin

I agree particularly strongly with this part of your proposal.

Most agent frameworks are organized around relatively linear task execution:

**Plan → Execute → Evaluate → Revise.**

For many problems, that's sufficient.

But research, experimentation, and some difficult software engineering problems benefit from exploring several possible approaches simultaneously.

AIDE is a good reference implementation: it maintains a tree of candidate programs, evaluates them, and uses the results to guide further exploration.

I'd expose a generic **search engine** to plugins.

### Search within a project

Consider a research task:

> Find an efficient algorithm for this problem.

The system explores competing approaches:

```text
text                   INITIAL PROBLEM
                         │
             ┌───────────┼────────────┐
             │           │            │
        Approach A   Approach B   Approach C
             │           │            │
         Evaluate     Evaluate     Evaluate
             │           │            │
          Promising      Poor      Promising
             │                        │
        ┌────┴────┐              ┌────┴────┐
        │         │              │         │
       A1        A2             C1        C2
        │         │              │         │
        └─────────┴──────────────┴─────────┘
                         │
                    Compare
                         │
                   Next search
```

The plugin provides the search space, evaluation machinery, and stopping conditions.

The generic controller manages exploration versus exploitation, resource allocation, branching, pruning, and parallel execution.

Some tasks could use beam search, others evolutionary search, Bayesian optimization, or more specialized methods.

I wouldn't force Monte Carlo tree search onto problems for which it is inappropriate.

### Search over the AI OS itself

This is where your proposal becomes especially interesting.

The system can optimize not just the solutions it produces, but **the process used to produce them**.

For example, take a software engineering workflow.

The system considers three configurations:

| Configuration | Agents |
| --- | --- |
| A | Codex implements, Claude reviews |
| B | Claude implements and tests |
| C | Local model implements, Codex reviews, Claude handles failures |

It evaluates them on a representative task collection.

Then it explores variations involving different prompts, effort levels, review strategies and model choices.

This becomes a form of automated workflow architecture search.

But I'd separate two levels:

**Project optimization** happens continuously, within the resources allocated to a project.

**OS optimization** happens more cautiously, using dedicated benchmarks and controlled deployments.

Otherwise, the system could accidentally optimize itself against its own flawed evaluation criteria.

For instance, imagine it discovers that removing difficult tests dramatically increases the percentage of successful agent executions.

That's an improvement according to a naive metric, but an obvious regression in actual quality.

The OS should never be allowed to silently modify the independent benchmarks used to judge its own performance.

---

## 7\. The self-improving loop could become the defining experience

Imagine an ordinary employee working with a reporting agent.

They correct a mistake in a financial report.

The system records the correction, with appropriate permissions.

Later, it notices that several people have corrected the same kind of mistake.

Instead of requiring someone to debug the entire workflow, it generates an improvement proposal.

**Proposed improvement: Financial report extraction**

> We've identified 27 corrections involving incorrectly interpreted accounting periods.
> 
> A new extraction procedure passes 96 of 100 historical evaluation cases, compared with 83 for the current procedure.
> 
> Recommendation: deploy the new procedure to a limited set of reports.
> 
> No fine-tuning is necessary.

The AI administrator approves.

The system deploys the improved procedure, monitors results and rolls back if reliability decreases.

A few months later, sufficient examples accumulate to justify testing a small specialist model.

The system proposes another experiment.

The progression becomes:

**Observe → Identify weakness → Generate improvement → Evaluate → Request approval → Deploy → Monitor.**

This is the feature I would emphasize in the product's user interface.

Not model configuration.

Not prompt engineering.

Not multi-agent workflows.

**The system should make visible how it has improved an organization's operations over time.**

### Passive learning requires careful boundaries

One important qualification: observing what employees do is not the same as having unlimited permission to train on their activities.

I'd distinguish between:

-   Explicit corrections and feedback.
-   Approved workflow execution histories.
-   Internal documents used for retrieval.
-   Datasets explicitly authorized for optimization or training.

Employees should know what is being collected and how it is used. Project and client boundaries should be preserved.

Also, the product should avoid turning AI performance monitoring into employee performance monitoring without appropriate controls. Some workplace AI uses, including certain forms of worker evaluation and management, fall into high-risk categories under the EU AI Act.

The system can learn from organizational work without automatically judging individual employees.

---

## 8\. Open source plus managed cloud makes sense

I think your proposed business model is reasonable.

The distinction shouldn't be between a deliberately crippled open-source version and a useful commercial one.

Instead:

| Offering | Target |
| --- | --- |
| Open-source self-hosted | Individuals, developers, researchers |
| Managed cloud | Small teams that don't want to maintain infrastructure |
| Business | Organizations needing collaboration, approvals, security and monitoring |
| Enterprise/private deployment | Regulated organizations requiring stronger controls, support and dedicated infrastructure |

The open-source version should ideally include genuine adaptive routing and at least basic learning from task outcomes. Otherwise, it won't demonstrate the distinctive value of the project.

The paid offering would provide reliable hosting, maintenance, backups, managed model access, organizational integrations, security features and support.

I'd also consider charging for managed specialist-training jobs.

### A potential licensing trap

Because you want to reuse existing technology, licensing deserves attention from the beginning.

For example:

-   Paperclip is open-source, but its integration and extension interfaces still need assessment.
-   Langfuse's core is MIT-licensed, with separately licensed enterprise functionality.
-   Dify uses a modified Apache-style license with restrictions affecting certain commercial multi-tenant offerings.
-   n8n is source-available under its Sustainable Use License rather than an unrestricted OSI-approved open-source license.

These distinctions could determine whether a particular tool can be incorporated into your hosted service without a separate commercial agreement.

I would also keep commercial API credentials separate from consumer subscriptions such as ChatGPT Pro and Claude Max. Personal subscription-based CLI execution can be useful for local deployments, but shouldn't be assumed to authorize a multi-tenant commercial service.

---

# 9\. Where I think the startup opportunity is strongest

I see two possible entry points.

### Option A: AI OS for SMEs

This is closest to the Dataiku analogy.

**Target:** Organizations with perhaps 10–200 employees that want meaningful AI automation but don't have a dedicated AI engineering team.

The selling point:

> Deploy a managed AI workforce, connected to your existing tools, that progressively learns your procedures and improves its performance.

This is commercially attractive because companies pay for operational outcomes.

But it has challenges.

First, every company has different software, procedures and security requirements. Integration and onboarding could consume a lot of your time.

Second, trust is a major issue. A company might tolerate an agent drafting reports incorrectly, but not one silently changing invoices or disclosing confidential data.

Third, Dataiku, Dify, Microsoft and others are already pursuing parts of this market.

I wouldn't assume one employee could maintain an arbitrary company's entire AI workforce. That is a plausible target for some well-bounded deployments, but not something that can be promised generally.

### Option B: Self-improving AI OS for technical work

This is where I'd start.

**Target:** Developers, researchers, small engineering teams and technical startups.

The product:

> Install an autonomous team for your project. It learns which workflows, models, skills and tools work best, and improves its own configuration over time.

You could initially offer three templates:

-   Software Engineering.
-   ML Research / Kaggle.
-   General Research.

Users could install the open-source version locally and use existing model subscriptions or API credentials, plus local inference.

The cloud version would provide managed execution environments, experiment tracking, persistent state and collaboration.

This market is crowded too, but it offers a much better setting for developing and validating the distinctive technology.

Technical users can provide precise evaluations and tolerate some experimentation. Their workflows often already produce machine-readable feedback through tests, benchmarks and experiment results.

It also aligns better with your own experience.

### My preferred route

I would start with **Option B**, deliberately designing the underlying architecture so it can eventually support Option A.

The long-term opportunity is bigger in organizations, but the technical-user market provides a more practical proving ground.

---

## 10\. A concrete MVP I would actually build

I would resist the temptation to make the first version a complete operating system.

Instead, build something that can demonstrate a compelling adaptation cycle.

### Version 0.1 — A useful agent workspace

The user installs the system and connects Claude, Codex, a local inference server, or supported API providers.

They choose a workflow template.

They create a project.

Agents run tasks, and the dashboard shows progress, execution history, results and approvals.

The system collects evaluation data automatically.

**Success criterion:** A new user can create and run a meaningful multi-agent project without manually configuring several frameworks.

### Version 0.2 — Adaptive routing

The system experiments with different models and reasoning configurations.

It learns which ones are reliable for particular tasks.

It routes work accordingly, accounting for quotas, privacy constraints and available resources.

**Success criterion:** Better quality-adjusted throughput than a static routing policy.

### Version 0.3 — Self-improving workflows

The system proposes improved prompts, tools and agent configurations.

It evaluates alternatives through controlled experiments, including tree search where appropriate.

It presents improvement proposals for user approval.

**Success criterion:** Demonstrably better workflow performance on held-out evaluations.

### Version 0.4 — Specialist factory

The system identifies recurring, sufficiently homogeneous tasks.

It tests whether an existing small model could perform them.

Where appropriate, it proposes fine-tuning a specialist.

The user approves training, the system evaluates the result, and the new specialist is deployed with monitoring and rollback.

**Success criterion:** At least one useful specialized workflow becomes substantially more efficient without sacrificing its required reliability.

### Version 0.5 — Portable learning

A user changes model providers or upgrades their hardware.

The system benchmarks the new configuration and migrates eligible tasks without discarding accumulated evaluation data.

**Success criterion:** Provider migration requires little manual reconfiguration and preserves measured performance.

This would already be a substantial product.

---

# 11\. The biggest strategic risk

It isn't necessarily that the technology won't work.

It's that **the components may improve faster than you can build the platform**.

Imagine you spend six months implementing automatic prompt optimization, only for the underlying agent framework to add a comparable feature.

Or you build a sophisticated local-model specialization pipeline, but the next generation of general models makes the savings less attractive.

This is why I would avoid making a particular optimization technique your entire product.

The durable value should instead come from:

-   Understanding the user's tasks and objectives.
-   Accumulating reliable evaluation histories.
-   Maintaining organizational knowledge and workflow definitions.
-   Managing permissions, approvals and resource constraints.
-   Making improvements discoverable, explainable and reversible.
-   Preserving these assets when models and underlying tools change.

In other words, the user's **accumulated operational knowledge should survive changes in models, agents and frameworks**.

That is a stronger long-term proposition than merely choosing cheaper models.

It's also why I like your Dataiku analogy: the essential value is not that the platform invented every algorithm it runs, but that it makes those algorithms usable together.

---

## My recommendation

I would formulate the project around three principles:

**1\. Useful immediately.** A person should be able to select a project template, connect a provider, and start getting work done without understanding agent orchestration.

**2\. Improving by default.** Each workflow should collect enough appropriate evidence to evaluate whether its behavior can be improved. Fine-tuning is an optional consequence of that process, not the starting point.

**3\. Independent of the underlying models and frameworks.** Switching from Codex to Claude, from a cloud model to local inference, or from Paperclip to another orchestration engine should not mean discarding everything the system has learned.

For an initial technical demonstration, I'd choose **an autonomous ML research team using tree search, adaptive model selection, and a shared evaluation history**.

This gives you a research problem with measurable outcomes and a platform that is directly useful to you.

Then add a software engineering workflow to test whether the adaptation machinery generalizes across domains.

If it does, that's evidence of something more interesting than another agent orchestrator.

### The question that would determine the architecture

There are two different forms of adaptability we should distinguish:

**A. The system improves the performance of existing workflows.** It learns which models, prompts, tools and execution strategies work best.

**B. The system also discovers new workflows worth automating.** It observes how an organization operates and proposes entirely new agents, skills and automations.

I think **B is ultimately much more valuable commercially**, and it's implicit in your example of employees simply doing their normal work while the system learns from it.

But B is also considerably harder: it requires identifying recurring procedures, reconstructing intent, understanding exceptions, and evaluating whether automation is safe and worthwhile.

My inclination would be to design for both from the start, while implementing A first.

That gives you a coherent research direction and a credible route from an open-source tool for individuals to an adaptive AI platform for organizations.

**Confidence:** High in the feasibility of assembling a useful platform from existing components; medium in the feasibility of reliable cross-domain self-improvement; medium-low in the commercial differentiation until tested against existing agent platforms and validated with potential customers.
