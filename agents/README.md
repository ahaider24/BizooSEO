# Agents

One module per agent: `agent_NN_short_name/` with `main.py`, `README.md`, and any agent-local config. Full specs in PRD §6. Shared runtime (env loading, Airtable client, Slack, GSC auth) lives in [`common/`](common/README.md); `pip install -r requirements.txt` once at the repo root, then any agent runs standalone via `python main.py` (n8n orchestration comes later).

| # | Agent | Phase | Cadence |
|---|---|---|---|
| 01 | Keyword Intelligence | 1 | Weekly (Mon 6:00 AM) |
| 02 | Technical SEO Auditor | 1 | Bi-weekly |
| 03 | Performance Monitor (KPI stack) | 1 | Weekly |
| 04 | Content Brief Generator | 2 | On queue |
| 05 | Competitor Gap Scanner | 2 | Monthly |
| 06 | Backlink Intelligence | 2 | Monthly |
| 07 | Landing Page Optimizer | 2 | On publish + monthly sweep |
| 08 | Deal Data Ingestion | 3 | Daily |
| 09 | Programmatic Page Generator (deals + drivers) | 3 | On data, PR-gated |
| 10 | Schema Agent | 3 | On generation |
| 11 | Internal Linking Intelligence | 3 | On publish |
| 12 | AI Overview Citation Tracker | 4 | Every 6 hours |
| 13 | Video Citation Pipeline Orchestrator | 4 | Weekly (Loop transcript) |
| 14 | X Mention Engine | 4 | Daily gen, real-time monitor |
| 15 | Entity Density Optimizer | 4 | On brief/generation + monthly sweep |

Build order per PRD §11 roadmap. Phase 1 + Agent 12 first: baseline Citation Share must be measured before any new content ships.
