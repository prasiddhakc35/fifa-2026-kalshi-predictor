#!/usr/bin/env python3
"""
PitchPredict -> Kalshi trading engine (starter skeleton)
=========================================================
Reads the Poisson model's probabilities, pulls live Kalshi prices, finds spots
where the model disagrees with the market, sizes a quarter-Kelly stake, and
prints the recommended trades.

IMPORTANT — read before using:
  * LIVE TRADING IS OFF. DRY_RUN=True only prints; it never sends an order.
  * Autonomous real-money trading is YOUR decision and YOUR risk. A model edge
    is not a guarantee; bankrolls can go to zero. Check that Kalshi (or your
    local prediction market) is legal for you, and start with money you can lose.
  * You need your own Kalshi account + API key. Get one at kalshi.com, then set:
        export KALSHI_KEY_ID="..."
        export KALSHI_PRIVATE_KEY_PATH="/path/to/key.pem"
  * Kalshi's API requires RSA-signed request headers. The sign/auth bits below
    are stubbed with TODOs — fill them from Kalshi's current API docs
    (docs.kalshi.com). Endpoints/series tickers change, so verify them live.

Dependencies:  pip install requests cryptography
"""

import os, json, time, datetime as dt

# ----------------------------- config -------------------------------------
DRY_RUN        = True       # << keep True until you have read all the code
BANKROLL       = 50.00      # starting cash you're allocating to the bot ($)
KELLY_FRACTION = 0.25       # quarter-Kelly = conservative sizing
MIN_EDGE_CENTS = 3          # only trade if model% beats market price by >= this
MAX_PER_TRADE  = 0.10       # never stake more than 10% of bankroll on one market
MODEL_FILE     = os.path.join(os.path.dirname(__file__), "r32_data.json")
KALSHI_BASE    = "https://api.elections.kalshi.com/trade-api/v2"  # verify in docs

# ------------------------- 1) load the model ------------------------------
def load_model():
    """Return list of {ticker_hint, label, model_prob} the bot will shop for."""
    data = json.load(open(MODEL_FILE))
    rows = []
    for m in data:
        # advancement markets (the cleanest mapping to a Kalshi Yes/No contract)
        rows.append({"match": f'{m["a"]} vs {m["b"]}',
                     "label": f'{m["a"]} to advance', "prob": m["advA"]})
        rows.append({"match": f'{m["a"]} vs {m["b"]}',
                     "label": f'{m["b"]} to advance', "prob": m["advB"]})
    return rows

# --------------------- 2) Kalshi API (auth stubs) -------------------------
def kalshi_headers(method, path):
    """
    TODO: Kalshi signs each request with your RSA private key.
    Build the timestamp + signature headers per docs.kalshi.com.
    Returns a dict of headers. Left unimplemented on purpose.
    """
    raise NotImplementedError("Fill in Kalshi RSA request signing from their API docs.")

def get_market_price(series_ticker):
    """
    TODO: GET {KALSHI_BASE}/markets?series_ticker=...  (or /markets/{ticker})
    and return the current YES ask price in cents (1-99).
    Returns None if not found. Stubbed to keep the bot non-live.
    """
    return None  # replace with a real request once auth works

def place_order(ticker, side, count, price_cents):
    """TODO: POST {KALSHI_BASE}/portfolio/orders  — DO NOT enable lightly."""
    raise NotImplementedError("Order placement intentionally not implemented.")

# --------------------------- 3) sizing ------------------------------------
def quarter_kelly_stake(model_prob, price_cents, cash):
    p = price_cents / 100.0
    q = model_prob / 100.0
    b = (1.0 / p) - 1.0                 # net decimal odds
    kelly = (b * q - (1 - q)) / b       # full-Kelly fraction
    f = max(0.0, KELLY_FRACTION * kelly)
    return round(min(cash * MAX_PER_TRADE, f * cash), 2)

# --------------------------- 4) main loop ---------------------------------
def run_once(cash):
    rows = load_model()
    print(f"\n[{dt.datetime.now():%H:%M:%S}] scanning {len(rows)} markets · cash ${cash:.2f}")
    picks = []
    for r in rows:
        price = get_market_price(r["label"])      # None until you wire the API
        if price is None:
            continue
        edge = r["prob"] - price
        if edge >= MIN_EDGE_CENTS:
            stake = quarter_kelly_stake(r["prob"], price, cash)
            if stake >= 1:
                picks.append({**r, "price": price, "edge": edge, "stake": stake,
                              "mult": round(100 / price, 2)})

    if not picks:
        print("  no qualifying edges right now (or API not wired yet).")
        return cash

    picks.sort(key=lambda x: -x["edge"])
    for p in picks:
        line = (f'  BUY {p["label"]:<26} @ {p["price"]}c  '
                f'model {p["prob"]:.0f}%  edge +{p["edge"]:.0f}c  '
                f'stake ${p["stake"]:.2f}  ({p["mult"]}x)')
        print(line)
        if not DRY_RUN:
            # place_order(p["ticker"], "yes", contracts, p["price"])  # you wire this
            pass
    return cash

if __name__ == "__main__":
    print("PitchPredict x Kalshi — DRY_RUN =", DRY_RUN)
    if not os.path.exists(MODEL_FILE):
        raise SystemExit("Run the model first to create r32_data.json")
    # Single pass. For a real bot, loop on a timer and persist cash/positions.
    run_once(BANKROLL)
    print("\nDone. Nothing was traded (dry run). Wire the API stubs to go live at your own risk.")
