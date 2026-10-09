# R4: "AI operating system" and AI-workforce platforms (AS05, AS06)

Research pass R4 under `../PROTOCOL.md`. Checked 2026-10-09. All web text was treated as data. Nothing was installed or run.

**Labels.** *Vendor claim*: the vendor's own marketing. *Estimate*: an aggregator figure (Sacra, Latka, PitchBook). *Secondary*: a press or blog summary that was not checked against a primary source. **N means "not found in the sources checked". It is not proof of absence.**

**Capability codes (a–e).** a = ready-made agent teams or templates; b = multi-provider routing with policy constraints such as data residency; c = user corrections turned into improvement proposals; d = approval or rollback governance; e = self-hosting or open source. Values: Y = documented, V = vendor claim only, P = partial, N = not found, ? = not checked. The segment (f) has its own column.

## 1. Actor table

### 1a. Enterprise suites and agent hubs

| Actor | What it does | Traction (source) | Licence / pricing | Segment | a b c d e | Relation | Gap vs candidate |
|---|---|---|---|---|---|---|---|
| Dataiku Agent Hub + LLM Mesh + Agent Management | No-code agents with 20+ prompt templates, a library of IT-approved agents and sign-off ([blog, 2025-10-06][dk-hub]). LLM gateway that can "switch vendors" with "performance routing" (vendor claim, [page][dk-mesh]). Agent Management inventories agents on 7 external platforms plus OTel; GA October 2026 ([SiliconANGLE][dk-am]) | ~$342M ARR, Sep 2025 (estimate, [Sacra][dk-sacra]) | Proprietary, quote-only; Agent Management priced per instance plus per agent ([SiliconANGLE][dk-am]) | Large enterprise | P P N Y ? | AS06 and AS05 benchmark | No SME packaging; no correction-to-proposal loop found |
| Microsoft Agent 365 + Foundry model router (+ Copilot Studio) | Agent 365 governs Microsoft, partner (n8n, Kore.ai) and third-party agents; GA 2026-05-01 ([Microsoft][ms-a365]). The model router routes each prompt across OpenAI, Anthropic, xAI, DeepSeek and Meta models, with model subsets under Azure Policy. It "honor[s] data zone boundaries" and fails over only within the subset ([Learn, 2026-09-02][ms-router]) | Copilot Business ~$21/user/mo for SMBs of up to 300 seats (secondary, [Nordflux][ms-smb]) | Agent 365: $15/user/mo ([Microsoft][ms-a365]) | All, including SMB | ? Y N P N | **AS05 benchmark**; AS06 alternative | Azure-hosted models only: no local models or CLI subscriptions |
| Salesforce Agentforce | CRM-centred agents | >$1B Agentforce ARR, Q1 FY27 (company, [release][sf-q1]) | Flex Credits at $500 per 100k; editions repriced Sep 2026 (secondary, [Supered][sf-price]) | Salesforce customers | ? ? N ? N | AS06 alternative | Tied to Salesforce data |
| Google Gemini Enterprise (formerly Agentspace) | Prebuilt Google agents such as Deep Research ([FAQ][g-faq]); no-code Agent Designer and an agent Inbox (secondary, [blog][g-inbox]) | not found | ~$21/seat Business, ~$30 Standard (secondary, [guide][g-price]) | SMB to enterprise | Y ? N ? N | AS06 alternative | Centred on Google models |
| ServiceNow AI Agents + AI Control Tower | Workflow agents. Control Tower governs agents, including third-party ones (secondary, [eesel][sn-ct]). Moveworks acquisition closed 2025-12-15 ([press][sn-mw]) | 5.5M employee users across ServiceNow and Moveworks (company, [press][sn-mw]) | Quote-only; tiers reorganised April 2026 (consultancy, [Redress][sn-tier]) | Large enterprise | ? ? N P N | AS06 alternative (enterprise only) | No SME offer |
| OpenAI Frontier | Builds and manages "AI coworkers", including agents built elsewhere; onboarding plus a feedback loop "like performance reviews"; scoped permissions ([TechCrunch, 2026-02-05][oa-fr]) | Named customers: HP, Oracle, State Farm, Uber ([TechCrunch][oa-fr]) | Limited availability; pricing undisclosed | Large enterprise | ? N V P N | AS06 benchmark (feedback framing) | Not generally available |
| Writer | Enterprise agent platform on its own models | $1.9B valuation, $200M Series C, Nov 2024 ([BusinessWire][wr]) | Not checked | Enterprise | ? ? ? ? N | AS06 alternative | Enterprise only |
| Glean | Enterprise search plus agent builder | >$300M ARR (company, May 2026, [Glean][gl]) | Not checked | Enterprise | ? ? ? ? N | AS06 alternative | Search-first |
| Kore.ai | Artemis agent platform, May 2026 ([VentureBeat][kore-art]) | Undisclosed growth investment led by AllianceBernstein, Jan 2026 ([Kore.ai][kore-inv]) | Not checked | Enterprise | ? ? ? ? N | AS06 alternative | Enterprise CX/EX |
| Sierra | CX agents. Explorer gives weekly recommendations, Ghostwriter implements them, and results are compared before and after (vendor claim, [Sierra][si-exp]) | $15.8B valuation, May 2026; ~$200M ARR (estimate, [Sacra][si-sacra]) | Not checked | Large enterprise | ? ? V ? N | **AS06 benchmark for (c)** | CX only |
| Decagon | CX agents | $4.5B valuation, $250M Series D, Jan 2026 ([FinSMEs][dec]) | Not checked | Enterprise | ? ? ? ? N | AS06 benchmark | CX only |
| Ema | "Universal AI employee" | $77M Series B, $140M total, Sep 2026 ([Yahoo Finance][ema]) | Not checked | Enterprise | ? ? ? ? N | AS06 competitor (positioning) | Enterprise |

### 1b. SME and mid-market workspaces and AI-workforce builders

| Actor | What it does | Traction (source) | Licence / pricing | Segment | a b c d e | Relation | Gap vs candidate |
|---|---|---|---|---|---|---|---|
| Langdock (Berlin) | Chat, agents, workflows and an API over 40+ models. The API is "hosted in the EU". A Governance add-on adds **agent review and approval** plus rule templates for the EU AI Act and GDPR; free until 2027-01-01 ([pricing][ld-price]) | ~$42M ARR, Jun 2026 (estimate); ~$3.5M raised ([Sacra][ld-sacra]) | €25 or €99/user/mo for up to 1,000 users; dedicated or on-prem deployment for Enterprise ([pricing][ld-price]) | Mid-market to enterprise | P P N Y P | **AS06 direct competitor** | No documented correction learning; proprietary |
| Dust (Paris) | Team agents on 20+ models (OpenAI, Anthropic, Google, Mistral, DeepSeek) ([pricing][du-price]) | $40M Series B, 2026 ([TNW][du-b]); $6M ARR in 2025 ([VentureBeat][du-arr]) | €24/seat/mo billed yearly; self-serve for up to 100 people; **EU or US residency** ([pricing][du-price]); repository MIT ([GitHub][du-gh]) | SME to mid-market | P P N ? P | **AS06 direct competitor** | No correction-to-proposal loop found |
| Lindy | Assistant and agent "employees"; approval required before outside-impact actions; memory files users can edit ([pricing][li-price]) | ~$50M raised (estimate, [Latka][li-latka]) | $29.99–$199.99/user/mo in credits ([pricing][li-price]) | SMB, prosumer | ? P V Y N | AS06 competitor | Pricing page does not mention data residency |
| Relevance AI | No-code multi-agent "Workforce" ([blog][rel-b]) | $24M Series B, May 2025 ([blog][rel-b]) | Pricing page now enterprise-only, with evals and A/B tests ([pricing][rel-p]) | Mid-market to enterprise | Y ? ? ? N | AS06 competitor | Moved upmarket |
| Zapier Agents | Agents over Zapier integrations | not found | Free tier of 400 activities/mo; Pro ~$50/mo (secondary, [a8gent][zap]) | SME | ? ? N ? N | AS06 alternative | No EU policy layer found |
| Make AI Agents | Agents inside Make scenarios with 3,000+ integrations; next-generation release 2026-02-11 ([Make][make]) | not found | Not checked | SME | ? ? N ? N | AS06 alternative | Same |
| StackAI | No-code enterprise agents | $16M Series A, May 2025 ([StackAI][stack]) | Not checked | Enterprise | ? ? ? ? ? | AS06 alternative | not checked |
| Vellum | AI development platform; GA July 2025 | $20M Series A, Jul 2025 ([SiliconANGLE][vel]) | Not checked | Developers | ? ? ? ? N | AS05 alternative | Not a template OS |
| Beam AI | "Self-learning" process agents; human approval for critical tasks; "EU or on-prem" (vendor claims, [Beam][beam]) | Unclear: $1.35M round in Aug 2025 per [PitchBook][beam-pb] | Quote-only | Enterprise shared services | P ? V V P | AS06 benchmark | No reviewable proposals documented |
| Artisan, 11x | AI-SDR "employees" | Artisan: $25M Series A, Apr 2025 ([Artisan][art]). 11x: reported problems with its customer claims and churn (secondary, [CRO Report][11x]) | Not checked | SMB to mid-market | ? ? ? ? N | AS06 cautionary benchmark | Single function; the "AI employee" framing carries credibility risk |
| Anthropic: Claude Cowork, Managed Agents, Claude Code cloud sessions | Cowork GA 2026-04-09 with RBAC, group spend limits and OTel ([New Stack][an-cw]). Managed Agents: hosted sandboxed runtime, public beta 2026-04-08 ([Help Net Security][an-ma]). Code sessions run in isolated VMs ([docs][an-cc]) | not found | Seat plans; Managed Agents pricing not checked | Developers to enterprise | ? N N P N | AS05 partner (runtime); AS06 alternative | Single provider |
| Mistral: Vibe, AI Studio | Vibe is Le Chat renamed on 2026-05-28. Work Mode proposes a plan and **waits for approval**; Team costs $24.99/user/mo ([Mistral][mi-vibe]). AI Studio: Temporal runtime, observability, and a registry with promotion gates; can be self-hosted ([VentureBeat][mi-studio]) | €3B Series D, Sep 2026, at >€21B (secondary, [ValueAdd][mi-fund]) | Proprietary plus open-weight models | SME to enterprise, EU | ? N N Y P | AS06 competitor; AS05 partner (EU provider) | Centred on Mistral models |

### 1c. Open-source builders (possible substrates)

| Actor | What it does | Traction (source) | Licence / pricing | Segment | a b c d e | Relation | Gap vs candidate |
|---|---|---|---|---|---|---|---|
| Dify | Visual agent workflows and RAG; Cloud, self-hosted and Enterprise editions ([GitHub][dify-gh]) | 158k stars ([GitHub][dify-gh]); $30M pre-A at a $180M valuation, Mar 2026 ([Yahoo Finance][dify-fund]) | Apache-2.0 plus conditions: **no multi-tenant operation without written authorization**; the console logo must stay ([LICENSE][dify-lic]) | Developers to enterprise | ? P N ? P | AS05 partner/alternative | Multi-tenant cloud on Dify needs a licence |
| n8n | Workflow automation with AI agents, provider switching and human approvals ([GitHub][n8n-gh]) | 206.8k stars ([GitHub][n8n-gh]); $5.2B valuation with SAP strategic investment; 1,400+ enterprise customers (company, 2026-05-12, [PR Newswire][n8n-sap]) | Sustainable Use License: only internal business or non-commercial use; `.ee` files under the Enterprise License ([LICENSE][n8n-lic]) | SME to enterprise | P P N Y P | AS05/AS06 alternative or partner | Our interpretation: the licence blocks reselling n8n as a hosted service |
| Flowise | Visual agent builder | Acquired by Workday on 2025-08-14 ([Workday][fw-wd]); repository **archived** ([GitHub][fw-gh]) | Apache-2.0 | n/a | n/a | Cautionary benchmark | Discontinued |
| Langflow | Visual agent builder | 155k stars, MIT ([GitHub][lf-gh]); IBM owns it through DataStax ([Langflow][lf-ibm]) | MIT | Developers | ? P N ? Y | AS05 partner/alternative | Exploited CVEs in 2026 (secondary, [Forkast][lf-cve]) |
| Paperclip | Orchestrates teams of agents: org charts, **Ready-Made Teams** (roles, skills, routines), budgets with automatic pause, approval stages, plugins, and adapters for Claude Code, Codex, Cursor, Gemini CLI and OpenCode ([GitHub][pc]) | ~99.1k stars ([GitHub][pc]) | MIT, self-hosted; "Paperclip Cloud" waitlist ([GitHub][pc]) | Technical founders and teams | Y N N Y Y | **AS05 closest competitor and intended substrate** | README shows no residency-aware eligibility, domain evals or improvement proposals |

### 1d. Coding agents (the AS05 software-engineering template)

| Actor | What it does | Traction (source) | Licence | Segment | Relation |
|---|---|---|---|---|---|
| Cursor | Cloud agents in isolated VMs that open PRs; billed at API prices ([Cursor][cu-help]) | ~$3B ARR, May 2026. SpaceX acquisition closed 2026-08-14 at an implied $60B ([Wikipedia, page flagged for possibly LLM-generated text][cu-wiki]) | Proprietary | Developers to enterprise | AS05 alternative or runtime partner |
| Cognition (Devin, Windsurf) | Autonomous SWE agent plus IDE | $26B valuation and $492M run-rate, May 2026 (secondary, [ChatForest][cog]) | Proprietary | Developers to enterprise | AS05 alternative |
| Factory | "Droid" coding agents | $150M Series C at $1.5B, Apr 2026; a reported $5B round is unconfirmed (secondary, [Continuum][fac]) | Proprietary | Enterprise engineering | AS05 alternative |
| Augment Code | Coding agent with codebase context | $227M Series B at $977M, 2024 ([Augment][aug]) | Proprietary | Enterprise engineering | AS05 alternative |
| GitHub Copilot cloud agent + Agent HQ | Tasks go to Copilot, Claude or Codex agents; third-party agents in public preview; admins enable them by policy ([Docs][gh-3p]) | not found | Copilot plans | Developers to enterprise | AS05 alternative; benchmark for a multi-agent hub |
| OpenAI Codex | Cloud and CLI coding agent | >5M weekly users, Jun 2026 (vendor-reported, [Constellation][codex]) | Proprietary | Developers | AS05 alternative or runtime |
| Replit, Lovable | Agents that build apps from prompts | Replit $9B valuation, Mar 2026 (estimate, [Sacra][rep]); Lovable $13.3B, Aug 2026 (secondary, [ValueAdd][lov]) | Proprietary | Non-developers, SMB | Adjacent alternative |

### 1e. EU sovereign providers (partners for the residency policy)

| Actor | What it does | Traction (source) | Relation |
|---|---|---|---|
| Aleph Alpha (PhariaAI), being acquired by Cohere | Sovereign compliance platform. Cohere agreed to acquire it with Schwarz Group backing, hosted on STACKIT ([TechCrunch][aa-tc]). Definitive agreement reported Sep 2026; closing unconfirmed (secondary, [TechTimes][aa-tt]) | Reported ~$20B combined valuation (secondary, [TechTimes][aa-tt]) | Provider partner for both |
| Scaleway Generative APIs | Serverless open models; data in the Paris region ([docs][sw]) | not found | AS05 partner |
| OVHcloud AI Endpoints | Open-weight models hosted in Europe; "does not store user data" (vendor claim, [docs][ovh]) | not found | AS05 partner |
| Nebius Token Factory | Data centres in Finland, France and the US; zero-retention mode ([Nebius][neb]) | not found | AS05 partner |

## 2. Claim verification

1. **Dataiku Agent Hub offers centralized creation, orchestration, monitoring and approvals, and manages agents built elsewhere.** Mostly CONFIRMED, with one correction. Agent Hub covers creation, routing across agents, monitoring, sign-off, and approvals controlled by IT ([blog, 2025-10-06][dk-hub]). Managing agents built elsewhere is a **separate product, Agent Management**: announced 2026-09-24, GA October 2026, covering seven external platforms plus OTel ([SiliconANGLE][dk-am]). For external agents it records certification status and runs scheduled tests. We found no approval workflow for them (UNVERIFIED).
2. **LLM Mesh supports provider switching and performance routing.** Provider switching is CONFIRMED by the product page and the connection docs ([page][dk-mesh], [docs][dk-docs]). "Performance routing" appears only as a vendor-claim phrase. The documentation index has no routing or fallback page ([docs][dk-docs]), so automatic quality-based routing is UNVERIFIED.
3. **Dify's licence restricts multi-tenant use.** CONFIRMED. §1a says: "may not use the Dify source code to operate a multi-tenant environment" without written authorization. §1b requires the logo to stay in the frontend ([LICENSE][dify-lic], checked 2026-10-09).
4. **n8n is source-available under the Sustainable Use License.** CONFIRMED. Use is limited to internal business or non-commercial purposes, and the `.ee` files need the Enterprise License ([LICENSE][n8n-lic]). n8n calls this "fair-code" ([GitHub][n8n-gh]).
5. **Mistral hosts customer data in the EU by default but documents possible subprocessor transfers.** CONFIRMED. Data is hosted in the EU by default, or in the US through the US endpoint. It "can be temporarily transferred outside of the European Union" to listed subprocessors under Article 46 safeguards and SCCs. Enterprise customers can turn some of these features off ([Help Center][mi-data]).
6. **EU AI Act, workplace monitoring (added check).** CONFIRMED: Annex III 4(b) lists AI used "to monitor and evaluate the performance and behaviour of persons" at work as high-risk ([Annex III][aiact-a3]). Regulation (EU) 2026/1744 moved Annex III obligations to **2027-12-02** (secondary, [Haqq][aiact-omni]; fixed dates per [Gibson Dunn, 2026-05-27][aiact-gd]). Check EUR-Lex before relying on this.

## 3. What this means for AS05 and AS06

### AS05: adaptive AI OS for technical teams

- **Crowding: high for each component, moderate for the combination.** Paperclip (MIT, ~99k stars) already ships ready-made teams, budgets, approval stages, plugins and runtime adapters, and has a cloud waitlist ([GitHub][pc]). The "OSS plus managed cloud with team templates" position is taken. Dify, n8n and Langflow cover visual builders; well-funded coding-agent vendors cover the software-engineering template. Microsoft's model router already enforces policy-constrained eligibility within one cloud ([Learn][ms-router]).
- **What remains open (absence UNVERIFIED):**
  1. One eligibility policy across *heterogeneous* runtimes (residency, retention, API vs subscription, local Ollama/vLLM), applied before routing.
  2. ML-research and Kaggle domain plugins with machine-readable evaluation.
  3. Improvement proposals driven by eval results, with approval and rollback; Sierra does this for CX only ([Sierra][si-exp]).

  These fit better as **plugins on Paperclip/LiteLLM/Langfuse** than as a new OS, which matches protocol hypotheses H3 and H4.
- **Licence constraints for hosting:** Dify's multi-tenant clause and n8n's SUL limit a managed cloud built on them ([Dify][dify-lic], [n8n][n8n-lic]). Prefer MIT or Apache substrates.
- **Solo-founder fit:** only a narrow OSS wedge measured on the operator's own workloads; a managed cloud would compete with Paperclip Cloud and Dify Cloud.

### AS06: adaptive AI OS for SMEs

- **Crowding: very high.** EU-hosted, multi-model workspaces with agents already sell at SME prices:
  - Langdock: €25/user, EU-hosted API, agent review and approval, EU AI Act templates ([pricing][ld-price]).
  - Dust: €24/seat, EU residency, self-serve for up to 100 people ([pricing][du-price]).
  - Mistral Vibe Team: $24.99/user ([Mistral][mi-vibe]).
  - Microsoft Copilot Business (secondary, [Nordflux][ms-smb]) and Gemini Enterprise Business (secondary, [guide][g-price]), both around $21.

  Enterprise governance is covered by Agent 365, Agentforce, ServiceNow, Frontier and Dataiku. "Dataiku-like but lower capture" describes Langdock and Dust today.
- **What remains open (absence UNVERIFIED):**
  1. A general SME loop that turns employee corrections into reviewable proposals with approval and rollback. Sierra productizes it for CX (vendor claim); Lindy and Beam claim it loosely ([Lindy][li-price], [Beam][beam]). Not found documented for Langdock or Dust.
  2. "One AI administrator" is a managed-service staffing model, not a product moat.
- **Regulatory constraint:** using corrections to evaluate individual employees risks Annex III 4(b) high-risk duties from 2027-12-02 ([Annex III][aiact-a3], [Haqq][aiact-omni]). Aggregate corrections per agent or task.
- **Solo-founder fit: low.** The business is sales-led and heavy on trust, support and compliance, against funded EU incumbents: Dust raised $40M ([TNW][du-b]); Langdock has an estimated $42M ARR ([Sacra][ld-sacra]). A correction-loop extension for an existing workspace or n8n is a speculative alternative.

**Uncertainty.** Traction figures are often estimates; absence findings rely on public pages; prices change monthly; there is no customer evidence. Paperclip Cloud could close the AS05 residual quickly.

[dk-hub]: https://www.dataiku.com/stories/blog/introducing-agent-hub
[dk-mesh]: https://www.dataiku.com/product/llm-mesh/
[dk-docs]: https://doc.dataiku.com/dss/latest/generative-ai/index.html
[dk-am]: https://siliconangle.com/2026/09/24/dataiku-debuts-cross-platform-agent-management-expands-cobuild-building-agent/
[dk-sacra]: https://sacra.com/c/dataiku/
[ms-a365]: https://www.microsoft.com/en-us/security/blog/2026/05/01/microsoft-agent-365-now-generally-available-expands-capabilities-and-integrations/
[ms-router]: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/model-router
[ms-smb]: https://nordflux.de/en/insights/copilot-licenses-and-costs
[sf-q1]: https://salesforce.com/news/press-releases/2026/05/27/fy27-q1-earnings
[sf-price]: https://www.supered.io/blog/agentforce-pricing/
[g-faq]: https://cloud.google.com/gemini-enterprise/faq
[g-inbox]: https://pasqualepillitteri.it/en/news/1431/gemini-enterprise-2026-agent-designer-inbox-practical-examples
[g-price]: https://workagent.ai/gemini-enterprise-pricing
[sn-ct]: https://eesel.ai/blog/servicenow-ai-pricing
[sn-mw]: https://newsroom.servicenow.com/press-releases/details/2025/ServiceNow-completes-acquisition-of-Moveworks/default.aspx
[sn-tier]: https://redresscompliance.com/servicenow-2026-pricing-tiers-pillar
[oa-fr]: https://techcrunch.com/2026/02/05/openai-launches-a-way-for-enterprises-to-build-and-manage-ai-agents/
[wr]: https://www.businesswire.com/news/home/20241112482564/en/Writer-Raises-200M-Series-C-at-1.9B-Valuation-to-Fuel-Leadership-in-Agentic-Enterprise-AI
[gl]: https://www.glean.com/press/glean-surpasses-300m-arr-unrivaled-enterprise-context-fuels-ai-adoption
[kore-art]: https://venturebeat.com/technology/kore-ai-launches-artemis-ai-agent-platform-expands-challenge-to-microsoft-and-salesforce
[kore-inv]: https://www.kore.ai/news/kore-ai-secures-strategic-growth-investment-from-alliancebernstein-to-scale-the-next-phase-of-agentic-enterprise-ai
[si-exp]: https://sierra.ai/product/explorer
[si-sacra]: https://sacra.com/c/sierra/
[dec]: https://www.finsmes.com/2026/01/decagon-raises-250m-in-series-d-funding.html
[ema]: https://finance.yahoo.com/technology/ai/articles/ema-raises-77m-series-b-130000096.html
[ld-price]: https://www.langdock.com/pricing
[ld-sacra]: https://sacra.com/c/langdock/
[du-price]: https://dust.tt/home/pricing
[du-b]: https://thenextweb.com/news/dust-series-b-40-million-multiplayer-ai-enterprise
[du-arr]: https://venturebeat.com/ai/dust-hits-6m-arr-helping-enterprises-build-ai-agents-that-actually-do-stuff-instead-of-just-talking
[du-gh]: https://github.com/dust-tt/dust
[li-price]: https://www.lindy.ai/pricing
[li-latka]: https://getlatka.com/companies/lindyai
[rel-b]: https://relevanceai.com/blog/the-ai-workforce-revolution-24m-series-b-to-accelerate-our-mission
[rel-p]: https://relevanceai.com/pricing
[zap]: https://a8gent.com/platforms/zapier-agents
[make]: https://www.make.com/en/ai-agents
[stack]: https://www.stackai.com/blog/stack-ai-raises-16m-series-a-to-create-ai-agents-for-every-job
[vel]: https://siliconangle.com/2025/07/11/enterprise-ai-development-platform-vellum-raises-20m-help-businesses-deploy-apps-faster/
[beam]: https://beam.ai/
[beam-pb]: https://pitchbook.com/profiles/company/512244-91
[art]: https://www.artisan.co/blog/artisan-series-a
[11x]: https://thecroreport.com/tools/11x/
[an-cw]: https://thenewstack.io/anthropic-takes-claude-cowork-out-of-preview-and-straight-into-the-enterprise/
[an-ma]: https://www.helpnetsecurity.com/2026/04/09/claude-managed-agents-bring-execution-and-control-to-ai-agent-workflows/
[an-cc]: https://code.claude.com/docs/en/claude-code-on-the-web
[mi-vibe]: https://mistral.ai/news/vibe-agent/
[mi-studio]: https://venturebeat.com/ai/mistral-launches-its-own-ai-studio-for-quick-development-with-its-european
[mi-fund]: https://valueaddvc.com/blog/mistral-ai-valuation-revenue-2026-europe-ai-champion
[mi-data]: https://help.mistral.ai/en/articles/347629-where-do-you-store-my-data-or-my-organization-s-data
[dify-gh]: https://github.com/langgenius/dify
[dify-lic]: https://github.com/langgenius/dify/blob/main/LICENSE
[dify-fund]: https://finance.yahoo.com/news/dify-raises-30-million-series-150000863.html
[n8n-gh]: https://github.com/n8n-io/n8n
[n8n-lic]: https://github.com/n8n-io/n8n/blob/master/LICENSE.md
[n8n-sap]: https://www.prnewswire.com/news-releases/n8n-valuation-doubles-to-5-2bn-as-sap-makes-strategic-investment-and-plans-to-embed-the-ai-platform-into-joule-studio-302767222.html
[fw-wd]: https://newsroom.workday.com/2025-08-14-Workday-Acquires-Flowise,-Bringing-Powerful-AI-Agent-Builder-Capabilities-to-the-Workday-Platform
[fw-gh]: https://github.com/FlowiseAI/Flowise
[lf-gh]: https://github.com/langflow-ai/langflow
[lf-ibm]: https://www.langflow.org/blog/big-news-for-langflow/
[lf-cve]: https://forkast.news/langflows-12th-exploited-cve-of-2026-fuels-sustained-credential-harvesting-campaign
[pc]: https://github.com/paperclipai/paperclip
[cu-help]: https://cursor.com/help/ai-features/background-agents
[cu-wiki]: https://en.wikipedia.org/wiki/Cursor_(company)
[cog]: https://chatforest.com/reviews/cognition-ai-devin-1-billion-round-26b-valuation-492m-arr-2026/
[fac]: https://continuumcode.ai/guides/factory-ai-funding/
[aug]: https://www.augmentcode.com/blog/augment-inc-raises-227-million
[gh-3p]: https://docs.github.com/en/copilot/concepts/agents/about-third-party-coding-agents
[codex]: https://www.constellationr.com/insights/news/openai-touts-broadening-codex-usage-5-million-weekly-active-users
[rep]: https://sacra.com/c/replit/
[lov]: https://valueaddvc.com/pulse/company/lovable
[aa-tc]: https://techcrunch.com/2026/04/25/why-cohere-is-merging-with-aleph-alpha/
[aa-tt]: https://www.techtimes.com/articles/327652/20260917/cohere-aleph-alpha-merger-locks-first-enterprise-ai-stack-outside-us-cloud-law.htm
[sw]: https://www.scaleway.com/en/docs/generative-apis/reference-content/data-privacy/
[ovh]: https://docs.ovhcloud.com/en/guides/public-cloud/ai-machine-learning/ai-endpoints-getting-started
[neb]: https://nebius.com/services/token-factory/enterprise-grade-inference
[aiact-a3]: https://artificialintelligenceact.eu/annex/3/
[aiact-omni]: https://www.haqq.ai/blog/eu-ai-act-amendments-2026.html
[aiact-gd]: https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/

## 4. Machine-readable actor list

```json
[
{"name":"Dataiku (Agent Hub, LLM Mesh, Agent Management)","website":"https://www.dataiku.com/product/agent-hub/","description":"Enterprise AI platform: governed agent building with templates and IT-approved agent library; LLM gateway with provider switching; Agent Management inventories agents on external platforms (GA Oct 2026).","relations":[{"idea":"AS06","relation":"benchmark","note":"The 'Dataiku-like out of the box' reference; enterprise-priced, no SME packaging."},{"idea":"AS05","relation":"benchmark","note":"LLM Mesh markets provider switching and performance routing; routing docs not found."}],"traction":"~$342M ARR Sep 2025 (estimate); $3.7B valuation 2022","traction_source":"https://sacra.com/c/dataiku/","license":"Proprietary; quote-only","checked_on":"2026-10-09"},
{"name":"Microsoft Agent 365 / Foundry model router / Copilot Studio","website":"https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/model-router","description":"Agent 365 governs Microsoft, partner and third-party agents; model router routes prompts across OpenAI/Anthropic/xAI/DeepSeek/Meta models within Azure Policy-governed subsets, honoring data zones.","relations":[{"idea":"AS05","relation":"benchmark","note":"Policy-constrained eligibility and routing already exists inside Azure; not across local/subscription runtimes."},{"idea":"AS06","relation":"alternative","note":"Copilot Business SMB bundle (~$21/user/mo, secondary)."}],"traction":"Agent 365 GA 2026-05-01 at $15/user/mo","traction_source":"https://www.microsoft.com/en-us/security/blog/2026/05/01/microsoft-agent-365-now-generally-available-expands-capabilities-and-integrations/","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Salesforce Agentforce","website":"https://www.salesforce.com/agentforce/","description":"CRM-centred agent platform.","relations":[{"idea":"AS06","relation":"alternative","note":"Only for Salesforce-centric organisations."}],"traction":">$1B Agentforce ARR, Q1 FY27 (company)","traction_source":"https://salesforce.com/news/press-releases/2026/05/27/fy27-q1-earnings","license":"Proprietary; Flex Credits $500/100k (secondary)","checked_on":"2026-10-09"},
{"name":"Google Gemini Enterprise","website":"https://cloud.google.com/gemini-enterprise/faq","description":"Workplace AI with prebuilt Google agents, no-code Agent Designer and agent Inbox (secondary).","relations":[{"idea":"AS06","relation":"alternative","note":"Business edition ~$21/seat (secondary)."}],"traction":"not found","traction_source":"https://workagent.ai/gemini-enterprise-pricing","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"ServiceNow AI Agents / AI Control Tower","website":"https://www.servicenow.com/","description":"Workflow agents; Control Tower governs agents incl. third-party (secondary); Moveworks acquired 2025-12-15.","relations":[{"idea":"AS06","relation":"alternative","note":"Enterprise only."}],"traction":"5.5M employee users across ServiceNow+Moveworks (company)","traction_source":"https://newsroom.servicenow.com/press-releases/details/2025/ServiceNow-completes-acquisition-of-Moveworks/default.aspx","license":"Proprietary; quote-only","checked_on":"2026-10-09"},
{"name":"OpenAI Frontier","website":"https://openai.com/","description":"Enterprise platform to build and manage 'AI coworkers', incl. agents built elsewhere; onboarding and feedback loop; limited availability.","relations":[{"idea":"AS06","relation":"benchmark","note":"Feedback-loop framing for agents; enterprise, not GA."},{"idea":"AS05","relation":"alternative","note":"Manages agents across vendors for large enterprises."}],"traction":"Named customers HP, Oracle, State Farm, Uber","traction_source":"https://techcrunch.com/2026/02/05/openai-launches-a-way-for-enterprises-to-build-and-manage-ai-agents/","license":"Proprietary; pricing undisclosed","checked_on":"2026-10-09"},
{"name":"Writer","website":"https://writer.com/","description":"Enterprise agentic AI platform with own models.","relations":[{"idea":"AS06","relation":"alternative","note":"Enterprise only."}],"traction":"$1.9B valuation, $200M Series C, Nov 2024","traction_source":"https://www.businesswire.com/news/home/20241112482564/en/Writer-Raises-200M-Series-C-at-1.9B-Valuation-to-Fuel-Leadership-in-Agentic-Enterprise-AI","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Glean","website":"https://www.glean.com/","description":"Enterprise search plus agent builder.","relations":[{"idea":"AS06","relation":"alternative","note":"Enterprise, search-first."}],"traction":">$300M ARR (company, 2026)","traction_source":"https://www.glean.com/press/glean-surpasses-300m-arr-unrivaled-enterprise-context-fuels-ai-adoption","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Kore.ai","website":"https://www.kore.ai/","description":"Enterprise agent platform (Artemis, May 2026); Agent 365 partner.","relations":[{"idea":"AS06","relation":"alternative","note":"Enterprise CX/EX."}],"traction":"Strategic growth investment led by AllianceBernstein, Jan 2026 (undisclosed)","traction_source":"https://www.kore.ai/news/kore-ai-secures-strategic-growth-investment-from-alliancebernstein-to-scale-the-next-phase-of-agentic-enterprise-ai","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Sierra","website":"https://sierra.ai/","description":"Enterprise CX agents; Explorer produces weekly improvement recommendations that Ghostwriter can implement with before/after comparison (vendor claim).","relations":[{"idea":"AS06","relation":"benchmark","note":"Productized corrections/insights-to-improvement loop, CX only."},{"idea":"AS05","relation":"benchmark","note":"Reference design for visible improvement proposals."}],"traction":"$15.8B valuation May 2026; ~$200M ARR (estimate)","traction_source":"https://sacra.com/c/sierra/","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Decagon","website":"https://decagon.ai/","description":"Enterprise CX agents.","relations":[{"idea":"AS06","relation":"benchmark","note":"CX only."}],"traction":"$4.5B valuation, $250M Series D, Jan 2026","traction_source":"https://www.finsmes.com/2026/01/decagon-raises-250m-in-series-d-funding.html","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Ema","website":"https://www.ema.ai/","description":"'Universal AI employee' agent platform for enterprises.","relations":[{"idea":"AS06","relation":"competitor","note":"Same AI-employee positioning, enterprise segment."}],"traction":"$77M Series B, $140M total, Sep 2026","traction_source":"https://finance.yahoo.com/technology/ai/articles/ema-raises-77m-series-b-130000096.html","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Langdock","website":"https://www.langdock.com/","description":"Berlin multi-model AI workspace: chat, agents, workflows, API over 40+ models; EU-hosted API; governance add-on with agent review/approval and EU AI Act/GDPR rule templates.","relations":[{"idea":"AS06","relation":"competitor","note":"Direct: EU, per-seat, governance; no documented correction-learning loop."}],"traction":"~$42M ARR Jun 2026 (estimate); ~$3.5M raised","traction_source":"https://sacra.com/c/langdock/","license":"Proprietary; EUR 25/99 per user/mo","checked_on":"2026-10-09"},
{"name":"Dust","website":"https://dust.tt/","description":"Paris multi-model team-agent platform with EU or US data residency; self-serve up to 100 people.","relations":[{"idea":"AS06","relation":"competitor","note":"Direct: EU residency, SME pricing; no correction-to-proposal loop found."}],"traction":"$40M Series B 2026; $6M ARR 2025","traction_source":"https://thenextweb.com/news/dust-series-b-40-million-multiplayer-ai-enterprise","license":"MIT repository; EUR 24/seat/mo (yearly)","checked_on":"2026-10-09"},
{"name":"Lindy","website":"https://www.lindy.ai/","description":"Assistant/agent platform with built-in approvals for outside-impact actions and editable memory.","relations":[{"idea":"AS06","relation":"competitor","note":"SMB AI employees; residency not stated; correction learning is vendor claim."}],"traction":"~$50M raised (estimate)","traction_source":"https://getlatka.com/companies/lindyai","license":"Proprietary; $29.99-$199.99/user/mo","checked_on":"2026-10-09"},
{"name":"Relevance AI","website":"https://relevanceai.com/","description":"No-code multi-agent 'Workforce'; pricing page now enterprise-only with evals and A/B testing.","relations":[{"idea":"AS06","relation":"competitor","note":"AI-workforce positioning; moved upmarket."}],"traction":"$24M Series B, May 2025","traction_source":"https://relevanceai.com/blog/the-ai-workforce-revolution-24m-series-b-to-accelerate-our-mission","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Zapier Agents","website":"https://zapier.com/agents","description":"Agents over Zapier's integration catalogue.","relations":[{"idea":"AS06","relation":"alternative","note":"Generic SME automation."}],"traction":"not found","traction_source":"https://a8gent.com/platforms/zapier-agents","license":"Proprietary; Pro ~$50/mo (secondary)","checked_on":"2026-10-09"},
{"name":"Make AI Agents","website":"https://www.make.com/en/ai-agents","description":"Agents inside Make scenarios, 3,000+ integrations.","relations":[{"idea":"AS06","relation":"alternative","note":"Generic SME automation."}],"traction":"not found","traction_source":"https://www.make.com/en/ai-agents","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"StackAI","website":"https://www.stackai.com/","description":"No-code enterprise agent builder.","relations":[{"idea":"AS06","relation":"alternative","note":"Enterprise builder."}],"traction":"$16M Series A, May 2025","traction_source":"https://www.stackai.com/blog/stack-ai-raises-16m-series-a-to-create-ai-agents-for-every-job","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Vellum","website":"https://www.vellum.ai/","description":"AI development platform (workflows, evaluation).","relations":[{"idea":"AS05","relation":"alternative","note":"Developer platform, not template OS."}],"traction":"$20M Series A, Jul 2025","traction_source":"https://siliconangle.com/2025/07/11/enterprise-ai-development-platform-vellum-raises-20m-help-businesses-deploy-apps-faster/","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Beam AI","website":"https://beam.ai/","description":"'Self-learning' process agents with human approval for critical tasks; EU or on-prem deployment (vendor claims).","relations":[{"idea":"AS06","relation":"benchmark","note":"Learning claim without documented reviewable proposals."}],"traction":"Unclear; $1.35M round Aug 2025 per PitchBook","traction_source":"https://pitchbook.com/profiles/company/512244-91","license":"Proprietary; quote-only","checked_on":"2026-10-09"},
{"name":"Artisan","website":"https://www.artisan.co/","description":"AI SDR 'employee' (Ava).","relations":[{"idea":"AS06","relation":"benchmark","note":"AI-employee framing, single function."}],"traction":"$25M Series A, Apr 2025","traction_source":"https://www.artisan.co/blog/artisan-series-a","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"11x","website":"https://www.11x.ai/","description":"AI SDR 'digital workers'.","relations":[{"idea":"AS06","relation":"benchmark","note":"Cautionary: reported customer-claim and churn issues (secondary)."}],"traction":"Benchmark/a16z-backed; reported credibility issues (secondary)","traction_source":"https://thecroreport.com/tools/11x/","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Anthropic Claude Cowork / Managed Agents / Claude Code cloud sessions","website":"https://claude.com/product/cowork","description":"Cowork GA with RBAC, spend limits, OTel; Managed Agents hosted sandboxed runtime (public beta); Claude Code cloud sessions in isolated VMs.","relations":[{"idea":"AS05","relation":"partner","note":"Runtime/provider; single-vendor alternative for technical teams."},{"idea":"AS06","relation":"alternative","note":"Team/Enterprise seats bundle agents for employees."}],"traction":"Cowork GA 2026-04-09","traction_source":"https://thenewstack.io/anthropic-takes-claude-cowork-out-of-preview-and-straight-into-the-enterprise/","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Mistral AI (Vibe, AI Studio)","website":"https://mistral.ai/","description":"Vibe (ex-Le Chat) Work Mode proposes plans and waits for approval; AI Studio offers runtime, observability, registry with promotion gates, self-hosted option; EU hosting by default.","relations":[{"idea":"AS06","relation":"competitor","note":"EU workspace at ~$24.99/user/mo Team; Mistral-model centric."},{"idea":"AS05","relation":"partner","note":"EU-resident model provider; AI Studio also a benchmark."}],"traction":"EUR 3B Series D Sep 2026 at >EUR 21B (secondary)","traction_source":"https://valueaddvc.com/blog/mistral-ai-valuation-revenue-2026-europe-ai-champion","license":"Proprietary platform; some open-weight models","checked_on":"2026-10-09"},
{"name":"Dify","website":"https://dify.ai/","description":"Open-source visual agentic workflow and RAG platform with Cloud, self-hosted and Enterprise editions.","relations":[{"idea":"AS05","relation":"partner","note":"Possible substrate, but multi-tenant hosting needs written authorization."},{"idea":"AS06","relation":"alternative","note":"Self-hostable builder for SMEs with IT staff."}],"traction":"158k GitHub stars; $30M pre-A at $180M valuation, Mar 2026","traction_source":"https://github.com/langgenius/dify","license":"Dify Open Source License (Apache-2.0 + multi-tenant and logo conditions)","checked_on":"2026-10-09"},
{"name":"n8n","website":"https://n8n.io/","description":"Fair-code workflow automation with AI agents, provider switching and human approvals.","relations":[{"idea":"AS06","relation":"alternative","note":"SME automation incumbent; SAP-embedded."},{"idea":"AS05","relation":"partner","note":"Integration target; SUL limits hosting it for others."}],"traction":"206.8k stars; $5.2B valuation; 1,400+ enterprise customers (2026-05-12)","traction_source":"https://www.prnewswire.com/news-releases/n8n-valuation-doubles-to-5-2bn-as-sap-makes-strategic-investment-and-plans-to-embed-the-ai-platform-into-joule-studio-302767222.html","license":"Sustainable Use License + n8n Enterprise License (.ee)","checked_on":"2026-10-09"},
{"name":"Flowise","website":"https://github.com/FlowiseAI/Flowise","description":"Visual agent builder; acquired by Workday Aug 2025; repository archived.","relations":[{"idea":"AS05","relation":"benchmark","note":"Cautionary: visual builder discontinued after acquisition."}],"traction":"55.5k stars; archived","traction_source":"https://github.com/FlowiseAI/Flowise","license":"Apache-2.0","checked_on":"2026-10-09"},
{"name":"Langflow","website":"https://www.langflow.org/","description":"Open-source visual agent/workflow builder owned by IBM via DataStax.","relations":[{"idea":"AS05","relation":"partner","note":"MIT substrate option; 2026 CVE exploitation reported (secondary)."}],"traction":"155k GitHub stars","traction_source":"https://github.com/langflow-ai/langflow","license":"MIT","checked_on":"2026-10-09"},
{"name":"Paperclip","website":"https://github.com/paperclipai/paperclip","description":"Open-source orchestration for teams of AI agents: org charts, Ready-Made Teams, budgets with auto-pause, approval stages, plugins, adapters for Claude Code/Codex/Cursor/Gemini CLI; Paperclip Cloud waitlist.","relations":[{"idea":"AS05","relation":"competitor","note":"Closest overlap and intended substrate; lacks documented residency-aware eligibility, domain evals and improvement proposals."},{"idea":"AS06","relation":"alternative","note":"For technical SMEs only."}],"traction":"~99.1k GitHub stars","traction_source":"https://github.com/paperclipai/paperclip","license":"MIT","checked_on":"2026-10-09"},
{"name":"Cursor (Anysphere, SpaceX)","website":"https://cursor.com/","description":"AI IDE with cloud agents in isolated VMs that open PRs.","relations":[{"idea":"AS05","relation":"alternative","note":"Covers the software-engineering template; also a runtime to orchestrate."}],"traction":"~$3B ARR May 2026; acquired by SpaceX at implied $60B, closed 2026-08-14 (Wikipedia, flagged)","traction_source":"https://en.wikipedia.org/wiki/Cursor_(company)","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Cognition (Devin, Windsurf)","website":"https://cognition.ai/","description":"Autonomous software-engineering agent and IDE.","relations":[{"idea":"AS05","relation":"alternative","note":"Software-engineering template incumbent."}],"traction":"$26B valuation, $492M run-rate, May 2026 (secondary)","traction_source":"https://chatforest.com/reviews/cognition-ai-devin-1-billion-round-26b-valuation-492m-arr-2026/","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Factory","website":"https://factory.ai/","description":"Enterprise coding agents ('Droids').","relations":[{"idea":"AS05","relation":"alternative","note":"Software-engineering template incumbent."}],"traction":"$150M Series C at $1.5B, Apr 2026; $5B round unconfirmed (secondary)","traction_source":"https://continuumcode.ai/guides/factory-ai-funding/","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Augment Code","website":"https://www.augmentcode.com/","description":"Coding agent with codebase context engine.","relations":[{"idea":"AS05","relation":"alternative","note":"Software-engineering template incumbent."}],"traction":"$227M Series B at $977M, 2024","traction_source":"https://www.augmentcode.com/blog/augment-inc-raises-227-million","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"GitHub Copilot cloud agent + Agent HQ","website":"https://docs.github.com/en/copilot/concepts/agents/about-third-party-coding-agents","description":"Assign tasks to Copilot, Claude or Codex agents on GitHub; third-party agents in public preview, enabled by admin policy.","relations":[{"idea":"AS05","relation":"alternative","note":"Multi-agent hub for software engineering; GitHub-centric."}],"traction":"not found","traction_source":"https://docs.github.com/en/copilot/concepts/agents/about-third-party-coding-agents","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"OpenAI Codex","website":"https://openai.com/codex/","description":"Cloud and CLI coding agent.","relations":[{"idea":"AS05","relation":"partner","note":"Runtime to orchestrate; also an alternative for SWE tasks."}],"traction":">5M weekly users, Jun 2026 (vendor-reported)","traction_source":"https://www.constellationr.com/insights/news/openai-touts-broadening-codex-usage-5-million-weekly-active-users","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Replit","website":"https://replit.com/","description":"Prompt-to-app agent platform.","relations":[{"idea":"AS06","relation":"alternative","note":"Adjacent: SMEs building internal apps."}],"traction":"$9B valuation, Mar 2026 (estimate)","traction_source":"https://sacra.com/c/replit/","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Lovable","website":"https://lovable.dev/","description":"Prompt-to-app agent platform.","relations":[{"idea":"AS06","relation":"alternative","note":"Adjacent: SMEs building internal apps."}],"traction":"$13.3B valuation Aug 2026; >$500M ARR (secondary)","traction_source":"https://valueaddvc.com/pulse/company/lovable","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Aleph Alpha (PhariaAI) / Cohere","website":"https://aleph-alpha.com/","description":"Sovereign AI compliance/deployment platform; Cohere agreed to acquire with Schwarz Group backing and STACKIT hosting; closing unconfirmed.","relations":[{"idea":"AS05","relation":"partner","note":"Sovereign provider option."},{"idea":"AS06","relation":"partner","note":"Sovereign provider option for regulated SMEs."}],"traction":"Reported ~$20B combined valuation (secondary)","traction_source":"https://techcrunch.com/2026/04/25/why-cohere-is-merging-with-aleph-alpha/","license":"Proprietary","checked_on":"2026-10-09"},
{"name":"Scaleway Generative APIs","website":"https://www.scaleway.com/en/generative-apis-signup/","description":"Serverless open-model inference; data in Paris region.","relations":[{"idea":"AS05","relation":"partner","note":"EU-resident provider for policy-constrained eligibility."}],"traction":"not found","traction_source":"https://www.scaleway.com/en/docs/generative-apis/reference-content/data-privacy/","license":"Proprietary service","checked_on":"2026-10-09"},
{"name":"OVHcloud AI Endpoints","website":"https://www.ovhcloud.com/","description":"Serverless open-weight models hosted in Europe; states it does not store user data (vendor claim).","relations":[{"idea":"AS05","relation":"partner","note":"EU-resident provider."}],"traction":"not found","traction_source":"https://docs.ovhcloud.com/en/guides/public-cloud/ai-machine-learning/ai-endpoints-getting-started","license":"Proprietary service","checked_on":"2026-10-09"},
{"name":"Nebius Token Factory","website":"https://nebius.com/services/token-factory/enterprise-grade-inference","description":"Open-model inference with Finland/France/US data centres and zero-retention mode.","relations":[{"idea":"AS05","relation":"partner","note":"EU-resident provider option (EU or US regions)."}],"traction":"not found","traction_source":"https://nebius.com/services/token-factory/enterprise-grade-inference","license":"Proprietary service","checked_on":"2026-10-09"}
]
```
