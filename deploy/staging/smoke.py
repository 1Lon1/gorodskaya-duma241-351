"""Verify the staged API and remove the deputy used by the probe."""

import json
import sys
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE_URL = "http://127.0.0.1:18080"


def request(path, *, method="GET", payload=None, token=None):
    headers = {}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode() if payload is not None else None
    http_request = Request(BASE_URL + path, method=method, data=data, headers=headers)
    try:
        with urlopen(http_request, timeout=5) as response:
            return json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f"{method} {path} returned HTTP {exc.code}") from exc


def verify(revision, credentials):
    health = request("/api/health")
    if health.get("status") != "ok":
        raise RuntimeError("Unexpected health response")
    version = request("/version")
    if version.get("revision") != revision or not version.get("version"):
        raise RuntimeError(f"/version did not report the expected revision {revision}")
    print(f"OK health and /version ({revision})", flush=True)

    try:
        login = request("/api/auth/login", method="POST", payload=credentials)
    except RuntimeError as exc:
        if not isinstance(exc.__cause__, HTTPError) or exc.__cause__.code != 401:
            raise
        request("/api/auth/register", method="POST", payload=credentials)
        login = request("/api/auth/login", method="POST", payload=credentials)
    token = login["access_token"]
    deputy = {
        "full_name": f"CD smoke {uuid.uuid4().hex}",
        "party": "CD smoke",
        "district": "1",
    }
    created = request("/api/deputies", method="POST", payload=deputy, token=token)
    deputy_path = f"/api/deputies/{created['id']}"
    try:
        record = request(deputy_path)
        if any(record.get(key) != value for key, value in deputy.items()):
            raise RuntimeError("The API returned unexpected deputy data")
    finally:
        request(deputy_path, method="DELETE", token=token)
    try:
        request(deputy_path)
    except RuntimeError as exc:
        if isinstance(exc.__cause__, HTTPError) and exc.__cause__.code == 404:
            print("OK login, create, read and delete a deputy", flush=True)
            return
        raise
    raise RuntimeError("Deleted deputy is still accessible")


if __name__ == "__main__":
    try:
        with open("smoke.json", encoding="utf-8") as credentials_file:
            verify(sys.argv[1], json.load(credentials_file))
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        sys.exit(f"Smoke test failed: {error}")
