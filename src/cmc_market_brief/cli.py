from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analysis import build_brief, format_markdown
from .client import CMCClient


ENDPOINTS = [
    "/v3/cryptocurrency/quotes/latest",
    "/v1/global-metrics/quotes/latest",
    "/v3/fear-and-greed/latest",
]


def _evidence(
    symbols: list[str],
    quote_payload: dict,
    global_payload: dict,
    fear_payload: dict,
    brief: dict,
) -> dict:
    return {
        "source": "CoinMarketCap API",
        "mode": "keyless-public-api",
        "requested_symbols": symbols,
        "endpoints": ENDPOINTS,
        "status_timestamps": {
            "quotes": (quote_payload.get("status") or {}).get("timestamp"),
            "global_metrics": (global_payload.get("status") or {}).get("timestamp"),
            "fear_and_greed": (fear_payload.get("status") or {}).get("timestamp"),
        },
        "brief": brief,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cmc-brief",
        description="Build a live crypto market brief from CoinMarketCap data.",
    )
    parser.add_argument(
        "symbols",
        nargs="*",
        default=["BTC", "ETH", "SOL"],
        help="Crypto symbols to monitor. Default: BTC ETH SOL",
    )
    parser.add_argument("--convert", default="USD")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of Markdown.",
    )
    parser.add_argument(
        "--evidence",
        help="Write a safe evidence JSON file containing market data, never the API key.",
    )
    args = parser.parse_args()

    symbols = [symbol.upper() for symbol in args.symbols]
    client = CMCClient()

    quotes = client.quotes(symbols, args.convert)
    global_metrics = client.global_metrics(args.convert)
    fear = client.fear_and_greed()
    brief = build_brief(quotes, global_metrics, fear, args.convert)

    if args.evidence:
        evidence = _evidence(symbols, quotes, global_metrics, fear, brief)
        Path(args.evidence).write_text(
            json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    if args.json:
        print(json.dumps(brief, indent=2, ensure_ascii=False))
    else:
        print(format_markdown(brief))


if __name__ == "__main__":
    main()
