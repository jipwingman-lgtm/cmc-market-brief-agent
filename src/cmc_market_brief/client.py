from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = "https://pro-api.coinmarketcap.com"


class CMCClient:
    """Small CoinMarketCap client with keyless fallback."""

    def __init__(self, api_key: str | None = None, timeout: float = 15.0) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("CMC_API_KEY", "")
        self.timeout = timeout

    @property
    def keyless(self) -> bool:
        return not bool(self.api_key)

    def _url_for(self, path: str, params: dict[str, Any] | None = None) -> str:
        if not path.startswith("/"):
            path = "/" + path
        prefix = "/public-api" if self.keyless else ""
        url = f"{BASE_URL}{prefix}{path}"
        if params:
            url += "?" + urlencode(params)
        return url

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "cmc-market-brief-agent/0.1",
        }
        if self.api_key:
            headers["X-CMC_PRO_API_KEY"] = self.api_key

        request = Request(self._url_for(path, params), headers=headers)
        with urlopen(request, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))

        status = payload.get("status") or {}
        if status.get("error_code") not in (None, 0):
            raise RuntimeError(status.get("error_message") or "CoinMarketCap API error")
        return payload

    def quotes(self, symbols: list[str], convert: str = "USD") -> dict[str, Any]:
        clean = [symbol.strip().upper() for symbol in symbols if symbol.strip()]
        if not clean:
            raise ValueError("At least one symbol is required.")
        return self._get(
            "/v3/cryptocurrency/quotes/latest",
            {
                "symbol": ",".join(clean),
                "convert": convert.upper(),
                "skip_invalid": "true",
            },
        )

    def global_metrics(self, convert: str = "USD") -> dict[str, Any]:
        return self._get(
            "/v1/global-metrics/quotes/latest",
            {"convert": convert.upper()},
        )

    def fear_and_greed(self) -> dict[str, Any]:
        return self._get("/v3/fear-and-greed/latest")

    def trending(self, limit: int = 5, convert: str = "USD") -> dict[str, Any]:
        if self.keyless:
            raise RuntimeError("Trending requires a CoinMarketCap API key.")
        return self._get(
            "/v1/cryptocurrency/trending/latest",
            {"limit": max(1, min(limit, 100)), "convert": convert.upper()},
        )
