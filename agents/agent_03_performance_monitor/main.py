"""Agent 03: Performance Monitor (rebuilt in v2.0).

PRD v2.0 section 6, Phase 1. Cadence: weekly (n8n trigger later; standalone
via `python main.py`). Reports the section 2 KPI stack, in order:

1. Citation Share per pillar (Agent 12 data in AIOverviewCitations), this
   week vs last week, against the section 2 ramp targets.
2. Brand Mention Velocity (Agent 14 data in SocialMentions; reported as
   pending until Agent 14 is live in June).
3. Tool-to-Signup (CRM base Leads; PostHog tool_session cohorts land with
   WF-02).
4. Branded query CTR (GSC, queries containing "bizoo", 28 days).

Rank tracking is demoted to a secondary view (GSC top queries). Report
posts to #bizoo-seo.
"""

import argparse
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agents.common.airtable import AirtableClient
from agents.common.config import load_env, require_env
from agents.common.gsc import gsc_session, search_analytics
from agents.common.slack import post_slack

CITATIONS_TABLE = "AIOverviewCitations"
MENTIONS_TABLE = "SocialMentions"

TARGET_NOTE = ("  Targets (PRD section 2): original pillars 8 to 12% by week 12, "
               "20 to 25% by month 6; Plan pillar 5% by week 12, 15% by month 6.")


def parse_dt(value):
    try:
        return datetime.fromisoformat((value or "").replace("Z", "+00:00"))
    except ValueError:
        return None


def fetch_recent_citations(airtable, days):
    """AIOverviewCitations rows from the last `days` days.

    Prefers a server-side CheckedAt filter; falls back to a full fetch
    filtered on record createdTime if the formula fails (field type drift).
    """
    formula = "IS_AFTER({{CheckedAt}}, DATETIME_ADD(NOW(), -{}, 'days'))".format(days)
    try:
        return airtable.list_records(CITATIONS_TABLE, formula=formula)
    except RuntimeError as exc:
        print("[agent03] CheckedAt filter failed ({}), falling back to full fetch".format(exc))
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return [r for r in airtable.list_records(CITATIONS_TABLE)
                if (parse_dt(r.get("createdTime")) or cutoff) >= cutoff]


def citation_share(rows, since, until):
    """Per pillar: (distinct non-anti-goal queries cited on any engine, distinct queries checked)."""
    per_pillar = {}
    for r in rows:
        f = r["fields"]
        checked = parse_dt(f.get("CheckedAt")) or parse_dt(r.get("createdTime"))
        if not checked or not (since <= checked < until) or f.get("AntiGoal"):
            continue
        queries = per_pillar.setdefault(f.get("Pillar") or "Unassigned", {})
        q = f.get("Query") or ""
        queries[q] = queries.get(q, False) or bool(f.get("BizooCited"))
    return {
        pillar: (sum(1 for cited in queries.values() if cited), len(queries))
        for pillar, queries in per_pillar.items()
    }


def share_section(airtable, days):
    rows = fetch_recent_citations(airtable, days * 2 + 1)
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=days)
    this_week = citation_share(rows, week_ago, now)
    last_week = citation_share(rows, now - timedelta(days=days * 2), week_ago)
    if not this_week and not last_week:
        return ["  no Agent 12 data yet: run agent_12_citation_tracker to set the baseline", TARGET_NOTE]
    lines = []
    for pillar in sorted(set(this_week) | set(last_week)):
        cited, total = this_week.get(pillar, (0, 0))
        prev_cited, prev_total = last_week.get(pillar, (0, 0))
        pct = 100.0 * cited / total if total else 0.0
        prev_pct = 100.0 * prev_cited / prev_total if prev_total else 0.0
        lines.append("  {}: {:.1f}% ({}/{}), {:+.1f} pts WoW".format(
            pillar, pct, cited, total, pct - prev_pct))
    lines.append(TARGET_NOTE)
    return lines


def mention_section(airtable):
    try:
        records = airtable.list_records(MENTIONS_TABLE)
    except RuntimeError:
        return ["  SocialMentions table not available yet (Agent 14 lands in June, PRD section 11)"]
    now = datetime.now(timezone.utc)

    def in_window(r, start_days, end_days):
        created = parse_dt(r.get("createdTime"))
        return created and now - timedelta(days=start_days) <= created < now - timedelta(days=end_days)

    last30 = sum(1 for r in records if in_window(r, 30, 0))
    prior30 = sum(1 for r in records if in_window(r, 60, 30))
    if not records:
        return ["  no mentions logged yet (Agent 14 lands in June)"]
    trend = "up" if last30 > prior30 else ("flat" if last30 == prior30 else "down")
    return ["  {} mentions last 30 days vs {} the prior 30 (trend {})".format(last30, prior30, trend)]


def tool_to_signup_section(days):
    crm_base = os.environ.get("AIRTABLE_BIZOO_CRM_BASE_ID")
    if not crm_base:
        return ["  pending: CRM base not configured (WF-01/WF-02, PRD section 10)"]
    crm = AirtableClient(os.environ["AIRTABLE_API_KEY"], crm_base)
    lines = []
    try:
        leads = crm.list_records("Leads")
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=days)
        new = sum(1 for r in leads if (parse_dt(r.get("createdTime")) or cutoff) > cutoff)
        lines.append("  {} new leads in the last {} days ({} total)".format(new, days, len(leads)))
    except RuntimeError:
        lines.append("  Leads table not readable yet (WF-01 pending)")
    lines.append("  tool_session cohorts land with WF-02 + PostHog wiring (PRD section 10)")
    return lines


def branded_ctr_section(session):
    if not session:
        return ["  GSC service account not configured, skipped"]
    end = date.today() - timedelta(days=3)
    start = end - timedelta(days=27)
    try:
        rows = search_analytics(session, {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "dimensions": ["query"],
            "dimensionFilterGroups": [{"filters": [
                {"dimension": "query", "operator": "contains", "expression": "bizoo"}
            ]}],
            "rowLimit": 250,
        })
    except Exception as exc:
        return ["  GSC error: {}".format(exc)]
    clicks = sum(r["clicks"] for r in rows)
    impressions = sum(r["impressions"] for r in rows)
    if not impressions:
        return ["  no branded impressions in the last 28 days yet"]
    return ["  {} clicks / {} impressions = {:.1f}% CTR across {} branded queries (28 days)".format(
        clicks, impressions, 100.0 * clicks / impressions, len(rows))]


def rank_section(session, top_n=10):
    if not session:
        return ["  skipped (no GSC)"]
    end = date.today() - timedelta(days=3)
    start = end - timedelta(days=27)
    try:
        rows = search_analytics(session, {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "dimensions": ["query"],
            "rowLimit": top_n,
        })
    except Exception as exc:
        return ["  GSC error: {}".format(exc)]
    lines = ['  "{}": position {:.1f}, {} clicks, {} impressions'.format(
        r["keys"][0], r["position"], r["clicks"], r["impressions"]) for r in rows]
    return lines or ["  no query data in GSC yet"]


def run(args):
    load_env()
    airtable_key, base_id = require_env("AIRTABLE_API_KEY", "AIRTABLE_BIZOO_SEO_BASE_ID")
    airtable = AirtableClient(airtable_key, base_id)
    session = gsc_session()

    lines = ["*Bizoo SEO weekly KPI report* (generated {})".format(date.today().isoformat())]
    lines.append("1. Citation Share per pillar (primary KPI, any engine, {}-day window):".format(args.days))
    lines.extend(share_section(airtable, args.days))
    lines.append("2. Brand Mention Velocity:")
    lines.extend(mention_section(airtable))
    lines.append("3. Tool-to-Signup:")
    lines.extend(tool_to_signup_section(args.days))
    lines.append("4. Branded query CTR:")
    lines.extend(branded_ctr_section(session))
    lines.append("Secondary view (rank, tracked not optimized):")
    lines.extend(rank_section(session))
    report = "\n".join(lines)
    print(report)

    if not args.dry_run:
        post_slack(os.environ.get("SLACK_WEBHOOK_BIZOO_SEO"), report)


def main():
    parser = argparse.ArgumentParser(description="Agent 03: Performance Monitor (KPI stack)")
    parser.add_argument("--days", type=int, default=7, help="reporting window in days (default 7)")
    parser.add_argument("--dry-run", action="store_true", help="print the report, skip Slack")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
