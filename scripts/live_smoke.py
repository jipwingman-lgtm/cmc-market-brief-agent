from __future__ import annotations

import json
from pathlib import Path

from cmc_market_brief.analysis import build_brief
from cmc_market_brief.client import CMCClient


def main() -> None:
    symbols = ["BTC", "ETH", "SOL"]
    client = CMCClient(api_key="")
    quotes = client.quotes(symbols)
    global_metrics = client.global_metrics()
    fear = client.fear_and_greed()
    brief = build_brief(quotes, global_metrics, fear)

    evidence = {
        "source": "CoinMarketCap keyless public API",
        "requested_symbols": symbols,
        "endpoints": [
            "/public-api/v3/cryptocurrency/quotes/latest",
            "/public-api/v1/global-metrics/quotes/latest",
            "/public-api/v3/fear-and-greed/latest",
        ],
        "status_timestamps": {
            "quotes": (quotes.get("status") or {}).get("timestamp"),
            "global_metrics": (global_metrics.get("status") or {}).get("timestamp"),
            "fear_and_greed": (fear.get("status") or {}).get("timestamp"),
        },
        "brief": brief,
    }

    output = json.dumps(evidence, indent=2, ensure_ascii=False)
    Path("live-evidence.json").write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
