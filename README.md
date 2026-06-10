# BizooSEO

Multi-agent SEO/GEO engine for Bizoo (getbizoo.com), the diligence-first financial operating system.

**Canonical spec:** [`docs/bizoo_seo_prd_v2.0.md`](docs/bizoo_seo_prd_v2.0.md). All build work executes against that document. Changes amend the PRD directly with a changelog entry; no addendum documents.

## Positioning Spine

> The model you plan with is the model you get diligenced on.

Never market as "an FP&A platform." The category is diligence-ready planning.

## Repo Structure

```
docs/        Canonical PRD + future specs
agents/      Agents 01-15, one Python module each (see agents/README.md)
config/      Environment template, CitationTargets seed, competitor list
n8n/         Exported n8n workflow JSON (WF-01 through WF-04 + agent triggers)
templates/   Agent 09 page templates: deals, drivers glossary
```

## Conventions

- **Dual-push remotes.** `git push` lands on both `ahaider24/BizooSEO` and `getbizoo/BizooSEO`. Verify with `git remote -v` (one fetch, two pushes). Sync both after every change, no exceptions.
- **Runtime:** DigitalOcean droplet at `/home/bizoo/engine/`, n8n-orchestrated, Airtable data layer, Slack alerts (#bizoo-seo, #bizoo-crm).
- **Executor:** Claude Code runs the repo. Strategy lives in the PRD.
- **Primary KPI:** Citation Share, per pillar. Rank is a secondary view.
- **No em dashes in any written output.** Commas, colons, periods, parentheses.

## Quick Links

- PRD v2.0: `docs/bizoo_seo_prd_v2.0.md`
- Decision Gates: PRD §12 (DG-1 and DG-2 gate the July content launch)
- Roadmap: PRD §11
