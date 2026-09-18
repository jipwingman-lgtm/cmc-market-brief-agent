# Demo recording guide

The hackathon accepts a working demo, deployed link, or screen recording. This project includes a local browser demo so no deployment is required for a valid recording.

## Before recording

Install the project:

    python -m venv .venv
    source .venv/bin/activate
    pip install -e .

Optional after the hackathon Startup tier is activated:

    export CMC_API_KEY="your-key"

Never show the key on screen.

## Start the demo

    cmc-brief-web

Open:

    http://127.0.0.1:8000

## Suggested 45-second recording

1. Show the GitHub repository name and README.
2. Open the local dashboard.
3. Point out the total market cap, BTC dominance, and CMC Fear & Greed cards.
4. Show BTC, ETH, and SOL watchlist cards.
5. Change the symbols field and click "Refresh live data".
6. Point out any anomaly flags.
7. If a Startup key is configured, show the CMC Trending section.
8. Briefly show docs/live-api-evidence.json and the successful live-cmc-smoke GitHub Actions run.

## What to say

- The project uses live CoinMarketCap data.
- The keyless demo uses quotes, global metrics, and CMC Fear & Greed.
- A Startup key additionally enables CMC Trending.
- The anomaly rules are deterministic and visible in the README.
- The tool is descriptive monitoring and does not predict prices or recommend trades.
- No API key is committed to the repository.
