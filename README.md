# CMC Market Brief Agent

A compact crypto market brief and anomaly monitor powered by the CoinMarketCap API.

Built for the **Build with CMC: API Hackathon** in the **Markets and Trading Tools** track.

## What it does

Give the CLI a watchlist such as BTC, ETH, and SOL. It fetches live CoinMarketCap data and returns:

- latest price
- 1h, 24h, and 7d percentage changes
- 24h volume
- market cap
- BTC and ETH market dominance
- total crypto market cap and 24h market volume
- CMC Crypto Fear & Greed
- deterministic anomaly flags for unusually large price or volume moves

The output is descriptive monitoring only. It does not predict prices or recommend trades.

## Why CoinMarketCap

The project combines three CMC data surfaces in one small workflow:

1. **Cryptocurrency quotes** for asset-level prices, market caps, volume, and price changes.
2. **Global metrics** for whole-market context and dominance.
3. **CMC Fear & Greed** for a proprietary market-sentiment signal.

This gives a user both the watchlist and the market backdrop in one command.

## Endpoints used

Keyed Pro API paths:

    GET /v3/cryptocurrency/quotes/latest
    GET /v1/global-metrics/quotes/latest
    GET /v3/fear-and-greed/latest

Without CMC_API_KEY, the client automatically uses the matching keyless public paths under:

    https://pro-api.coinmarketcap.com/public-api/

The response structure stays compatible, so moving from the public demo to a keyed plan does not require a parser rewrite.

## Install

Requirements:

- Python 3.10+
- Internet access

Clone and install:

    git clone https://github.com/jipwingman-lgtm/cmc-market-brief-agent.git
    cd cmc-market-brief-agent
    python -m venv .venv
    source .venv/bin/activate
    pip install -e .

Windows PowerShell:

    .venv\Scripts\Activate.ps1
    pip install -e .

## Run without an API key

The default workflow uses CoinMarketCap's keyless public API:

    cmc-brief BTC ETH SOL

For JSON:

    cmc-brief BTC ETH SOL --json

To save hackathon-safe API evidence:

    cmc-brief BTC ETH SOL --evidence live-evidence.json

The evidence file contains market data, endpoint names, and API response timestamps. It never includes an API key.

## Run with a CoinMarketCap API key

After registering for a CoinMarketCap API plan, set the key locally:

    export CMC_API_KEY="your-key"

Then run the same command:

    cmc-brief BTC ETH SOL

The client automatically switches from the keyless public path to the standard Pro API path.

Never commit the key. See SECURITY.md.

## Anomaly rules

The first version intentionally uses transparent deterministic thresholds:

| Signal | Rule |
| --- | --- |
| notable_24h_move | absolute 24h change >= 5% |
| large_24h_move | absolute 24h change >= 10% |
| fast_1h_move | absolute 1h change >= 3% |
| large_volume_change | absolute 24h volume change >= 50% |
| high_volume_to_market_cap | 24h volume / market cap >= 20% |

These rules are easy to inspect and change. They are market-monitoring signals, not trading recommendations.

## Live API evidence

The repository includes a GitHub Actions workflow:

    .github/workflows/live-smoke.yml

It makes real keyless requests to CoinMarketCap for BTC, ETH, and SOL, prints the resulting market brief, and uploads a live-cmc-evidence artifact.

This provides visible evidence that the project is making real CMC API calls without putting a private API key into the repository.

## Tests

Install development dependencies and run:

    pip install -e ".[dev]"
    pytest -q

Unit tests use synthetic market data and do not spend API credits.

## Project structure

    src/cmc_market_brief/client.py     CoinMarketCap HTTP client
    src/cmc_market_brief/analysis.py   transparent anomaly detection
    src/cmc_market_brief/cli.py        command-line interface
    scripts/live_smoke.py              real public-API smoke test
    tests/test_analysis.py             offline unit tests
    docs/SUBMISSION.md                 hackathon checklist

## Hackathon status

- [x] Working CoinMarketCap client
- [x] Real-time crypto quotes
- [x] Global market metrics
- [x] CMC Fear & Greed
- [x] Anomaly monitor
- [x] CLI output in Markdown and JSON
- [x] Unit tests
- [x] Live API smoke workflow
- [ ] Public repository
- [ ] Demo video
- [ ] DoraHacks submission
- [ ] X post with #BuildwithCMC

## Roadmap

- user-configurable alert thresholds
- historical baselines
- watchlist presets
- scheduled alert mode
- optional Startup-tier signals
- small web dashboard
- exportable demo snapshots

## License

MIT
