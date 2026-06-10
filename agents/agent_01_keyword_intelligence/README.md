# Agent 01: Keyword Intelligence

PRD v2.0 section 6, Phase 1. Weekly competitor keyword intersection plus GSC movers, feeding the Agent 04 brief queue.

What it does:

1. Pulls Bizoo's own DataForSEO ranked keywords (top 100: presence anywhere means "not absent").
2. Pulls each section 4 competitor's ranked keywords at positions 1 to 30 (`config/competitors.yml`, disambiguation-only domains excluded).
3. Opportunities are competitor keywords where Bizoo is absent, scored `volume * (1 / competition) * relevance_weight`. Weights live in `relevance.yml` (agent-local config); section 2 anti-goals (FP&A head terms, Runway-brand queries other than displacement intents) score zero.
4. Writes the top 20 new opportunities to `Keywords` with status `Queued`, deduped against existing rows.
5. GSC Search Analytics movers: last 28 full days vs the prior 28.
6. Slack digest to #bizoo-seo: opportunities, movers, competitor alerts (competitor in the top 3 above the volume floor).

## Run

```
python main.py                 # full weekly run
python main.py --dry-run       # pull data, no Airtable writes, no Slack
python main.py --top 10 --alert-volume 500
```

Cadence: weekly cron, Monday 6:00 AM (n8n trigger wired later; standalone only for now). DataForSEO Labs live calls cost per request: one call per domain, 9 calls per run.

## Environment (config/.env.example)

`DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD`, `AIRTABLE_API_KEY`, `AIRTABLE_BIZOO_SEO_BASE_ID`, `SLACK_WEBHOOK_BIZOO_SEO`, `BIZOO_DOMAIN`, and optionally `GSC_SERVICE_ACCOUNT_JSON_PATH` (movers section is skipped gracefully without it).

## Airtable schema expected

`Keywords` (agent-written, read by Agent 04):

| Field | Type |
|---|---|
| Keyword | single line text (primary) |
| Status | single select (Queued, ...) |
| Source | single line text |
| Score | number |
| Volume | number |
| Competition | number (0 to 1) |
| CompetitorDomain | single line text |
| CompetitorPosition | number |
| AddedAt | date |
