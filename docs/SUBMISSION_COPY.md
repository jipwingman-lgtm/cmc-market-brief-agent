# Submission copy

## Project name

CMC Market Brief Agent

## Track

Markets and Trading Tools

## Short description

CMC Market Brief Agent turns live CoinMarketCap data into a compact watchlist brief with market context and transparent anomaly flags. It combines asset quotes, global market metrics, CMC Fear & Greed, and—when a Startup-tier key is configured—CMC Trending.

## What it does

A user enters a small crypto watchlist such as BTC, ETH, and SOL. The tool fetches live CoinMarketCap data and produces current prices, 1h/24h/7d changes, volume, market cap, market-wide context, sentiment, and deterministic flags for unusually large price or volume moves.

The project includes both a CLI and a local browser demo.

## CoinMarketCap endpoints

- GET /v3/cryptocurrency/quotes/latest
- GET /v1/global-metrics/quotes/latest
- GET /v3/fear-and-greed/latest
- GET /v1/cryptocurrency/trending/latest when Startup-tier access is configured

## What the API made possible

CoinMarketCap provides asset-level market data, global market context, and proprietary signals in one API. That lets the project create a compact market brief without combining several independent data providers. The CMC Fear & Greed endpoint adds sentiment context, while the Startup-tier Trending endpoint adds a discovery signal based on CoinMarketCap search activity.

## Limitation / friction

Ticker symbols are not globally unique, so a symbol query can return multiple assets. The project handles this by selecting the highest-ranked CMC asset for each requested symbol, while documenting that unique CMC IDs are the safer identifier for production use.

The first version uses point-in-time data and transparent rule thresholds. It does not predict future prices or recommend trades.

## Demo evidence

The repository includes a live-cmc-smoke GitHub Actions workflow that performs real keyless CoinMarketCap API calls and uploads the resulting evidence artifact. A verified market-data snapshot is also committed at docs/live-api-evidence.json.

## Repository

https://github.com/jipwingman-lgtm/cmc-market-brief-agent
