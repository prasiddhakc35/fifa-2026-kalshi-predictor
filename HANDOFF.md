# HANDOFF — FIFA 2026 World Cup × Kalshi Prediction Project

> Single-page handoff for Claude Code (or any new dev/assistant). Read this top
> to bottom. It lists every file with its full path, what each does, the current
> state, how to run things, and what to do next. The deeper methodology + tuning
> notes live in `CLAUDE.md` (auto-loaded when this folder opens).

---

## 1. One-line summary

A football match-prediction engine for the **2026 FIFA World Cup**, wrapped in a
**Kalshi-style prediction-market app**. A Poisson model turns team strength into
win/draw/advance probabilities → market-style prices (cents = implied %) →
bet sizing (¼-Kelly), edge vs market, and a running portfolio. Goal: grow a small
bankroll ($10–$100) over the tournament by compounding small edges, build toward
an automatic Kalshi bot, and use it as a resume/portfolio piece.

**Current stage:** Group stage done. Model covers all **16 Round-of-32** matches.
Demo match: **Brazil vs Japan (Jun 29, Houston)**.

---

## 2. Folder location

Everything lives in:

```
/Users/prasiddhakc/Claude/Projects/Fifa Kalshi prediction/
```

---

## 3. Every file (full paths)

| File (full path) | Size | What it is |
|---|---|---|
| `/Users/prasiddhakc/Claude/Projects/Fifa Kalshi prediction/CLAUDE.md` | 12K | **Master handoff / project memory.** Goals, honesty rules, full model methodology, team ratings, rebuild instructions, roadmap, conventions. Auto-loads when the folder opens. |
| `/Users/prasiddhakc/Claude/Projects/Fifa Kalshi prediction/HANDOFF.md` | this file | Quick-reference handoff with all paths + run steps. |
| `/Users/prasiddhakc/Claude/Projects/Fifa Kalshi prediction/index.html` | 32K | **Main deliverable.** Self-contained interactive Kalshi-style app: flags grid → match stats/odds → bet ticket (multiplier, edge, ¼-Kelly) → live portfolio (persists via `localStorage`) → growth projection. Open in any browser, no server. |
| `/Users/prasiddhakc/Claude/Projects/Fifa Kalshi prediction/r32_data.json` | 8K | **Model output**, list of 16 R32 matches. Per-match keys: `id, date, venue, a, af, asum, b, bf, bsum, xgA, xgB, pA, pD, pB, advA, advB, over25, btts, scores`. The HTML embeds a copy; the bot reads this file. |
| `/Users/prasiddhakc/Claude/Projects/Fifa Kalshi prediction/kalshi_bot.py` | 8K | **Trading-bot skeleton.** Reads `r32_data.json`, built to pull live Kalshi prices, find edges, size ¼-Kelly. `DRY_RUN=True` (prints only, places nothing). Auth + order endpoints are TODO stubs. |
| `/Users/prasiddhakc/Claude/Projects/Fifa Kalshi prediction/PitchPredict Blueprint 2.pdf` | 128K | The methodology guide / source of truth for the approach. |

> Not in the folder: the Python that generated the model (`model.py`,
> `allmatches.py`) ran in a sandbox. The canonical output is `r32_data.json`;
> the generating logic is reproduced in `CLAUDE.md` §6 so it can be rebuilt.

---

## 4. The model in brief

Goals follow a **Poisson distribution**. Per team per match:

```
expected_goals(team) = BASE × Attack(team) × Defense(opponent) × Location(team)
BASE = 1.35
```

Build a 0–10 × 0–10 scoreline matrix with `scipy.stats.poisson`, sum into
Win/Draw/Loss; knockout draws resolve via a penalty split (`0.5 ± 0.05`).
Ratings are **calibrated** (pre-tournament priors blended with group-stage form),
**not** ML-trained — say "calibrated," not "trained." Team ratings live in
`CLAUDE.md` §5.

---

## 5. How to run

**App:**
```
open "/Users/prasiddhakc/Claude/Projects/Fifa Kalshi prediction/index.html"
```
No server. Bankroll/portfolio persist in the browser (`localStorage` keys
`pp_bank`, `pp_pos`). Click the portfolio value to change the bankroll.

**Bot (dry run — places nothing):**
```
cd "/Users/prasiddhakc/Claude/Projects/Fifa Kalshi prediction/"
pip install requests cryptography --break-system-packages
python3 kalshi_bot.py
```
Going live requires your own Kalshi API key, implementing RSA request signing +
order endpoints (TODOs in the file), and flipping `DRY_RUN`. Bot config near the
top: `DRY_RUN`, `BANKROLL`, `KELLY_FRACTION=0.25`, `MIN_EDGE_CENTS=3`.

**Rebuild model output:**
```
pip install scipy numpy --break-system-packages
```
Use the logic in `CLAUDE.md` §6 to regenerate `r32_data.json`, then re-embed the
new array into the `const DATA = [...]` block in `index.html`.
The JSON and the HTML copy must not drift apart.

---

## 6. Non-negotiable rules (keep in every deliverable)

- Predict **probabilities, not certainties** — a 75% pick still loses ~1 in 4.
- An **edge only exists when the model beats the market price.** Betting at the
  market's own price is ~zero EV (worse after fees).
- **No autonomous real-money trades.** Default everything to dry-run; only add
  live-order code on an explicit, separate, confirmed request.
- Not financial advice. Prediction-market legality varies by location.
- App stays a **single self-contained HTML file** (no build step).
- Headlines = **winner + probability**, never a single predicted scoreline.

---

## 7. Next steps (roadmap)

1. **Results tracker + recalibration** after each R32 match (blend ~80% old /
   20% new); log model accuracy + **Brier score**. A tracked record is the real
   resume story.
2. **Extend to Round of 16 / quarters** as the bracket fills.
3. **Dixon–Coles correction** for low-scoring games / draw frequency.
4. **Monte-Carlo tournament sim** → title odds.
5. **Bot, read-only first** — wire Kalshi auth to read live prices and print
   edges in dry run before anything else.
6. **Backtest** on 300–500+ past matches before trusting any edge.

---

## 8. Data sources

Group tables: NBC Sports. R32 bracket/schedule: FOX Sports, Olympics.com, Yahoo.
For genuine fitting later: `martj42/international_results` (GitHub), `eloratings.net`,
FIFA rankings.
