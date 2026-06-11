# Agent 03: Performance Monitor (rebuilt in v2.0)

PRD v2.0 section 6, Phase 1. Weekly KPI report to #bizoo-seo, ordered by the section 2 KPI stack. Rank tracking is demoted to a secondary view at the bottom.

Sections:

1. **Citation Share per pillar** (primary KPI). Computed from `AIOverviewCitations` (Agent 12 history): distinct non-anti-goal queries with a Bizoo citation on any engine over distinct queries checked, this window vs the prior one, with the section 2 ramp targets printed alongside. Run Agent 12 first; this section says so if the table is empty.
2. **Brand Mention Velocity.** `SocialMentions` counts, last 30 days vs prior 30. Reports pending until Agent 14 lands (June, PRD section 11).
3. **Tool-to-Signup.** New `Leads` in the CRM base over the window. PostHog `tool_session` cohort tracking arrives with WF-02; noted as pending in the report.
4. **Branded query CTR.** GSC queries containing "bizoo", trailing 28 days.

Secondary: GSC top queries with average position (tracked, not optimized).

Every section degrades to an explicit "pending" or "skipped" line instead of failing, so the report is useful from day one when upstream agents and workflows are not live yet.

## Run

```
python main.py --dry-run    # print the report, skip Slack
python main.py              # print + post to #bizoo-seo
python main.py --days 14
```

Cadence: weekly (n8n trigger wired later; standalone only for now).

## Environment (config/.env.example)

`AIRTABLE_API_KEY`, `AIRTABLE_BIZOO_SEO_BASE_ID`, `SLACK_WEBHOOK_BIZOO_SEO`, optionally `AIRTABLE_BIZOO_CRM_BASE_ID` (Tool-to-Signup) and `GSC_SERVICE_ACCOUNT_JSON_PATH` (CTR + rank view).

## Airtable tables read

- `AIOverviewCitations` (Agent 12 schema, see `agents/agent_12_citation_tracker/README.md`). `CheckedAt` should be a date-with-time field so the server-side window filter works; the agent falls back to record createdTime otherwise.
- `SocialMentions` (Agent 14, optional until June).
- CRM base `Leads` (WF-01, optional until live).
