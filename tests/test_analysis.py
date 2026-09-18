from cmc_market_brief.analysis import build_brief, format_markdown
from cmc_market_brief.client import CMCClient


def _payloads():
    quotes = {
        "data": [
            {
                "id": 1,
                "name": "Bitcoin",
                "symbol": "BTC",
                "cmc_rank": 1,
                "quote": [
                    {
                        "symbol": "USD",
                        "price": 100000,
                        "volume_24h": 50000000000,
                        "volume_change_24h": 55,
                        "percent_change_1h": 1.2,
                        "percent_change_24h": 6.5,
                        "percent_change_7d": 8.0,
                        "market_cap": 2000000000000,
                    }
                ],
            },
            {
                "id": 1027,
                "name": "Ethereum",
                "symbol": "ETH",
                "cmc_rank": 2,
                "quote": [
                    {
                        "symbol": "USD",
                        "price": 4000,
                        "volume_24h": 30000000000,
                        "volume_change_24h": -10,
                        "percent_change_1h": -3.4,
                        "percent_change_24h": -11.5,
                        "percent_change_7d": -4.0,
                        "market_cap": 480000000000,
                    }
                ],
            },
        ]
    }
    global_metrics = {
        "data": {
            "btc_dominance": 58.2,
            "eth_dominance": 13.1,
            "quote": {
                "USD": {
                    "total_market_cap": 3500000000000,
                    "total_volume_24h": 140000000000,
                }
            },
        }
    }
    fear = {
        "data": {
            "value": 72,
            "value_classification": "Greed",
        }
    }
    return quotes, global_metrics, fear


def test_build_brief_flags_large_moves():
    brief = build_brief(*_payloads())
    assert brief["assets"][0]["symbol"] == "ETH"
    assert "large_24h_move" in brief["assets"][0]["flags"]
    btc = next(item for item in brief["assets"] if item["symbol"] == "BTC")
    assert "notable_24h_move" in btc["flags"]
    assert "large_volume_change" in btc["flags"]


def test_markdown_contains_market_context():
    brief = build_brief(*_payloads())
    output = format_markdown(brief)
    assert "# CMC Market Brief" in output
    assert "Fear & Greed: 72 (Greed)" in output
    assert "BTC" in output
    assert "ETH" in output


def test_client_uses_public_prefix_without_key():
    client = CMCClient(api_key="")
    url = client._url_for(
        "/v3/cryptocurrency/quotes/latest",
        {"symbol": "BTC", "convert": "USD"},
    )
    assert "/public-api/v3/cryptocurrency/quotes/latest" in url
    assert "symbol=BTC" in url


def test_client_uses_pro_endpoint_with_key():
    client = CMCClient(api_key="synthetic-test-key")
    url = client._url_for("/v3/cryptocurrency/quotes/latest")
    assert "/public-api/" not in url


def test_duplicate_symbols_choose_highest_rank():
    quotes, global_metrics, fear = _payloads()
    quotes["data"].append(
        {
            "id": 999999,
            "name": "Unrelated BTC ticker",
            "symbol": "BTC",
            "cmc_rank": 3500,
            "quote": [
                {
                    "symbol": "USD",
                    "price": 0.01,
                    "percent_change_24h": -80,
                    "market_cap": 10000,
                    "volume_24h": 100,
                }
            ],
        }
    )

    brief = build_brief(quotes, global_metrics, fear)
    btc_assets = [item for item in brief["assets"] if item["symbol"] == "BTC"]

    assert len(btc_assets) == 1
    assert btc_assets[0]["name"] == "Bitcoin"
