"""Environment and config loading shared by all agents.

The droplet convention (config/.env.example) is a single .env at the repo
root: /home/bizoo/engine/.env. Locally the same file sits at the repo root.
"""

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def load_env(env_path=None):
    """Load KEY=VALUE pairs from .env into os.environ.

    Existing environment values win; the file only fills gaps. Missing file
    is fine (CI, or everything already exported in the shell).
    """
    path = Path(env_path) if env_path else REPO_ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def require_env(*names):
    """Return the values of the named env vars, exiting clearly if any are missing."""
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        raise SystemExit(
            "Missing required environment variables: "
            + ", ".join(missing)
            + ". Copy config/.env.example to .env at the repo root and fill them in."
        )
    return [os.environ[n] for n in names]


def load_competitors(include_disambiguation=False):
    """Flat list of tracked competitor domains from config/competitors.yml.

    Excludes disambiguation_only domains by default: mosaic.tech is not a
    competitor (PRD section 4), it is tracked only so entity linking resolves
    "Mosaic" correctly.
    """
    import yaml

    data = yaml.safe_load((REPO_ROOT / "config" / "competitors.yml").read_text())
    domains = []
    for front in (data.get("direct") or {}).values():
        domains.extend(front)
    domains.extend(data.get("tracked") or [])
    if include_disambiguation:
        domains.extend(data.get("disambiguation_only") or [])
    return domains
