from __future__ import annotations

from typing import Any


def _quote_for(asset_or_metrics: dict[str, Any], convert: str = "USD") -> dict[str, Any]:
    quote = asset_or_metrics.get("quote") or {}
    if isinstance(quote, dict):
        return quote.get(convert.upper(), {}) or {}
    if isinstance(quote, list):
        for item in quote:
            if str(item.get("symbol", "")).upper() == convert.upper():
                return item
        return quote[0] if quote else {}
    return {}


def _num(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _asset_signals(asset: dict[str, Any], convert: str) -> dict[str, Any]:
    quote = _quote_for(asset, convert)
    change_1h = _num(quote.get("percent_change_1h"))
    change_24h = _num(quote.get("percent_change_24h"))
    change_7d = _num(quote.get("percent_change_7d"))
    market_cap = _num(quote.get("market_cap"))
    volume_24h = _num(quote.get("volume_24h"))
    volume_change_24h = _num(quote.get("volume_change_24h"))

    flags: list[str] = []

    if change_24h is not None:
        if abs(change_24h) >= 10:
            flags.append("large_24h_move")
        elif abs(change_24h) >= 5:
            flags.append("notable_24h_move")

    if change_1h is not None and abs(change_1h) >= 3:
        flags.append("fast_1h_move")

    if volume_change_24h is not None and abs(volume_change_24h) >= 50:
        flags.append("large_volume_change")

    if market_cap and volume_24h is not None and market_cap > 0:
        turnover = volume_24h / market_cap
        if turnover >= 0.20:
            flags.append("high_volume_to_market_cap")
    else:
        turnover = None

    return {
        "name": asset.get("name"),
        "symbol": asset.get("symbol"),
        "rank": asset.get("cmc_rank"),
        "price": _num(quote.get("price")),
        "percent_change_1h": change_1h,
        "percent_change_24h": change_24h,
        "percent_change_7d": change_7d,
        "volume_24h": volume_24h,
        "volume_change_24h": volume_change_24h,
        "market_cap": market_cap,
        "volume_to_market_cap": turnover,
        "last_updated": quote.get("last_updated") or asset.get("last_updated"),
        "flags": flags,
    }


def build_brief(
    quotes_payload: dict[str, Any],
    global_payload: dict[str, Any],
    fear_payload: dict[str, Any],
    convert: str = "USD",
) -> dict[str, Any]:
    assets_raw = quotes_payload.get("data") or []
    if isinstance(assets_raw, dict):
        assets_raw = list(assets_raw.values())

    assets = [_asset_signals(asset, convert) for asset in assets_raw]
    assets.sort(
        key=lambda item: abs(item["percent_change_24h"] or 0),
        reverse=True,
    )

    global_data = global_payload.get("data") or {}
    global_quote = _quote_for(global_data, convert)
    fear = fear_payload.get("data") or {}

    flagged = [asset["symbol"] for asset in assets if asset["flags"]]
    strongest = assets[0] if assets else None

    if strongest and strongest["percent_change_24h"] is not None:
        direction = "up" if strongest["percent_change_24h"] >= 0 else "down"
        headline = (
            f"{strongest['symbol']} has the largest 24h move in this watchlist: "
            f"{abs(strongest['percent_change_24h']):.2f}% {direction}."
        )
    else:
        headline = "No 24h price-change data is available for the requested assets."

    return {
        "headline": headline,
        "watchlist": [asset["symbol"] for asset in assets],
        "flagged_assets": flagged,
        "market": {
            "total_market_cap": _num(global_quote.get("total_market_cap")),
            "total_volume_24h": _num(global_quote.get("total_volume_24h")),
            "btc_dominance": _num(global_data.get("btc_dominance")),
            "eth_dominance": _num(global_data.get("eth_dominance")),
            "fear_greed_value": fear.get("value"),
            "fear_greed_classification": fear.get("value_classification"),
            "last_updated": (
                global_quote.get("last_updated")
                or global_data.get("last_updated")
                or fear.get("update_time")
            ),
        },
        "assets": assets,
        "methodology": {
            "notable_24h_move": "absolute 24h change >= 5%",
            "large_24h_move": "absolute 24h change >= 10%",
            "fast_1h_move": "absolute 1h change >= 3%",
            "large_volume_change": "absolute 24h volume change >= 50%",
            "high_volume_to_market_cap": "24h volume / market cap >= 20%",
        },
        "disclaimer": (
            "Descriptive market monitoring only. This output is not financial advice "
            "and does not predict future performance."
        ),
    }


def _money(value: float | None) -> str:
    if value is None:
        return "n/a"
    if abs(value) >= 1_000_000_000_000:
        return "$" + f"{value / 1_000_000_000_000:.2f}T"
    if abs(value) >= 1_000_000_000:
        return "$" + f"{value / 1_000_000_000:.2f}B"
    if abs(value) >= 1_000_000:
        return "$" + f"{value / 1_000_000:.2f}M"
    if abs(value) >= 1:
        return "$" + f"{value:,.2f}"
    return "$" + f"{value:.6f}"


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:+.2f}%"


def format_markdown(brief: dict[str, Any]) -> str:
    market = brief["market"]
    lines = [
        "# CMC Market Brief",
        "",
        brief["headline"],
        "",
        "## Market context",
        "",
        f"- Total market cap: {_money(market['total_market_cap'])}",
        f"- 24h market volume: {_money(market['total_volume_24h'])}",
        f"- BTC dominance: {_pct(market['btc_dominance'])}",
        f"- ETH dominance: {_pct(market['eth_dominance'])}",
        (
            "- Fear & Greed: "
            f"{market['fear_greed_value']} "
            f"({market['fear_greed_classification'] or 'n/a'})"
        ),
        "",
        "## Watchlist",
        "",
    ]

    for asset in brief["assets"]:
        flags = ", ".join(asset["flags"]) if asset["flags"] else "none"
        lines.extend(
            [
                f"### {asset['symbol']} — {asset['name']}",
                f"- Price: {_money(asset['price'])}",
                f"- 1h: {_pct(asset['percent_change_1h'])}",
                f"- 24h: {_pct(asset['percent_change_24h'])}",
                f"- 7d: {_pct(asset['percent_change_7d'])}",
                f"- 24h volume: {_money(asset['volume_24h'])}",
                f"- Signals: {flags}",
                "",
            ]
        )

    lines.extend(["---", brief["disclaimer"]])
    return "\n".join(lines)
