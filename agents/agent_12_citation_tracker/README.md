# Agent 12: AI Overview Citation Tracker

PRD v2.0 section 6 (Phase 4 spec). Built first per the section 11 roadmap: baseline Citation Share must be measured before any new content ships.

Per active `CitationTargets` row:

1. Google AI Overview capture via SerpAPI (cited URLs + positions, two-step fetch when the overview is behind a page token).
2. Perplexity (`sonar`) citation capture.
3. Google AI Mode capture via SerpAPI, priority subset only (PRD 5.2: Plan families 4 and 2 plus the top 50 original-pillar commercial queries).

Outputs:

- One `AIOverviewCitations` row per target per engine checked.
- Per-engine cited-state checkboxes maintained on `CitationTargets` (this is the state-change detector).
- Slack digest to #bizoo-seo: Citation Share snapshot per pillar, every citation state change, R2 early warning when runway.com is cited on an original-pillar query (PRD section 9), errors.

Anti-goal targets (`AntiGoal` checked) are logged for competitive awareness but excluded from Citation Share (PRD section 2, zero priority weight). Weekly and monthly Citation Share trends are computed by Agent 03 from `AIOverviewCitations` history.

## Run

```
python main.py                                         # full run, all active targets
python main.py --limit 5 --dry-run                     # engines called, no Airtable writes, no Slack
python main.py --query "how to calculate cash runway"  # ad-hoc one-query check, no Airtable
python main.py --engines perplexity --limit 10         # one engine only
python main.py --quiet                                 # Slack only on changes / warnings / errors
```

Cadence: every 6 hours. The n8n trigger is wired later; this build is standalone only. Quota note (PRD section 13): ~340 targets x 4 runs/day against SerpAPI; watch the plan limit.

## Environment (config/.env.example)

`SERPAPI_KEY`, `PERPLEXITY_API_KEY`, `AIRTABLE_API_KEY`, `AIRTABLE_BIZOO_SEO_BASE_ID`, `SLACK_WEBHOOK_BIZOO_SEO`, `BIZOO_DOMAIN`. An engine whose key is missing is skipped with a console note, so Perplexity-only testing works before the SerpAPI account exists.

## Airtable schema expected

`CitationTargets` (manually seeded to ~340 per PRD 5.2; agent maintains the state fields):

| Field | Type | Notes |
|---|---|---|
| Query | single line text | primary field |
| Pillar | single select | Ingest, Model, Monitor, Execute, Plan |
| Family | single select | optional, Plan-pillar families 1 to 4 |
| Priority | checkbox | include in the AI Mode subset |
| AntiGoal | checkbox | logged, zero priority weight |
| Status | single select | Active / Paused; blank counts as Active |
| Bizoo Cited AIO | checkbox | agent-maintained |
| Bizoo Cited Perplexity | checkbox | agent-maintained |
| Bizoo Cited AI Mode | checkbox | agent-maintained |
| Last Checked | date with time | agent-maintained |

`AIOverviewCitations` (agent-written, read by reporting and Agent 13):

| Field | Type |
|---|---|
| Query | single line text |
| Pillar | single select |
| Engine | single select |
| CheckedAt | date with time |
| AIPresent | checkbox |
| CitedDomains | long text |
| BizooCited | checkbox |
| BizooPosition | number |
| CompetitorsCited | long text |
| AntiGoal | checkbox |

Writes use Airtable typecast, so select options (pillars, engines) create themselves on first use.
