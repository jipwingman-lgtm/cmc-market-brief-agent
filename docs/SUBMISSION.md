# Hackathon submission checklist

Track: **Markets and Trading Tools**

## Working product

- [x] Public-data CoinMarketCap client
- [x] Live quotes for requested assets
- [x] Global market metrics
- [x] CMC Fear & Greed Index
- [x] Rule-based anomaly flags
- [x] Markdown and JSON output
- [x] Automated unit tests
- [x] Live API smoke workflow
- [ ] Public repository
- [x] Local browser demo
- [ ] Demo video or deployed demo
- [ ] DoraHacks submission
- [ ] X post with #BuildwithCMC

## CMC endpoints used

- GET /v3/cryptocurrency/quotes/latest
- GET /v1/global-metrics/quotes/latest
- GET /v3/fear-and-greed/latest
- GET /v1/cryptocurrency/trending/latest (Startup tier and above)

The live smoke workflow calls the keyless /public-api equivalents of the first three endpoints. Trending is activated automatically when CMC_API_KEY is configured.

## What CMC made possible

One API supplies per-asset prices and changes, global market context, and CoinMarketCap's proprietary Fear & Greed value. That makes it possible to turn several market signals into one compact watchlist brief without stitching together multiple data providers.

## Current limitation

The first version uses point-in-time market data and deterministic thresholds. It does not predict prices or recommend trades. Historical baselines, user-configurable alert rules, and Startup-tier endpoints can be added during the hackathon.

## Required final links

Repository: https://github.com/jipwingman-lgtm/cmc-market-brief-agent

Demo/video: TODO

DoraHacks submission: TODO

X post: TODO
