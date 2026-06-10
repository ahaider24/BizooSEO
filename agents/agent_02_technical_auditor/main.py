"""Agent 02: Technical SEO Auditor.

PRD v2.0 section 6, Phase 1. Cadence: bi-weekly (n8n trigger later;
standalone via `python main.py`).

Crawls getbizoo.com and writes findings to TechnicalAudit:
  - robots.txt and sitemap presence/freshness
  - page health on sitemap URLs: status, canonical, noindex, title, meta
    description, JSON-LD validity
  - internal link health (sampled)
  - Core Web Vitals via the PageSpeed Insights API (keyless, low volume)
  - GSC sitemap status and index coverage on a sampled subset

Next.js/Vercel SSR edge cases, dynamic routes, and ISR can break
crawlability silently (PRD section 6); this agent is the tripwire.
"""

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agents.common.airtable import AirtableClient
from agents.common.config import load_env, require_env
from agents.common.gsc import gsc_property, gsc_session
from agents.common.slack import post_slack

AUDIT_TABLE = "TechnicalAudit"
PSI_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
HEADERS = {"User-Agent": "BizooSEO-Agent02/1.0 (+https://getbizoo.com)"}

CRUX_METRICS = {
    "LARGEST_CONTENTFUL_PAINT_MS": "LCP",
    "INTERACTION_TO_NEXT_PAINT": "INP",
    "CUMULATIVE_LAYOUT_SHIFT_SCORE": "CLS",
}
# Lighthouse lab fallback when the site has no CrUX field data yet:
# audit id -> (label, warning threshold, critical threshold)
LAB_THRESHOLDS = {
    "largest-contentful-paint": ("LCP", 2500, 4000),
    "cumulative-layout-shift": ("CLS", 0.1, 0.25),
    "total-blocking-time": ("TBT", 200, 600),
}


def finding(category, severity, url, detail):
    return {"Category": category, "Severity": severity, "URL": url, "Detail": detail}


def host_of(url):
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def check_robots(base, http):
    url = urljoin(base, "/robots.txt")
    try:
        resp = http.get(url, timeout=30)
    except requests.RequestException as exc:
        return [finding("Robots", "critical", url, "fetch failed: {}".format(exc))]
    if resp.status_code != 200:
        return [finding("Robots", "warning", url, "robots.txt returned {}".format(resp.status_code))]
    if any(line.strip().lower() == "disallow: /" for line in resp.text.splitlines()):
        return [finding("Robots", "critical", url, "robots.txt contains a full-site Disallow")]
    return []


def parse_sitemap(xml_text):
    root = ET.fromstring(xml_text)
    kind = root.tag.rsplit("}", 1)[-1]  # urlset or sitemapindex
    entries = []
    for child in root:
        loc, lastmod = None, None
        for el in child:
            tag = el.tag.rsplit("}", 1)[-1]
            if tag == "loc":
                loc = (el.text or "").strip()
            elif tag == "lastmod":
                lastmod = (el.text or "").strip()
        if loc:
            entries.append((loc, lastmod))
    return kind, entries


def fetch_sitemap(base, http):
    findings, entries = [], []
    url = urljoin(base, "/sitemap.xml")
    try:
        resp = http.get(url, timeout=30)
    except requests.RequestException as exc:
        return entries, [finding("Sitemap", "critical", url, "fetch failed: {}".format(exc))]
    if resp.status_code != 200:
        return entries, [finding("Sitemap", "critical", url, "sitemap.xml returned {}".format(resp.status_code))]
    try:
        kind, items = parse_sitemap(resp.text)
    except ET.ParseError as exc:
        return entries, [finding("Sitemap", "critical", url, "sitemap XML invalid: {}".format(exc))]

    if kind == "sitemapindex":
        for loc, _ in items:
            try:
                child = http.get(loc, timeout=30)
                child.raise_for_status()
                _, child_items = parse_sitemap(child.text)
                entries.extend(child_items)
            except (requests.RequestException, ET.ParseError) as exc:
                findings.append(finding("Sitemap", "critical", loc, "child sitemap failed: {}".format(exc)))
    else:
        entries = items

    if not entries:
        findings.append(finding("Sitemap", "critical", url, "sitemap contains no URLs"))
        return entries, findings
    lastmods = [lm for _, lm in entries if lm]
    if lastmods:
        newest = max(lastmods)[:10]
        cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).date().isoformat()
        if newest < cutoff:
            findings.append(finding("Sitemap", "warning", url,
                                    "newest lastmod is {}, sitemap may be stale".format(newest)))
    else:
        findings.append(finding("Sitemap", "info", url, "no lastmod values in sitemap"))
    return entries, findings


def audit_page(url, http, domain):
    findings, internal = [], set()
    try:
        resp = http.get(url, timeout=30)
    except requests.RequestException as exc:
        return [finding("Pages", "critical", url, "fetch failed: {}".format(exc))], internal
    if resp.status_code != 200:
        return [finding("Pages", "critical", url, "sitemap URL returned {}".format(resp.status_code))], internal
    soup = BeautifulSoup(resp.text, "html.parser")

    canonical = soup.find("link", rel="canonical")
    if not canonical or not canonical.get("href"):
        findings.append(finding("Canonical", "warning", url, "no canonical tag"))
    elif canonical["href"].rstrip("/") != url.rstrip("/"):
        findings.append(finding("Canonical", "warning", url, "canonical points to {}".format(canonical["href"])))

    robots_meta = soup.find("meta", attrs={"name": "robots"})
    if robots_meta and "noindex" in (robots_meta.get("content") or "").lower():
        findings.append(finding("Pages", "critical", url, "noindex on a sitemap URL"))

    if not (soup.title and soup.title.get_text(strip=True)):
        findings.append(finding("Pages", "warning", url, "missing or empty <title>"))
    description = soup.find("meta", attrs={"name": "description"})
    if not (description and (description.get("content") or "").strip()):
        findings.append(finding("Pages", "warning", url, "missing meta description"))

    ld_blocks = soup.find_all("script", type="application/ld+json")
    if not ld_blocks:
        findings.append(finding("Schema", "warning", url,
                                "no JSON-LD structured data (v2.0 mandates schema on every page)"))
    for block in ld_blocks:
        try:
            json.loads(block.string or "")
        except (json.JSONDecodeError, TypeError):
            findings.append(finding("Schema", "critical", url, "invalid JSON-LD block"))

    for a in soup.find_all("a", href=True):
        href = urljoin(url, a["href"].split("#")[0])
        parsed = urlparse(href)
        if parsed.scheme in ("http", "https") and host_of(href) == domain:
            internal.add(href)
    return findings, internal


def check_links(links, http):
    findings = []
    for link in links:
        try:
            resp = http.head(link, timeout=20, allow_redirects=True)
            if resp.status_code in (403, 405, 501):
                resp = http.get(link, timeout=20, allow_redirects=True)
        except requests.RequestException as exc:
            findings.append(finding("Links", "critical", link, "fetch failed: {}".format(exc)))
            continue
        if resp.status_code >= 400:
            findings.append(finding("Links", "critical", link, "internal link returns {}".format(resp.status_code)))
        elif len(resp.history) > 1:
            findings.append(finding("Links", "info", link, "{} redirect hops".format(len(resp.history))))
    return findings


def fmt(value):
    return "{:.2f}".format(value) if value < 10 else "{:.0f}".format(value)


def check_cwv(url):
    """Core Web Vitals via PageSpeed Insights, keyless (fine at this volume).

    CrUX field data preferred; Lighthouse lab values as fallback while the
    site has too little traffic for field data.
    """
    try:
        resp = requests.get(PSI_URL, params={"url": url, "strategy": "mobile", "category": "performance"},
                            timeout=180)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        return [finding("CWV", "info", url, "PageSpeed Insights unavailable: {}".format(exc))]

    findings = []
    crux = ((data.get("loadingExperience") or {}).get("metrics")) or {}
    if crux:
        for key, label in CRUX_METRICS.items():
            metric = crux.get(key)
            if not metric:
                continue
            category = metric.get("category")
            if category == "SLOW":
                findings.append(finding("CWV", "critical", url,
                                        "{} field data is POOR (p75 {})".format(label, metric.get("percentile"))))
            elif category == "AVERAGE":
                findings.append(finding("CWV", "warning", url,
                                        "{} field data NEEDS IMPROVEMENT (p75 {})".format(label, metric.get("percentile"))))
    else:
        audits = ((data.get("lighthouseResult") or {}).get("audits")) or {}
        for audit_id, (label, warn, crit) in LAB_THRESHOLDS.items():
            value = (audits.get(audit_id) or {}).get("numericValue")
            if value is None:
                continue
            if value >= crit:
                findings.append(finding("CWV", "critical", url,
                                        "{} lab value {} (no field data yet)".format(label, fmt(value))))
            elif value >= warn:
                findings.append(finding("CWV", "warning", url,
                                        "{} lab value {} (no field data yet)".format(label, fmt(value))))
    return findings


def gsc_checks(sample_urls, inspect_n):
    session = gsc_session()
    if not session:
        return [finding("Index", "info", "", "GSC service account not configured, index checks skipped")]
    findings = []
    site = quote(gsc_property(), safe="")
    try:
        resp = session.get(
            "https://searchconsole.googleapis.com/webmasters/v3/sites/{}/sitemaps".format(site), timeout=60)
        resp.raise_for_status()
        sitemaps = resp.json().get("sitemap", [])
        if not sitemaps:
            findings.append(finding("Index", "warning", "", "no sitemap submitted to GSC"))
        for sm in sitemaps:
            errors, warnings = int(sm.get("errors", 0)), int(sm.get("warnings", 0))
            if errors:
                findings.append(finding("Index", "critical", sm.get("path", ""),
                                        "GSC reports {} sitemap errors".format(errors)))
            if warnings:
                findings.append(finding("Index", "warning", sm.get("path", ""),
                                        "GSC reports {} sitemap warnings".format(warnings)))
    except Exception as exc:
        findings.append(finding("Index", "info", "", "GSC sitemaps check failed: {}".format(exc)))

    for url in sample_urls[:inspect_n]:
        try:
            resp = session.post(
                "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",
                json={"inspectionUrl": url, "siteUrl": gsc_property()},
                timeout=60,
            )
            resp.raise_for_status()
            status = ((resp.json().get("inspectionResult") or {}).get("indexStatusResult")) or {}
            coverage = status.get("coverageState", "unknown")
            if coverage != "Submitted and indexed":
                findings.append(finding("Index", "warning", url, "coverage state: {}".format(coverage)))
        except Exception as exc:
            findings.append(finding("Index", "info", url, "URL inspection failed: {}".format(exc)))
    return findings


def run(args):
    load_env()
    domain = os.environ.get("BIZOO_DOMAIN", "getbizoo.com")
    base = "https://{}/".format(domain)
    http = requests.Session()
    http.headers.update(HEADERS)

    findings = []
    findings += check_robots(base, http)
    entries, sitemap_findings = fetch_sitemap(base, http)
    findings += sitemap_findings

    urls = [base] + [u for u, _ in entries if u.rstrip("/") != base.rstrip("/")]
    pages = urls[: args.max_pages]
    all_internal = set()
    for url in pages:
        page_findings, internal = audit_page(url, http, domain)
        findings += page_findings
        all_internal |= internal

    crawled = {u.rstrip("/") for u in pages}
    to_check = sorted(l for l in all_internal if l.rstrip("/") not in crawled)[: args.max_links]
    findings += check_links(to_check, http)

    for url in pages[: args.cwv_pages]:
        findings += check_cwv(url)

    findings += gsc_checks(pages, args.inspect_sample)

    counts = {"critical": 0, "warning": 0, "info": 0}
    for f in findings:
        counts[f["Severity"]] += 1
    now_iso = datetime.now(timezone.utc).isoformat()
    findings.append(finding("Audit", "info", base,
                            "audit complete: {} pages crawled, {} links sampled, {} sitemap URLs".format(
                                len(pages), len(to_check), len(entries))))

    if args.dry_run:
        print("[dry-run] would write {} TechnicalAudit rows".format(len(findings)))
        for f in findings:
            print("  [{Severity}] {Category} {URL} :: {Detail}".format(**f))
    else:
        airtable_key, base_id = require_env("AIRTABLE_API_KEY", "AIRTABLE_BIZOO_SEO_BASE_ID")
        airtable = AirtableClient(airtable_key, base_id)
        airtable.create_records(AUDIT_TABLE, [dict(f, CheckedAt=now_iso, Agent="Agent 02") for f in findings])

    lines = ["*Agent 02 audit* {} ({})".format(now_iso, domain)]
    lines.append("{} critical, {} warning, {} info across {} pages".format(
        counts["critical"], counts["warning"], counts["info"], len(pages)))
    criticals = [f for f in findings if f["Severity"] == "critical"]
    if criticals:
        lines.append("Critical findings (first 15):")
        lines.extend("  {Category} {URL} :: {Detail}".format(**f) for f in criticals[:15])
    digest = "\n".join(lines)
    print(digest)

    if not args.dry_run:
        post_slack(os.environ.get("SLACK_WEBHOOK_BIZOO_SEO"), digest)


def main():
    parser = argparse.ArgumentParser(description="Agent 02: Technical SEO Auditor")
    parser.add_argument("--max-pages", type=int, default=25, help="sitemap pages to crawl (default 25)")
    parser.add_argument("--max-links", type=int, default=50, help="internal links to status-check (default 50)")
    parser.add_argument("--cwv-pages", type=int, default=2,
                        help="pages through PageSpeed Insights, keyless quota is tight (default 2)")
    parser.add_argument("--inspect-sample", type=int, default=5,
                        help="pages through the GSC URL Inspection API (default 5)")
    parser.add_argument("--dry-run", action="store_true",
                        help="crawl and print findings, no Airtable writes, no Slack")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
