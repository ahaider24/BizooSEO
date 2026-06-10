"""Agent 01: Keyword Intelligence.

PRD v2.0 section 6, Phase 1. Cadence: weekly, Monday 6:00 AM (n8n trigger
later; standalone via `python main.py`).

1. GSC Search Analytics for getbizoo.com: top queries and movers vs the
   prior 28-day window.
2. DataForSEO Labs ranked keywords for each section 4 competitor (positions
   1 to 30), intersected against Bizoo's own ranked set: keywords where
   Bizoo is absent are opportunities.
3. Opportunity score: volume * (1 / competition) * relevance weight.
   Weights live in relevance.yml; section 2 anti-goals score zero.
4. Top 20 written to Keywords with status Queued (feeds Agent 04).
5. Slack digest to #bizoo-seo: movers, opportunities, competitor alerts.
"""

import argparse
import os
import sys
from datetime import date, timedelta
from pathlib import Path

import requests
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agents.common.airtable import AirtableClient
from agents.common.config import load_competitors, load_env, require_env
from agents.common.gsc import gsc_session, search_analytics
from agents.common.slack import post_slack

KEYWORDS_TABLE = "Keywords"
DATAFORSEO_URL = "https://api.dataforseo.com/v3/dataforseo_labs/google/ranked_keywords/live"
AGENT_DIR = Path(__file__).resolve().parent


def load_relevance():
    return yaml.safe_load((AGENT_DIR / "relevance.yml").read_text())


def relevance_weight(keyword, rules):
    kw = keyword.lower()
    for rule in rules.get("exclude") or []:
        if rule["pattern"] in kw and not any(u in kw for u in rule.get("unless") or []):
            return 0.0
    for bucket in ("pillar", "adjacent"):
        cfg = rules.get(bucket) or {}
        if any(term in kw for term in cfg.get("terms") or []):
            return float(cfg.get("weight", 1.0))
    return float(rules.get("default_weight", 0.3))


def ranked_keywords(target, login, password, rank_max, limit=1000):
    """DataForSEO Labs ranked keywords for a domain, capped at rank_max."""
    payload = [{
        "target": target,
        "language_code": "en",
        "location_code": 2840,
        "limit": limit,
        "order_by": ["keyword_data.keyword_info.search_volume,desc"],
        "filters": [["ranked_serp_element.serp_item.rank_absolute", "<=", rank_max]],
    }]
    resp = requests.post(DATAFORSEO_URL, auth=(login, password), json=payload, timeout=180)
    resp.raise_for_status()
    items = []
    for task in resp.json().get("tasks") or []:
        if task.get("status_code") and task["status_code"] >= 40000:
            raise RuntimeError("DataForSEO task error {}: {}".format(
                task["status_code"], task.get("status_message")))
        for result in task.get("result") or []:
            for item in result.get("items") or []:
                kd = item.get("keyword_data") or {}
                info = kd.get("keyword_info") or {}
                serp = (item.get("ranked_serp_element") or {}).get("serp_item") or {}
                if kd.get("keyword"):
                    items.append({
                        "keyword": kd["keyword"].lower(),
                        "volume": info.get("search_volume") or 0,
                        "competition": info.get("competition"),
                        "position": serp.get("rank_absolute"),
                    })
    return items


def score(item, rules):
    competition = item["competition"] if item["competition"] is not None else 0.5
    return item["volume"] * (1.0 / max(competition, 0.05)) * relevance_weight(item["keyword"], rules)


def gsc_windows(session):
    """Top queries for the last 28 full days and the 28 days before that."""
    end = date.today() - timedelta(days=3)  # GSC data lags about 2 days
    start = end - timedelta(days=27)
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=27)

    def window(s, e):
        rows = search_analytics(session, {
            "startDate": s.isoformat(),
            "endDate": e.isoformat(),
            "dimensions": ["query"],
            "rowLimit": 250,
        })
        return {r["keys"][0]: r for r in rows}

    return window(start, end), window(prev_start, prev_end)


def movers(current, previous, top_n=5):
    deltas = []
    for q in set(current) | set(previous):
        delta = current.get(q, {}).get("clicks", 0) - previous.get(q, {}).get("clicks", 0)
        if delta:
            deltas.append((delta, q))
    up = sorted((d for d in deltas if d[0] > 0), reverse=True)[:top_n]
    down = sorted(d for d in deltas if d[0] < 0)[:top_n]
    return up, down


def gsc_section(top_n=5):
    session = gsc_session()
    if not session:
        return ["  GSC service account not configured, movers skipped"]
    try:
        current, previous = gsc_windows(session)
    except Exception as exc:
        return ["  GSC error: {}".format(exc)]
    if not current and not previous:
        return ["  no GSC query data yet (28-day window)"]
    up, down = movers(current, previous, top_n)
    lines = []
    for delta, q in up:
        lines.append('  up   +{} clicks: "{}"'.format(delta, q))
    for delta, q in down:
        lines.append('  down {} clicks: "{}"'.format(delta, q))
    return lines or ["  no significant movers WoW"]


def run(args):
    load_env()
    rules = load_relevance()
    bizoo_domain = os.environ.get("BIZOO_DOMAIN", "getbizoo.com")
    login, password = require_env("DATAFORSEO_LOGIN", "DATAFORSEO_PASSWORD")
    airtable_key, base_id = require_env("AIRTABLE_API_KEY", "AIRTABLE_BIZOO_SEO_BASE_ID")
    competitors = load_competitors()
    today_iso = date.today().isoformat()

    gsc_lines = gsc_section()

    # Bizoo's own footprint: anywhere in the top 100 counts as "not absent".
    bizoo_keywords = {i["keyword"] for i in ranked_keywords(bizoo_domain, login, password, rank_max=100)}

    opportunities = {}  # keyword -> best-scoring item across competitors
    competitor_alerts = []
    for comp in competitors:
        try:
            items = ranked_keywords(comp, login, password, rank_max=args.rank_max)
        except Exception as exc:
            print("[agent01] {}: DataForSEO error: {}".format(comp, exc))
            continue
        for item in items:
            kw = item["keyword"]
            if kw in bizoo_keywords:
                continue
            item = dict(item, competitor=comp, score=score(item, rules))
            if item["position"] and item["position"] <= 3 and item["volume"] >= args.alert_volume:
                competitor_alerts.append('{} ranks #{} for "{}" (vol {})'.format(
                    comp, item["position"], kw, item["volume"]))
            if item["score"] <= 0:
                continue
            best = opportunities.get(kw)
            if best is None or item["score"] > best["score"]:
                opportunities[kw] = item

    ranked = sorted(opportunities.values(), key=lambda i: i["score"], reverse=True)

    airtable = AirtableClient(airtable_key, base_id)
    existing = {
        (r["fields"].get("Keyword") or "").lower()
        for r in airtable.list_records(KEYWORDS_TABLE, fields=["Keyword"])
    }
    to_write = [i for i in ranked if i["keyword"] not in existing][: args.top]
    rows = [{
        "Keyword": i["keyword"],
        "Status": "Queued",
        "Source": "Agent 01",
        "Score": round(i["score"], 1),
        "Volume": i["volume"],
        "Competition": i["competition"],
        "CompetitorDomain": i["competitor"],
        "CompetitorPosition": i["position"],
        "AddedAt": today_iso,
    } for i in to_write]

    if args.dry_run:
        print("[dry-run] would write {} Keywords rows".format(len(rows)))
    else:
        airtable.create_records(KEYWORDS_TABLE, rows)

    lines = ["*Agent 01 weekly digest* {}".format(today_iso)]
    lines.append("Opportunities: {} scored, {} new queued (top {})".format(
        len(ranked), len(rows), args.top))
    for i, item in enumerate(to_write[:10], 1):
        lines.append('  {}. "{}" score {:.0f} (vol {}, {} at #{})'.format(
            i, item["keyword"], item["score"], item["volume"], item["competitor"], item["position"]))
    lines.append("GSC movers (28d WoW):")
    lines.extend(gsc_lines)
    if competitor_alerts:
        lines.append("Competitor alerts (top 3 positions, vol >= {}):".format(args.alert_volume))
        lines.extend("  " + a for a in competitor_alerts[:10])
    digest = "\n".join(lines)
    print(digest)

    if not args.dry_run:
        post_slack(os.environ.get("SLACK_WEBHOOK_BIZOO_SEO"), digest)


def main():
    parser = argparse.ArgumentParser(description="Agent 01: Keyword Intelligence")
    parser.add_argument("--top", type=int, default=20, help="opportunities written to Keywords (default 20)")
    parser.add_argument("--rank-max", type=int, default=30,
                        help="competitor position ceiling for intersection (default 30, PRD section 6)")
    parser.add_argument("--alert-volume", type=int, default=200,
                        help="volume floor for competitor top-3 alerts (default 200)")
    parser.add_argument("--dry-run", action="store_true",
                        help="pull data but skip Airtable writes and Slack")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
