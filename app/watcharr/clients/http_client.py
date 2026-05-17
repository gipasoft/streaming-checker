from __future__ import annotations

import requests


class HttpClient:
    def __init__(self, base_url: str, headers: dict[str, str] | None = None, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout

    def request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = dict(self.headers)
        headers.update(kwargs.pop("headers", {}) or {})

        response = requests.request(method, url, headers=headers, timeout=self.timeout, **kwargs)
        response.raise_for_status()

        if response.status_code == 204 or not response.text:
            return None
        return response.json()

    def get(self, path: str, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs):
        return self.request("PUT", path, **kwargs)

