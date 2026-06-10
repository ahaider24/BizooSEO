# agents/common

Shared runtime helpers imported by every agent's `main.py`:

- `config.py`: loads `.env` from the repo root (droplet: `/home/bizoo/engine/.env`), `require_env` guards with clear messages, `load_competitors()` for `config/competitors.yml`.
- `airtable.py`: minimal Airtable REST client (pagination, 10-record write batches, 5 rps throttle, one 429 retry, typecast on writes so select options auto-create).
- `slack.py`: incoming-webhook poster; prints a note instead of failing when the webhook is unset.
- `gsc.py`: Search Console service-account auth (`GSC_SERVICE_ACCOUNT_JSON_PATH`, shared AMG pattern) and a Search Analytics query helper. Property form: `sc-domain:{BIZOO_DOMAIN}`.

Each agent's `main.py` adds the repo root to `sys.path` at startup, so `python main.py` works from inside any agent directory with no install step beyond `pip install -r requirements.txt` at the repo root.
