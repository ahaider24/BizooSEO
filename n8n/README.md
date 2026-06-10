# n8n Workflows

Exported workflow JSON lives here, one file per workflow. Import into the
Bizoo folder namespace on the shared n8n instance (separate from AMG's).

| File | Workflow | PRD ref |
|---|---|---|
| wf01_landing_page_intake.json | Landing Page Intake | §10 |
| wf02_seo_attribution_enricher.json | SEO Attribution Enricher (conversions++ feedback loop) | §10 |
| wf03_amg_crossconnect_sync.json | AMG Cross-connect Sync | §10 |
| wf04_stage_advancement_stripe.json | Stage Advancement + Stripe Sync | §10 |
| agent_triggers/ | Cron + webhook triggers for Agents 01-15 | §6 |

Export from n8n after any change and commit, so workflows are version-controlled.
