"""Minimal Airtable REST client shared by all agents.

Covers exactly what the agents need: paginated list, batched create, batched
update. Airtable limits: 5 requests/second per base (throttled here), 10
records per write request (batched here). Writes use typecast so select
options are created on first use.
"""

import time

import requests

API_URL = "https://api.airtable.com/v0"


class AirtableClient:
    def __init__(self, api_key, base_id, min_interval=0.25):
        self.base_id = base_id
        self.session = requests.Session()
        self.session.headers.update({"Authorization": "Bearer " + api_key})
        self.min_interval = min_interval
        self._last_request = 0.0

    def _throttle(self):
        wait = self.min_interval - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        self._last_request = time.monotonic()

    def _request(self, method, table, **kwargs):
        self._throttle()
        url = "{}/{}/{}".format(API_URL, self.base_id, requests.utils.quote(table))
        resp = self.session.request(method, url, timeout=30, **kwargs)
        if resp.status_code == 429:
            time.sleep(31)
            resp = self.session.request(method, url, timeout=30, **kwargs)
        if not resp.ok:
            raise RuntimeError(
                "Airtable {} {} failed ({}): {}".format(method, table, resp.status_code, resp.text[:300])
            )
        return resp.json()

    def list_records(self, table, formula=None, fields=None, max_records=None):
        """Return all records (dicts with id, createdTime, fields), following pagination."""
        records = []
        params = {}
        if formula:
            params["filterByFormula"] = formula
        if fields:
            params["fields[]"] = fields
        if max_records:
            params["maxRecords"] = max_records
        while True:
            data = self._request("GET", table, params=params)
            records.extend(data.get("records", []))
            offset = data.get("offset")
            if not offset:
                return records
            params["offset"] = offset

    def create_records(self, table, fields_list):
        """Create records in batches of 10. None values are stripped. Returns created records."""
        created = []
        for i in range(0, len(fields_list), 10):
            batch = [
                {"fields": {k: v for k, v in f.items() if v is not None}}
                for f in fields_list[i : i + 10]
            ]
            data = self._request("POST", table, json={"records": batch, "typecast": True})
            created.extend(data["records"])
        return created

    def update_records(self, table, updates):
        """Patch records. updates: list of (record_id, fields) tuples. Batches of 10."""
        updated = []
        for i in range(0, len(updates), 10):
            batch = [{"id": rid, "fields": f} for rid, f in updates[i : i + 10]]
            data = self._request("PATCH", table, json={"records": batch, "typecast": True})
            updated.extend(data["records"])
        return updated
