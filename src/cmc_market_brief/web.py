from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .analysis import build_brief
from .client import CMCClient


HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CMC Market Brief Agent</title>
  <style>
    :root { font-family: Inter, system-ui, sans-serif; color-scheme: dark; }
    body { margin: 0; background: #0b1020; color: #eef2ff; }
    main { max-width: 1100px; margin: 0 auto; padding: 40px 20px 64px; }
    h1 { margin-bottom: 8px; }
    .sub { color: #aab4d6; margin-top: 0; }
    .controls { display: flex; gap: 10px; margin: 24px 0; flex-wrap: wrap; }
    input, button { font: inherit; border-radius: 10px; border: 1px solid #33406a; padding: 10px 12px; }
    input { flex: 1; min-width: 240px; background: #111831; color: #fff; }
    button { background: #4967ff; color: white; cursor: pointer; border: 0; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
    .card { background: #111831; border: 1px solid #28345a; border-radius: 14px; padding: 18px; }
    .muted { color: #aab4d6; }
    .metric { font-size: 1.45rem; margin: 6px 0; }
    .flag { display: inline-block; background: #2b3457; border-radius: 999px; padding: 4px 8px; margin: 3px 4px 0 0; font-size: .8rem; }
    #status { margin: 12px 0; color: #aab4d6; }
    .error { color: #ff9c9c; white-space: pre-wrap; }
    footer { margin-top: 26px; color: #8692b8; font-size: .9rem; }
  </style>
</head>
<body>
<main>
  <h1>CMC Market Brief Agent</h1>
  <p class="sub">Live watchlist context and anomaly flags from CoinMarketCap data.</p>

  <div class="controls">
    <input id="symbols" value="BTC,ETH,SOL" aria-label="Symbols">
    <button id="load">Refresh live data</button>
  </div>

  <div id="status">Loading…</div>
  <section id="market" class="grid"></section>
  <h2>Watchlist</h2>
  <section id="assets" class="grid"></section>
  <section id="trending-wrap" style="display:none">
    <h2>CMC Trending</h2>
    <section id="trending" class="grid"></section>
  </section>

  <footer>Descriptive monitoring only. No price prediction or trading recommendation.</footer>
</main>

<script>
const fmtMoney = value => {
  if (value === null || value === undefined) return "n/a";
  const n = Number(value);
  if (Math.abs(n) >= 1e12) return "$" + (n / 1e12).toFixed(2) + "T";
  if (Math.abs(n) >= 1e9) return "$" + (n / 1e9).toFixed(2) + "B";
  if (Math.abs(n) >= 1e6) return "$" + (n / 1e6).toFixed(2) + "M";
  return "$" + n.toLocaleString(undefined, {maximumFractionDigits: 6});
};
const fmtPct = value => value === null || value === undefined
  ? "n/a"
  : (Number(value) >= 0 ? "+" : "") + Number(value).toFixed(2) + "%";

function card(title, body) {
  return '<article class="card"><div class="muted">' + title + '</div>' + body + '</article>';
}

async function load() {
  const symbols = document.getElementById("symbols").value.trim() || "BTC,ETH,SOL";
  const status = document.getElementById("status");
  status.className = "";
  status.textContent = "Calling CoinMarketCap…";

  try {
    const response = await fetch("/api/brief?symbols=" + encodeURIComponent(symbols));
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Request failed");

    const m = payload.market;
    document.getElementById("market").innerHTML = [
      card("Headline", '<div class="metric">' + payload.headline + '</div>'),
      card("Total market cap", '<div class="metric">' + fmtMoney(m.total_market_cap) + '</div>'),
      card("24h market volume", '<div class="metric">' + fmtMoney(m.total_volume_24h) + '</div>'),
      card("BTC dominance", '<div class="metric">' + fmtPct(m.btc_dominance) + '</div>'),
      card("Fear & Greed", '<div class="metric">' + m.fear_greed_value + ' — ' + m.fear_greed_classification + '</div>')
    ].join("");

    document.getElementById("assets").innerHTML = payload.assets.map(a => {
      const flags = a.flags.length
        ? a.flags.map(f => '<span class="flag">' + f + '</span>').join("")
        : '<span class="muted">No anomaly flags</span>';
      return card(
        a.symbol + " — " + a.name,
        '<div class="metric">' + fmtMoney(a.price) + '</div>' +
        '<div>1h ' + fmtPct(a.percent_change_1h) + ' · 24h ' + fmtPct(a.percent_change_24h) + ' · 7d ' + fmtPct(a.percent_change_7d) + '</div>' +
        '<div style="margin-top:10px">' + flags + '</div>'
      );
    }).join("");

    const trendWrap = document.getElementById("trending-wrap");
    if (payload.trending && payload.trending.length) {
      trendWrap.style.display = "block";
      document.getElementById("trending").innerHTML = payload.trending.map(a =>
        card(
          a.symbol + " — " + a.name,
          '<div class="metric">' + fmtMoney(a.price) + '</div>' +
          '<div>24h ' + fmtPct(a.percent_change_24h) + '</div>'
        )
      ).join("");
    } else {
      trendWrap.style.display = "none";
    }

    status.textContent = "Live CMC data loaded.";
  } catch (err) {
    status.className = "error";
    status.textContent = String(err);
  }
}

document.getElementById("load").addEventListener("click", load);
load();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/":
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed.path == "/api/brief":
            try:
                query = parse_qs(parsed.query)
                raw_symbols = query.get("symbols", ["BTC,ETH,SOL"])[0]
                symbols = [
                    item.strip().upper()
                    for item in raw_symbols.split(",")
                    if item.strip()
                ][:20]
                client = CMCClient()
                quotes = client.quotes(symbols)
                global_metrics = client.global_metrics()
                fear = client.fear_and_greed()

                trending = None
                if not client.keyless:
                    try:
                        trending = client.trending(limit=5)
                    except RuntimeError:
                        trending = None

                brief = build_brief(
                    quotes,
                    global_metrics,
                    fear,
                    trending_payload=trending,
                )
                self._json(200, brief)
            except Exception as exc:
                self._json(500, {"error": str(exc)})
            return

        self._json(404, {"error": "Not found"})

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        print(format % args)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local CMC Market Brief demo.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"CMC Market Brief Agent: http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
