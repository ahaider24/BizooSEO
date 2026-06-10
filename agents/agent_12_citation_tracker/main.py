"""Agent 12: AI Overview Citation Tracker.

PRD v2.0 section 6, Phase 4 spec, deployed first (section 11): baseline
Citation Share must be measured before any new content ships. Cadence: every
6 hours once n8n-orchestrated; standalone for now via `python main.py`.

Per active CitationTargets row:
  1. Google AI Overview capture via SerpAPI, cited URL parse.
  2. Perplexity (sonar) citation capture.
  3. Google AI Mode capture via SerpAPI, priority subset only (PRD 5.2).

Writes one AIOverviewCitations row per target per engine checked, maintains
the per-engine cited-state checkboxes on CitationTargets, alerts Slack on
every citation state change, and posts a Citation Share snapshot per pillar.

Anti-goal targets (AntiGoal checked) are logged for competitive awareness but
carry zero priority weight: excluded from Citation Share (PRD section 2). A
runway.com citation on an original-pillar query raises the R2 early warning.
Weekly/monthly Citation Share trends are Agent 03's job, computed from
AIOverviewCitations history.
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agents.common.airtable import AirtableClient
from agents.common.config import load_competitors, load_env, require_env
from agents.common.slack import post_slack

TARGETS_TABLE = "CitationTargets"
CITATIONS_TABLE = "AIOverviewCitations"

ENGINE_AIO = "ai_overview"
ENGINE_PERPLEXITY = "perplexity"
ENGINE_AI_MODE = "ai_mode"
ALL_ENGINES = (ENGINE_AIO, ENGINE_PERPLEXITY, ENGINE_AI_MODE)

# Per-engine cited-state fields maintained on CitationTargets.
STATE_FIELDS = {
    ENGINE_AIO: "Bizoo Cited AIO",
    ENGINE_PERPLEXITY: "Bizoo Cited Perplexity",
    ENGINE_AI_MODE: "Bizoo Cited AI Mode",
}

ORIGINAL_PILLARS = {"Ingest", "Model", "Monitor", "Execute"}
RUNWAY_DOMAIN = "runway.com"

SERPAPI_URL = "https://serpapi.com/search.json"
PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"


def domain_of(url):
    netloc = urlparse(url or "").netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def domain_matches(domain, target):
    return domain == target or domain.endswith("." + target)


def parse_references(refs):
    citations = []
    for i, ref in enumerate(refs or []):
        url = ref.get("link")
        if not url:
            continue
        index = ref.get("index")
        position = index + 1 if isinstance(index, int) else i + 1
        citations.append({"url": url, "domain": domain_of(url), "position": position})
    return citations


def serpapi_get(params, api_key):
    resp = requests.get(SERPAPI_URL, params=dict(params, api_key=api_key, no_cache="true"), timeout=90)
    resp.raise_for_status()
    data = resp.json()
    if data.get("error"):
        raise RuntimeError("SerpAPI: " + str(data["error"]))
    return data


def check_ai_overview(query, api_key):
    data = serpapi_get({"engine": "google", "q": query, "hl": "en", "gl": "us"}, api_key)
    aio = data.get("ai_overview") or {}
    if aio.get("page_token"):
        # Overview served separately: second fetch with the page token.
        data = serpapi_get({"engine": "google_ai_overview", "page_token": aio["page_token"]}, api_key)
        aio = data.get("ai_overview") or {}
    present = bool(aio.get("text_blocks") or aio.get("references"))
    return {"present": present, "citations": parse_references(aio.get("references"))}


def check_ai_mode(query, api_key):
    data = serpapi_get({"engine": "google_ai_mode", "q": query, "hl": "en", "gl": "us"}, api_key)
    refs = data.get("references") or []
    present = bool(data.get("text_blocks") or refs)
    return {"present": present, "citations": parse_references(refs)}


def check_perplexity(query, api_key):
    resp = requests.post(
        PERPLEXITY_URL,
        json={"model": "sonar", "messages": [{"role": "user", "content": query}]},
        headers={"Authorization": "Bearer " + api_key},
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    urls = data.get("citations") or [r.get("url") for r in data.get("search_results") or [] if r.get("url")]
    citations = [{"url": u, "domain": domain_of(u), "position": i + 1} for i, u in enumerate(urls)]
    return {"present": bool(citations), "citations": citations}


CHECKERS = {
    ENGINE_AIO: check_ai_overview,
    ENGINE_AI_MODE: check_ai_mode,
    ENGINE_PERPLEXITY: check_perplexity,
}


def engine_key(engine):
    return os.environ.get("PERPLEXITY_API_KEY" if engine == ENGINE_PERPLEXITY else "SERPAPI_KEY")


def resolve_engines(requested):
    engines = [e.strip() for e in requested.split(",")] if requested else list(ALL_ENGINES)
    unknown = [e for e in engines if e not in ALL_ENGINES]
    if unknown:
        raise SystemExit("Unknown engine(s): {}. Valid: {}".format(", ".join(unknown), ", ".join(ALL_ENGINES)))
    available = []
    for engine in engines:
        if engine_key(engine):
            available.append(engine)
        else:
            key_name = "PERPLEXITY_API_KEY" if engine == ENGINE_PERPLEXITY else "SERPAPI_KEY"
            print("[agent12] skipping {}: {} not set".format(engine, key_name))
    if not available:
        raise SystemExit("No engine has credentials configured. See config/.env.example.")
    return available


def ad_hoc_check(query, engines, bizoo_domain, competitors):
    """One-query check against each engine, printed, no Airtable. For key/parse testing."""
    for engine in engines:
        try:
            result = CHECKERS[engine](query, engine_key(engine))
        except Exception as exc:
            print("\n{}: ERROR {}".format(engine, exc))
            continue
        print("\n{}: AI answer present: {}".format(engine, result["present"]))
        for c in result["citations"]:
            flags = []
            if domain_matches(c["domain"], bizoo_domain):
                flags.append("BIZOO")
            if any(domain_matches(c["domain"], comp) for comp in competitors):
                flags.append("competitor")
            suffix = "  [{}]".format(", ".join(flags)) if flags else ""
            print("  {:>2}. {}  {}{}".format(c["position"], c["domain"], c["url"], suffix))
        if not result["citations"]:
            print("  (no citations)")


def citation_share_lines(targets):
    """Share of active, non-anti-goal targets with a Bizoo citation on any engine."""
    by_pillar = {}
    for record in targets:
        f = record["fields"]
        if f.get("AntiGoal"):
            continue
        pillar = f.get("Pillar") or "Unassigned"
        cited = any(bool(f.get(field)) for field in STATE_FIELDS.values())
        total, n = by_pillar.get(pillar, (0, 0))
        by_pillar[pillar] = (total + 1, n + (1 if cited else 0))
    lines = []
    for pillar in sorted(by_pillar):
        total, n = by_pillar[pillar]
        lines.append("  {}: {}/{} ({:.1f}%)".format(pillar, n, total, 100.0 * n / total))
    return lines


def run(args):
    load_env()
    bizoo_domain = os.environ.get("BIZOO_DOMAIN", "getbizoo.com")
    competitors = load_competitors()
    engines = resolve_engines(args.engines)

    if args.query:
        ad_hoc_check(args.query, engines, bizoo_domain, competitors)
        return

    airtable_key, base_id = require_env("AIRTABLE_API_KEY", "AIRTABLE_BIZOO_SEO_BASE_ID")
    airtable = AirtableClient(airtable_key, base_id)
    targets = [
        r for r in airtable.list_records(TARGETS_TABLE)
        if (r["fields"].get("Status") or "Active") == "Active" and r["fields"].get("Query")
    ]
    if args.limit:
        targets = targets[: args.limit]
    now_iso = datetime.now(timezone.utc).isoformat()

    citation_rows, target_updates = [], []
    state_changes, runway_warnings, errors = [], [], []

    for record in targets:
        f = record["fields"]
        query = f["Query"]
        pillar = f.get("Pillar") or ""
        anti_goal = bool(f.get("AntiGoal"))
        updates = {"Last Checked": now_iso}

        for engine in engines:
            if engine == ENGINE_AI_MODE and not f.get("Priority"):
                continue  # AI Mode tracks the priority subset only (PRD 5.2)
            try:
                result = CHECKERS[engine](query, engine_key(engine))
            except Exception as exc:
                errors.append('{} "{}": {}'.format(engine, query, exc))
                continue

            cited_domains = [c["domain"] for c in result["citations"]]
            bizoo_position = next(
                (c["position"] for c in result["citations"] if domain_matches(c["domain"], bizoo_domain)),
                None,
            )
            bizoo_cited = bizoo_position is not None
            competitors_cited = sorted(
                {d for d in cited_domains if any(domain_matches(d, comp) for comp in competitors)}
            )

            citation_rows.append({
                "Query": query,
                "Pillar": pillar or None,
                "Engine": engine,
                "CheckedAt": now_iso,
                "AIPresent": result["present"],
                "CitedDomains": ", ".join(cited_domains),
                "BizooCited": bizoo_cited,
                "BizooPosition": bizoo_position,
                "CompetitorsCited": ", ".join(competitors_cited),
                "AntiGoal": anti_goal,
            })

            if bizoo_cited != bool(f.get(STATE_FIELDS[engine])):
                verb = "GAINED" if bizoo_cited else "LOST"
                state_changes.append('{} {} citation: "{}" ({})'.format(verb, engine, query, pillar or "no pillar"))
            updates[STATE_FIELDS[engine]] = bizoo_cited
            f[STATE_FIELDS[engine]] = bizoo_cited  # keep in-memory state current for the share snapshot

            if pillar in ORIGINAL_PILLARS and any(domain_matches(d, RUNWAY_DOMAIN) for d in cited_domains):
                runway_warnings.append('runway.com cited on original-pillar query "{}" ({})'.format(query, engine))

        target_updates.append((record["id"], updates))

    if args.dry_run:
        print("[dry-run] would write {} AIOverviewCitations rows, update {} targets".format(
            len(citation_rows), len(target_updates)))
    else:
        airtable.create_records(CITATIONS_TABLE, citation_rows)
        airtable.update_records(TARGETS_TABLE, target_updates)

    lines = ["*Agent 12 run* {}: {} targets checked, engines: {}".format(now_iso, len(targets), ", ".join(engines))]
    lines.append("Citation Share snapshot (any engine, anti-goals excluded):")
    lines.extend(citation_share_lines(targets) or ["  (no eligible targets)"])
    if state_changes:
        lines.append("Citation state changes ({}):".format(len(state_changes)))
        lines.extend("  " + s for s in state_changes)
    if runway_warnings:
        lines.append("R2 EARLY WARNING (PRD section 9): Runway on diligence-prep queries:")
        lines.extend("  " + w for w in runway_warnings)
    if errors:
        lines.append("Errors ({}, first 10):".format(len(errors)))
        lines.extend("  " + e for e in errors[:10])
    digest = "\n".join(lines)
    print(digest)

    if args.dry_run:
        return
    if args.quiet and not (state_changes or runway_warnings or errors):
        print("[quiet] no state changes, Slack post skipped")
        return
    post_slack(os.environ.get("SLACK_WEBHOOK_BIZOO_SEO"), digest)


def main():
    parser = argparse.ArgumentParser(description="Agent 12: AI Overview Citation Tracker")
    parser.add_argument("--limit", type=int, help="check only the first N targets (testing)")
    parser.add_argument("--engines", help="comma list from: {} (default all)".format(",".join(ALL_ENGINES)))
    parser.add_argument("--query", help="ad-hoc single-query check, no Airtable read or write")
    parser.add_argument("--dry-run", action="store_true",
                        help="call the engines but skip Airtable writes and Slack")
    parser.add_argument("--quiet", action="store_true",
                        help="post to Slack only on state changes, warnings, or errors")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
