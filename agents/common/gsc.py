"""Google Search Console helpers shared by Agents 01, 02, 03.

Auth follows the shared AMG pattern (PRD section 5.3): a service account JSON
at GSC_SERVICE_ACCOUNT_JSON_PATH with the getbizoo.com property delegated to
it. The property is the domain form: sc-domain:getbizoo.com.

google-auth is imported lazily so agents that never touch GSC (Agent 12) do
not need it at import time.
"""

import os
from urllib.parse import quote

SCOPES = ["https://www.googleapis.com/auth/webmasters"]


def gsc_property():
    return "sc-domain:" + os.environ.get("BIZOO_DOMAIN", "getbizoo.com")


def gsc_session():
    """AuthorizedSession for GSC, or None when the service account file is absent."""
    path = os.environ.get("GSC_SERVICE_ACCOUNT_JSON_PATH", "")
    if not path or not os.path.exists(path):
        return None
    from google.auth.transport.requests import AuthorizedSession
    from google.oauth2 import service_account

    creds = service_account.Credentials.from_service_account_file(path, scopes=SCOPES)
    return AuthorizedSession(creds)


def search_analytics(session, body):
    """Run a Search Analytics query against the Bizoo property. Returns rows."""
    url = "https://searchconsole.googleapis.com/webmasters/v3/sites/{}/searchAnalytics/query".format(
        quote(gsc_property(), safe="")
    )
    resp = session.post(url, json=body, timeout=60)
    resp.raise_for_status()
    return resp.json().get("rows", [])
