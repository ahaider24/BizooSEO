# Agent 02: Technical SEO Auditor

PRD v2.0 section 6, Phase 1. Bi-weekly crawl of getbizoo.com. Next.js/Vercel SSR edge cases, dynamic routes (deals + drivers), and ISR can introduce crawlability regressions silently; this agent is the tripwire.

Checks, in order:

1. robots.txt presence; full-site Disallow is critical.
2. sitemap.xml (handles sitemap indexes): presence, XML validity, URL count, lastmod freshness (stale after 30 days).
3. Page health on sitemap URLs (capped by `--max-pages`): HTTP status, canonical presence/match, noindex-on-sitemap-URL (critical), title, meta description, JSON-LD parse validity.
4. Internal link health: links collected during the crawl, sampled (`--max-links`), 4xx/5xx critical, redirect chains logged.
5. Core Web Vitals via PageSpeed Insights (keyless): CrUX field data when it exists, Lighthouse lab values (LCP, CLS, TBT) as fallback while traffic is too low for field data.
6. GSC: submitted-sitemap errors/warnings, URL Inspection coverage state on a sample. Skipped gracefully when the service account is absent.

Output: one `TechnicalAudit` row per finding plus a run-summary row; Slack digest of severity counts and critical findings to #bizoo-seo.

## Run

```
python main.py --dry-run        # crawl + print findings, no writes
python main.py                  # full audit, writes TechnicalAudit, posts Slack
python main.py --max-pages 100 --max-links 200 --inspect-sample 10
```

Cadence: bi-weekly (n8n trigger wired later; standalone only for now).

## Environment (config/.env.example)

`AIRTABLE_API_KEY`, `AIRTABLE_BIZOO_SEO_BASE_ID`, `SLACK_WEBHOOK_BIZOO_SEO`, `BIZOO_DOMAIN`, optionally `GSC_SERVICE_ACCOUNT_JSON_PATH`. PageSpeed Insights runs keyless at this volume.

## Airtable schema expected

`TechnicalAudit` (agent-written, manual review):

| Field | Type |
|---|---|
| CheckedAt | date with time |
| Agent | single line text |
| Category | single select (Robots, Sitemap, Pages, Canonical, Schema, Links, CWV, Index, Audit) |
| Severity | single select (critical, warning, info) |
| URL | url or single line text |
| Detail | long text |
