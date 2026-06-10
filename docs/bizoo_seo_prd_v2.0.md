# Bizoo SEO Engine PRD v2.0 (Consolidated)

**Status:** Canonical. Supersedes v1.1 (April 2026), v1.2 (GEO Addendum), and v1.3 (Planning Layer Addendum) in full. Where earlier versions conflicted, this document resolves the conflict. No other Bizoo SEO document is authoritative.
**Author:** Amir
**Date:** May 2026
**Companion documents:** Bizoo CRM Spec (carried within this doc, §10), Bizoo Product PRD (separate, Kam-owned, not yet written; see Decision Gate DG-1).

---

## 1. Vision & Strategic Frame

Bizoo (getbizoo.com) is a diligence-first financial operating system for founders, PE analysts, M&A practitioners, CFOs, and business buyers/sellers, now expanding into a founder-grade planning layer (scenario planning + what-if, runway and cash visibility, plain-language driver formulas).

The SEO engine's job is not to rank pages. It is to make Bizoo the cited source when an AI answers a founder's or PE associate's question, and to convert that citation into product signups through interactive surfaces AI cannot replicate.

**Why citation, not rank.** As of early 2026, AI Overviews appear in 50 to 60% of US searches (up from 6.49% in January 2025). Only 38% of cited pages rank in the top 10 organic results, down from 76% seven months earlier. Domain Authority correlation with citation has collapsed to r=0.18. Cited pages earn 35% more organic clicks and 91% more paid clicks than non-cited competitors on the same SERP. On April 29, 2026, Google replaced the Android Search button with "Ask Google." The rank game is half-dead; the citation game is the game.

**The positioning spine (carried on every artifact):**

> "The model you plan with is the model you get diligenced on."

- Runway Financial helps founders plan. Their model dies at the data room door: when diligence starts, buyers' analysts rebuild everything and tear apart every assumption.
- mosaic.pe helps buyers tear plans apart. Nothing for the founder side.
- Bizoo is the only tool where the planning model is diligence-ready by construction.

**Naming discipline:** Bizoo is never marketed as "an FP&A platform." That framing invites a feature-checklist comparison against Runway's 750+ integrations and Ambient Intelligence, which Bizoo loses. The category is "diligence-ready planning," which has exactly one entrant.

---

## 2. KPIs

| Tier | KPI | Definition | Target |
|---|---|---|---|
| Primary | **Citation Share** | % of tracked queries where Bizoo is cited in AI Overview / AI Mode / Perplexity, reported per pillar | Original 4 pillars: 8 to 12% by wk 12, 20 to 25% by mo 6, 35 to 45% by mo 12. Plan pillar (separate ramp): 5% by wk 12, 15% by mo 6 |
| Secondary | **Brand Mention Velocity** | Indexed third-party mentions of Bizoo/getbizoo.com per month, authority-weighted | Trend up; reviewed monthly |
| Secondary | **Tool-to-Signup Rate** | Cited page → tool session → email capture → signup | 400+ monthly tool sessions, 8 to 12% email capture by wk 12 of planning launch |
| Tertiary | **Branded Query CTR** | GSC CTR on Bizoo-branded queries | Measurable by wk 12 |
| Tracked, not optimized | Domain Authority, raw rank positions | Legacy signals | Secondary dashboard view only |
| Long-range | Programmatic page traffic | GA4 + GSC | 1,000+/mo sessions by M12, signup conversion tracked toward 1%+ |

**Anti-goals (zero priority weight in Agent 12):** "FP&A software" head terms, Runway-brand-dominated queries where they hold the citation, any query whose searcher mental model is "I have a finance team and need their tooling."

---

## 3. The 2026 Ranking Signal Map

The model the entire engine optimizes against, from the largest published GEO studies as of May 2026:

| Signal | Strength | Engine response |
|---|---|---|
| Semantic completeness (134 to 167 word self-contained answer) | r=0.87 | Mandatory extractable passage atop every page (Agent 04 brief format) |
| Multimodal integration (text + image + video + schema) | r=0.92, +156% selection, up to +317% with full schema | Three-pipeline architecture (§5); programmatic pages multimodal by default |
| E-E-A-T + author credentials | 96% of citations carry strong signals | Person schema, bylines, Amir/Kam credential pages, honest competitor concessions |
| Entity density (15+ recognized entities / 1,000 words) | 4.8x selection probability | Agent 15 enforcement floor on every publish |
| Fact verification (recent stats, Tier-1 sources) | +89% selection | Source-citation discipline in briefs; freshness timestamps |
| Brand mentions (off-site) | Strongest correlation in Ahrefs 75K-brand study (with YouTube) | Pipeline C (X) + PR layer |
| YouTube transcript signals | Strongest single channel; wins via query fan-out | Pipeline B |
| FAQ + HowTo + Article schema | High extractability | Mandatory on every page |

---

## 4. Competitive Landscape

**Front 1: Diligence. Direct competitor: mosaic.pe** (LBO/deals analysis, mega-fund PE Associate testimonials). Content surface thin, no meaningful YouTube presence, building product depth not search depth. The citation window is open; every week of compounding raises their displacement cost.

**Front 2: Planning. Direct competitor: Runway Financial** (runway.com, $33.5M from a16z/Initialized, 20x revenue growth into 2024, 750+ integrations, unlimited seats, ICP = finance teams at $1M to $50M ARR). We do not fight them on entrenched queries. The structural opening: pre-$1M ARR, pre-finance-hire founders are outside their ICP and exactly inside ours. Ambient Intelligence is deliberately out of Bizoo scope; comparison content concedes it immediately and reframes (their intelligence explains what already happened; Bizoo's engine tells you what a buyer will say before you meet one).

**Not a competitor: mosaic.tech** (San Diego Series C FP&A for mid-market finance teams; competes with Cube/Planful/Datarails). Tracked for disambiguation only. Agent 15 verifies entity resolution so "Mosaic" cites resolve to mosaic.pe in our content.

**The real competitor at the bottom of market: spreadsheets.** Excel/Google Sheets, addressed via the /vs/spreadsheets sleeper page (§8).

**Tracked competitor list (Agent 01 / Agent 12):** mosaic.pe, runway.com, causal.app, visible.vc, finmark.com, mosaic.tech (disambiguation), cube.inc, liveplan.com.

---

## 5. Architecture Overview

### 5.1 Three Content Pipelines, One Source

**Source substrate:** the weekly Bizoo Loop call (Amir + Kam, 45 to 60 min, recorded, transcribed), mirroring AMG's v8.3 transcript-first model. Standing agenda segment: "one driver, explained" (5 min, Kam), which alone feeds a glossary page review, a video, and 2 X posts weekly. One call produces one cluster: a 2,500-word pillar page, a 5-minute video, 3 to 5 X posts, and one proprietary framework or data point.

- **Pipeline A: Technical Citation.** Text-first, schema-heavy, extractable. Pillar pages, editorial, /vs/ pages, glossary. Owns ContentPages.
- **Pipeline B: Video Citation.** YouTube-first, 3 to 8 minute explainers optimized for query fan-out (Google's AI decomposes queries into sub-questions; YouTube videos rank for the sub-questions even when invisible on the head query). View count is not the goal; indexing and citation are. Owns Videos.
- **Pipeline C: Social Signal.** X-first, founder personal accounts (Amir primary, Kam secondary), never @getbizoo as lead. Feeds brand mention velocity and sameAs entity confirmation. No automated posting, every post human-approved. Owns SocialMentions.

### 5.2 Five Query Pillars (~340 CitationTargets)

Ingest, Model, Monitor, Execute (original ~200 queries) + **Plan** (~140 queries, four families):

1. Scenario planning intent (~45): "scenario planning software for startups," "what-if analysis financial model," "downside scenario planning for fundraising"
2. Cash runway intent (~40): "how to calculate cash runway," "startup runway calculator," "how many months of runway before raising"
3. Driver/formula definitional intent (~35): "what is driver-based planning," "burn multiple definition," "CAC payback driver"
4. Competitive/commercial intent (~20): "Runway Financial alternative," "best financial planning tool for pre-seed startups," "financial planning software for companies under $1M ARR"

Priority tracking (6-hour AI Mode loop): Family 4, Family 2, plus the top 50 original-pillar commercial queries.

### 5.3 Infrastructure

Shared with AMG: DigitalOcean droplet (Bizoo isolated at /home/bizoo/engine/, AMG at /home/amg/engine/), n8n instance (separate workflow folder namespace), DataForSEO account, GSC service account pattern (getbizoo.com property added to the existing service account at /home/amg/gsc_service_account.json). Migration triggers per the documented July 19, 2026 hard date or earlier on specific triggers.

Bizoo-only: Bizoo SEO Airtable base, Bizoo CRM Airtable base (separate from product base appiXBfiQPeWsWLm5), Next.js on Vercel (getbizoo.com, root-domain path routing, never subdomains: authority consolidates), Loops.so email (free tier to 1,000 contacts), PostHog self-hosted on DO, Claude API (Sonnet) for brief/script/page generation, SerpAPI, Perplexity API, YouTube Data API v3, spaCy + entity linker (self-hosted).

Slack channels: #bizoo-seo, #bizoo-crm, #bizoo-x-queue (Notion-backed approval queue for X drafts).

### 5.4 Airtable: Bizoo SEO Base (12 tables)

| Table | Fed by | Read by |
|---|---|---|
| Keywords | Agent 01, Agent 05 | Agent 04 |
| ContentBriefs | Agent 04 | Human execution |
| ContentPages | Human on publish + Agent 03 + WF-02 conversions++ | Agents 03, 04, 07, 15, WF-02 |
| TechnicalAudit | Agents 02, 10 | Manual review |
| LinkProspects | Agent 06 | Manual outreach |
| Deals | Agent 08 | Agent 09 |
| ProgrammaticPages | Agent 09 | Agent 11 |
| InternalLinks | Agent 11 | Developer implementation |
| CitationTargets | Manual seed + Agent 12 maintenance | Agent 12, 13 |
| AIOverviewCitations | Agent 12 | Reporting, Agent 13 |
| Videos / VideoBriefs | Agent 13 | Agent 11, human recording |
| SocialMentions | Agent 14 | Reporting |
| Drivers | Kam's engine documentation seed | Agent 09 (glossary template) |

---

## 6. Agent Specifications (15 Agents, 4 Phases)

All agents: Python, on the DO droplet, n8n-orchestrated, Airtable as data layer, Slack for alerts. Dual GitHub remote sync (AmirGetsJobs org + ahaider24) after every code change, no exceptions.

### Phase 1: Foundation (target: live May 2026)

**Agent 01 — Keyword Intelligence.** Weekly cron (Mon 6:00 AM). Pulls DataForSEO Rank Tracker + GSC Search Analytics for getbizoo.com, runs competitor keyword intersection (positions 1 to 30 where Bizoo is absent) against the §4 competitor list, scores opportunities (volume × 1/competition × relevance weight), writes top 20 to Keywords with status Queued. Slack digest: movers, opportunities, competitor alerts. Feeds Agent 04.

**Agent 02 — Technical SEO Auditor.** Bi-weekly crawl of getbizoo.com: Core Web Vitals, canonicals, internal link health, sitemap freshness, schema validity, GSC index coverage. Critical because Next.js/Vercel SSR edge cases, dynamic routes (deals + drivers), and ISR can introduce crawlability regressions silently. Writes to TechnicalAudit.

**Agent 03 — Performance Monitor (rebuilt in v2.0).** Reports the §2 KPI stack first: Citation Share per pillar (from Agent 12 data), Brand Mention Velocity (from Agent 14 data), Tool-to-Signup (from PostHog/CRM), Branded CTR (GSC). Rank tracking demoted to a secondary view. Weekly report to #bizoo-seo.

### Phase 2: Topical Authority (target: live June to July 2026)

**Agent 04 — Content Brief Generator.** Consumes Keywords queue + CitationTargets + conversion signals (WF-02 writes conversions++ back to ContentPages, making this agent self-directing over time). Every brief mandates: (a) a 134 to 167 word extractable answer opening the page, self-contained, no preamble; (b) a 20 to 30 entity target list; (c) a 5 to 8 question FAQ section formatted for schema; (d) a video companion flag for Pipeline B; (e) the diligence spine woven in. Claude API generation, human execution.

**Agent 05 — Competitor Gap Scanner.** Monthly scan of the §4 competitor list for net-new pages, topic launches, and citation wins (cross-referenced with Agent 12 data). Writes gaps to Keywords.

**Agent 06 — Backlink Intelligence.** Identifies link prospects (podcasts, finance newsletters, founder communities), writes 50+/mo to LinkProspects for manual outreach. Slow-build, started early.

**Agent 07 — Landing Page Optimizer.** Audits every ContentPages entry for v2.0 compliance: extractable passage (y/n), entity density count, schema coverage (FAQ + HowTo + Article + Person + sameAs), multimodal elements (image, video embed, table, chart). Produces a 0 to 100 compliance score; pages under 70 queue for rewrite.

### Phase 3: Programmatic Engines (target: prototype August, live September 2026)

**Agent 08 — Deal Data Ingestion.** Ingests public M&A transaction data daily into Deals. Quality threshold: 60% data completeness minimum to generate a page (no thin pages).

**Agent 09 — Programmatic Page Generator.** Two templates, both GitHub-PR-gated with human review on the first 100 pages per template, Vercel auto-deploy on merge:
- *Deals template:* /deals/[slug], /comps/[industry], /acquirers/[firm]. Multimodal by default: structured comparison table, server-rendered chart from deal data, 3-question FAQ schema, 5 to 8 Agent 11 internal links.
- *Driver Glossary template (the product-SEO convergence play):* /drivers/[term], seeded from the Drivers table (80 to 120 terms from Kam's engine documentation). Each page: the product's own plain-language definition as the extractable passage (product copy IS the SEO content, zero marginal cost), the formula in traditional notation and Bizoo readable syntax side by side (itself a product demo), a worked example, a "how buyers scrutinize this in diligence" section (the spine; the section Investopedia and Runway docs cannot write), FAQ schema, and an inline calculator where the term permits (runway, burn multiple, CAC payback). Definitional queries are the heaviest AI Overview trigger category and incumbents have no product behind their pages.

**Agent 10 — Schema Agent.** Generates and validates structured data across all page types. Tested on 10 sample deal pages before Agent 09 goes autonomous.

**Agent 11 — Internal Linking Intelligence.** Maintains the link graph: every glossary page links to its parent pillar and relevant /vs/ page; every deal page links to 5 to 8 related pages; videos cross-linked into relevant pages on publish.

### Phase 4: GEO Layer (deploy weeks 1 to 6 of v2.0 execution)

**Agent 12 — AI Overview Citation Tracker.** Every 6 hours. For each of ~340 CitationTargets: SerpAPI AI Overview capture + cited URL parse, Perplexity API citation capture, AI Mode tracking on the priority subset. Logs cited domains, citation position, Bizoo presence, competitor presence. Computes Citation Share daily/weekly/monthly per pillar. Slack alert on any citation state change. Also logs (without prioritizing) the §2 anti-goal queries for competitive awareness, including early warning if Runway begins targeting diligence-prep queries.

**Agent 13 — Video Citation Pipeline Orchestrator.** Weekly, on Loop transcript availability. Extracts 1 to 3 video topics scored on query fan-out potential (Plan-pillar topics get a scoring boost for the first 12 weeks post-planning-launch). Generates script (hook 15s, framework 60s, three named entities/concepts 120 to 240s each, CTA with branded query 15s; 6 to 8 min total) and full metadata package (query-verbatim title, 200 to 400 word entity-rich description with getbizoo.com links, 8 to 12 chapter markers, timestamped transcript, tags). Human records (Loom solo / Riverside duo; Descript or Opus Clip editing to 25-video catalog, then contract editor). Standing series: "Drivers, Explained" (3 to 4 min, Kam-fronted; his credentials feed the E-E-A-T author signal). Post-publish: ingests YouTube URL, scrapes transcript for entities, writes to Videos.

**Agent 14 — X Mention Engine.** Daily generation, real-time monitoring. Monitors X for Bizoo, competitor names, topical anchors; logs to SocialMentions. Drafts 5 to 8 posts/week for Amir (including the build-in-public planning-layer thread series: screenshots, formula syntax reveals) and 2 to 3 for Kam (formula syntax design decisions; finance Twitter engages notation arguments at disproportionate rates). Surfaces 3 to 5 conversations weekly for substantive founder participation (entity association, not promotion). All drafts to #bizoo-x-queue for human approval. Both X profiles listed as sameAs in Organization schema.

**Agent 15 — Entity Density Optimizer.** Runs on every Agent 04 brief completion, every Agent 09 generation, and a monthly ContentPages sweep. NER via spaCy + entity linker (Claude API for high-confidence linking). Enforces the 15 entities/1,000 words floor, suggests specific entity insertions with placement, verifies disambiguation (Mosaic → mosaic.pe; Runway the metric vs Runway the company vs Rent the Runway). Writes density score to ContentPages.

---

## 7. Click Generation Layer

Citation is visibility; clicks are revenue. AI Overviews cut CTR ~61% for non-cited pages, and even cited pages need a click reason.

1. **Branded query targeting.** "Bizoo vs X" and feature-specific branded pages, owned by definition once awareness exists.
2. **Interactive tools (now product demos, not lead magnets).** Priority order: (i) Founder Cash Runway Tool, a stripped live demo of the shipped cash-visibility feature, email-gated, PostHog tool_session event wired to WF-02; (ii) Quality of Earnings checklist generator (Kam-authored, his QoE framework); (iii) LBO model preview (three inputs, Bizoo output, email-gated). Linked from every relevant cited page. AI can summarize the page; the user must click to use the tool.
3. **Proprietary data drops.** "The Bizoo Founder Finance Index," quarterly: survey 200 to 500 founders on cash position, runway anxiety, time-to-diligence-readiness. Original data is a citation magnet (sites with original data gained 22% visibility in the March 2026 core update) and nobody else has this dataset.
4. **High commercial intent capture.** The 30 to 50 buy/evaluate queries ("Runway Financial alternative," "best diligence software for founders") get priority Pipeline A coverage.

---

## 8. Comparison Page Strategy (Product Claim Pages)

All /vs/ pages share the structure: 150-word extractable verdict up top, honest feature table with explicit concessions (honesty passes AI fact-verification; one-sided pages fail it), reframe section, embedded interactive widget (the unreplicable click reason).

- **/vs/runway-financial:** Concede Ambient Intelligence and integration breadth immediately. Reframe: "what Runway can't tell you: what a buyer will say." Embedded mini scenario-comparison widget on Bizoo's real engine.
- **/vs/mosaic-pe:** "mosaic.pe is what the buyer uses. Bizoo is how you show up prepared for it."
- **/vs/spreadsheets (sleeper priority):** The real bottom-of-market competitor. Hero: plain-language formulas ("formulas you can read") vs nested Excel hell. High volume, low competition from either funded incumbent.
- Legacy roadmap pages /vs/causal et al. proceed per the Phase 2 timeline.

---

## 9. Risks

| # | Risk | Counter |
|---|---|---|
| R1 | Category confusion ("so you're an FP&A tool?") invites feature-checklist losses | The spine, enforced on every artifact; immediate honest concessions then reframe |
| R2 | Runway targets diligence-prep queries with superior budget | Unlikely on 12-month horizon (irrelevant to their ICP, roadmap energy on AI features); Agent 12 provides free early warning |
| R3 | Glossary commoditization by Investopedia-class incumbents or AI-native copycats | The diligence-scrutiny section nobody else can write, inline calculators nobody static can match, first-mover citation compounding |
| R4 | Product-content timing mismatch (traffic into features that can't catch it) | Hard rule: content for a feature cluster publishes no more than 2 weeks before usable beta |
| R5 | X output reads bot-authored, signal devalued | No automated posting, human approval on every post, founder accounts only |
| R6 | Programmatic thin-page risk | 60% data completeness floor, PR-gated review on first 100 pages per template, week-12 quality gate before scale |

---

## 10. CRM & Attribution Layer (carried from v1.1, unchanged except noted)

**Bizoo CRM Airtable base** (separate from product base appiXBfiQPeWsWLm5). Six tables: Contacts, Leads, SEO Attribution, AMG Cross-connect, Pipeline, Nurture Sequences.

Four n8n workflows:
- **WF-01 Landing Page Intake:** getbizoo.com form (Cloudflare Turnstile validation unchanged) writes to Contacts + Leads.
- **WF-02 SEO Attribution Enricher:** the architectural centerpiece. Attributes signups to source pages and writes conversions++ back to ContentPages, making Agent 04 self-directing. v2.0 addition: consumes the PostHog tool_session event for Tool-to-Signup cohort tracking.
- **WF-03 AMG Cross-connect Sync:** prerequisite, AMG base field mapping confirmation.
- **WF-04 Stage Advancement + Stripe Sync:** Stripe webhook (customer.created, invoice.payment_succeeded/failed, subscription.updated/deleted) drives pipeline stages; PostHog /pricing view fires MQL trigger.

Email: Loops.so (sequence logic in Loops, n8n fires events only). Sequences: LP Onboarding, AMG Cross-sell, Trial Activation.

---

## 11. Consolidated Roadmap

Two parallel tracks. Track 1 (Foundation/Authority/Programmatic) follows the original phase calendar. Track 2 (GEO + Planning) runs the v1.2/v1.3 90-day plans concurrently.

**May 2026**
- Agents 01, 02, 03 live. WF-01, WF-03, WF-04 live.
- Agent 12 live: CitationTargets seeded to ~340 (Plan pillar included), baseline Citation Share measured BEFORE any new content ships.
- Top 8 existing landing pages rewritten with extractable passages + full schema. Person + sameAs schema live on the Organization page.
- Drivers table seeded from Kam's documentation (80+ terms minimum). DG-2 resolved first.

**June 2026**
- Agents 04, 05 live; first 10 briefs in v2.0 format; WF-02 live.
- Agents 13, 14, 15 deployed. First 4 Loop calls recorded; first 4 videos shipped; X cadence live on Amir's account; full ContentPages entity sweep.
- /vs/runway-financial and /vs/spreadsheets briefs written.

**July 2026 (gated on planning-feature usable beta, R4 rule)**
- Agents 06, 07 live. /vs/causal, /vs/runway-financial, /vs/mosaic-pe published.
- Glossary template QA'd on first 15 pages; first 40 glossary pages + 3 Plan pillar pages live.
- Founder Cash Runway Tool relaunched as product demo; tool_session wired.
- "Drivers, Explained" episodes 1 to 4.

**August 2026**
- Agent 08 prototype, Deals populating. Dynamic routes scaffolded. Agent 10 tested on 10 sample deals.
- Glossary at 80+ pages. Week-12 GEO checkpoint: original pillars at 8 to 12% Citation Share; Plan pillar reviewed against 5%; if Plan under 3%, halt page additions and run Agents 07 + 15 audit sweep (volume without citation is the failure mode).
- First Bizoo Founder Finance Index (Q3 2026) shipped: landing page + email gate, X + video distribution.

**September 2026**
- Agent 09 live (PR-gated). First 50 deal pages published, index rate measured, Claude prompt calibrated.
- Tool-to-Signup first cohort review in CRM.

**October to December 2026**
- Agent 11 live. Autonomous daily deal pipeline post-100-page validation. Acquirer + Comps page sets. 500+ programmatic pages.
- SEO-sourced MRR tracking live, reviewed monthly.
- Month-6 targets: original pillars 20 to 25% Citation Share, Plan pillar 15%.

**Month 12 horizon:** 35 to 45% Citation Share on original pillars, at which point the content gap becomes a structural disadvantage neither mosaic.pe nor a late-moving Runway closes in under 12 months.

---

## 12. Decision Gates (formerly "open questions": each now has an owner, a deadline, and a default)

| ID | Decision | Owner | Deadline | Default if undecided |
|---|---|---|---|---|
| DG-1 | Bizoo Product PRD for the three planning clusters (separate doc) | Kam (Amir on GTM sections) | Before July gate | July content publishing HALTS per R4 |
| DG-2 | Does Kam's engine documentation exist in extractable form for the Drivers seed? | Kam | May, week 2 | Loop-call "one driver, explained" becomes the seeding mechanism; glossary timeline stretches 6 wk → 12 wk |
| DG-3 | Video editing ownership, first 90 days | Amir | Before first recording | Amir + Descript; contract editor at 25-video catalog |
| DG-4 | Kam co-authors X posts or is quoted in Amir's | Kam | June | Quoted in Amir's (lower coordination cost) |
| DG-5 | Founder Finance Index distribution: Substack vs landing page + email gate | Amir | Before August | Landing page + email gate (no new platform overhead) |
| DG-6 | Branded-query seeding budget pre-flywheel (months 1 to 3) | Amir | June | $500 to $1,500/mo LinkedIn test against PE associate audiences |
| DG-7 | Reddit as a fourth pipeline (r/FinancialCareers, r/private_equity; Reddit citation share growing) | Amir | Month-6 checkpoint | Deferred unless Citation Share stalls |
| DG-8 | Programmatic page domain placement | RESOLVED | n/a | Root domain, path-based routing (authority consolidation) |
| DG-9 | Deal page quality floor | RESOLVED | n/a | 60% data completeness |

---

## 13. Engineering Footprint & Cost

Reused: DO droplet, n8n, DataForSEO, GSC service account, Claude API, Vercel pipeline, Cloudflare Turnstile, existing Airtable bases pattern.

Net new services: Perplexity API (~$20/mo), YouTube Data API v3 (free quota), spaCy + entity linker (self-hosted, free), PostHog (self-hosted, free), Loops.so (free tier). SerpAPI usage grows with the 6-hour Agent 12 loop; monitor quota at the ~340-query set.

**Total incremental run cost: under $50/month.** The binding constraints are human: Kam's documentation time (DG-2), weekly Loop call discipline, video recording time, and X approval throughput. Compute is not the constraint.

Repo discipline: all agents at /home/bizoo/engine/, dual-push to both GitHub remotes after every change, Claude Code as repo executor, this thread as strategist.

---

**End of PRD v2.0. This document is canonical. Future changes amend this file directly with a changelog entry; no further addendum documents.**

## Changelog
- v2.0 (May 2026): Consolidated v1.1 + v1.2 + v1.3. Resolved supersessions. Converted open questions to decision gates. Single source of truth established.
