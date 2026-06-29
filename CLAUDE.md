# CLAUDE.md — FIFA 2026 World Cup × Kalshi Prediction Project

> Handoff memory for Claude Code. This file is auto-loaded when you open this
> folder. It captures the goal, the model, the data, every file, how to run
> things, and what to do next. Read it top to bottom before making changes.

---

## 1. What this project is

A football (soccer) match-prediction engine for the **2026 FIFA World Cup**,
presented as a **Kalshi-style prediction-market app**. It estimates each team's
chance of winning / drawing / advancing, turns those into market-style prices
(cents = implied %), and lets the user size bets, see a payout multiplier, an
edge vs the market price, a recommended (Kelly) trade, and a running portfolio.

**Owner's goals (from the project brief):**
- Understand current World Cup standings for all teams.
- Predict upcoming knockout matches and likely outcomes.
- Start with a small bankroll ($10–$100) and grow it **over the tournament**
  (compounding small edges — NOT a single 1000% moonshot).
- Build it toward a **fully automatic prediction-trading bot** on Kalshi.
- Use the project as a **resume/portfolio piece** and, ideally, make some money.

**Reality checks that must stay in every deliverable (non-negotiable, honesty > hype):**
- Predict **probabilities, not certainties**. A 75% pick still loses ~1 in 4.
- An **edge only exists when the model's number beats the market's price.**
  Betting at the market's own price has ~zero expected value (worse after fees).
- We do **not** place real-money trades autonomously for the user, and we never
  promise returns. Prediction-market legality varies by location.
- This is a personal/educational project — **not financial advice.**

---

## 2. Tournament context (as of 2026-06-28)

- First 48-team World Cup. Group stage is **done**; the **Round of 32** (new
  knockout round, 16 matches) is the current stage.
- The model currently covers **all 16 Round-of-32 matches**. The headline / demo
  match is **Brazil vs Japan** (Jun 29, Houston).
- When the R32 results come in, the next job is to **recalibrate and extend the
  model to the Round of 16** (see Roadmap).

---

## 3. The model (PitchPredict Blueprint → Poisson)

Methodology comes from `PitchPredict Blueprint 2.pdf` (in this folder). Core idea:
goals follow a **Poisson distribution**, so if we estimate each team's expected
goals (xG) for a matchup, we get the probability of every scoreline and from
that win/draw/loss and advancement.

**Formula (per team, per match):**

```
expected_goals(team) = BASE × Attack(team) × Defense(opponent) × Location(team)
BASE = 1.35   (avg goals per team per game at a World Cup)
```

- `Attack`  = scoring multiplier vs an average WC team (1.0 = average).
- `Defense` = conceding multiplier; **lower = stronger defense** (e.g. 0.62 = elite).
- `Location`= small boost for hosts / big home-crowd support (USA, Mexico, Canada,
  plus a Brazil crowd boost in US venues). Neutral = 1.0.

Then build the scoreline matrix with `scipy.stats.poisson` (0–10 goals each),
sum into Win / Draw / Loss. **Knockout advancement** resolves draws via a
penalty-shootout split with a small edge to the stronger side
(`pen = 0.5 ± 0.05`).

**Honest framing (blueprint vocabulary):** the ratings are **calibrated** from
pre-tournament strength priors blended with 2026 group-stage form (points / goal
difference). They are NOT machine-"trained" on a large dataset. Call it
*calibrated*, not *trained*, in any copy. Upgrade path: add real historical
results → Dixon–Coles correction → Monte-Carlo tournament sim → xG features →
only then consider ML (XGBoost). Don't skip steps.

---

## 4. Files in this folder

| File | What it is |
|---|---|
| `PitchPredict Blueprint 2.pdf` | The methodology guide. Source of truth for the approach. |
| `WorldCup_R32_Predictor.html` | **Main deliverable.** Self-contained interactive Kalshi-style app: flags grid → match stats/odds → bet ticket (multiplier, edge, ¼-Kelly recommendation) → live portfolio (persists via localStorage) → tournament growth projection. Open in any browser. |
| `Brazil_vs_Japan_Kalshi.html` | Earlier single-match mockup (Brazil vs Japan). Kept for reference. |
| `r32_data.json` | Model output for all 16 R32 matches (xG, W/D/L, advancement, over 2.5, BTTS, top scorelines). The HTML embeds a copy; the bot reads this file. |
| `kalshi_bot.py` | Trading-bot **skeleton**. Reads `r32_data.json`, is built to pull live Kalshi prices, find edges, size ¼-Kelly. `DRY_RUN=True` — prints only, places nothing. Auth + order endpoints are stubbed with TODOs. |
| `CLAUDE.md` | This handoff file. |

> Note: the Python that generated the model (`model.py`, `allmatches.py`) was run
> in a sandbox and may not be in this folder. The canonical model output is
> `r32_data.json`; the generating logic is reproduced in Section 6 so you can
> rebuild it.

---

## 5. Team ratings (current calibration)

`(Attack, Defense)` multipliers; Defense lower = better. Edit these to re-tune.

```
Brazil      (1.55, 0.62)   Japan        (1.20, 0.95)
South Africa(0.82, 1.16)   Canada       (1.08, 0.84)
Germany     (1.45, 0.78)   Paraguay     (0.90, 1.04)
Netherlands (1.45, 0.80)   Morocco      (1.22, 0.82)
France      (1.60, 0.72)   Sweden       (1.00, 1.00)
Ivory Coast (1.05, 0.95)   Norway       (1.30, 0.95)
Mexico      (1.30, 0.80)   Ecuador      (1.00, 0.82)
USA         (1.25, 0.85)   Bosnia       (0.95, 1.05)
Belgium     (1.35, 0.90)   Senegal      (1.12, 0.98)
England     (1.45, 0.80)   DR Congo     (0.95, 1.05)
Colombia    (1.25, 0.85)   Croatia      (1.20, 0.92)
Spain       (1.65, 0.70)   Austria      (1.00, 1.00)
Switzerland (1.10, 0.85)   Algeria      (1.00, 1.00)
Argentina   (1.50, 0.75)   Cape Verde   (0.80, 1.10)
Australia   (0.95, 1.00)   Egypt        (1.05, 0.92)
Portugal    (1.50, 0.80)   Ghana        (1.00, 1.00)
```
Location boosts: Mexico/USA 1.08, Canada 1.07, Brazil 1.05 (US-crowd). Others 1.0.

**Current R32 advancement odds (team A% – team B%):**
SA 29–71 Canada · Brazil 74–27 Japan · Germany 74–26 Paraguay · Netherlands 58–42
Morocco · France 75–25 Sweden · Ivory Coast 42–58 Norway · Mexico 62–38 Ecuador ·
USA 69–31 Bosnia · Belgium 60–40 Senegal · England 73–28 DR Congo · Colombia 55–45
Croatia · Spain 77–23 Austria · Switzerland 59–41 Algeria · Argentina 80–20 Cape
Verde · Australia 43–57 Egypt · Portugal 71–29 Ghana.

---

## 6. How to rebuild / extend the model

```bash
pip install scipy numpy --break-system-packages
```

Reproduce `r32_data.json` with this logic (per match, teams a vs b):

```python
import numpy as np, json
from scipy.stats import poisson
BASE = 1.35
def loc(team): return {"Mexico":1.08,"USA":1.08,"Canada":1.07,"Brazil":1.05}.get(team,1.0)
def match(a, b, T):
    aa,ad = T[a]; ba,bd = T[b]
    la = BASE*aa*bd*loc(a); lb = BASE*ba*ad*loc(b)
    pa = poisson.pmf(np.arange(11), la); pb = poisson.pmf(np.arange(11), lb)
    M = np.outer(pa, pb); M /= M.sum()
    pA = np.tril(M,-1).sum(); pD = np.trace(M); pB = np.triu(M,1).sum()
    pen = 0.5 + 0.05*(1 if la>=lb else -1)
    return dict(xgA=round(la,2), xgB=round(lb,2),
                pA=round(pA*100,1), pD=round(pD*100,1), pB=round(pB*100,1),
                advA=round((pA+pD*pen)*100,1), advB=round((pB+pD*(1-pen))*100,1))
```

To re-tune: adjust `(Attack, Defense)` in Section 5, re-run, regenerate
`r32_data.json`, and paste the new array into the `const DATA = [...]` block near
the top of the `<script>` in `WorldCup_R32_Predictor.html`.

---

## 7. How to run / use

- **App:** double-click `WorldCup_R32_Predictor.html` (or `open` it). No server
  needed. Portfolio + bankroll persist in the browser via `localStorage`
  (keys `pp_bank`, `pp_pos`). Click the portfolio value to change the bankroll.
- **Bot (dry run):** `python3 kalshi_bot.py` — prints recommended trades, places
  nothing. To go live you must add your own Kalshi API key, implement the RSA
  request signing + order endpoints (TODOs in the file), and flip `DRY_RUN`.

---

## 8. Data sources

- Final group tables / standings: NBC Sports "2026 World Cup group stage table".
- R32 bracket & schedule: FOX Sports, Olympics.com, Yahoo Sports.
- Blueprint recommends `martj42/international_results` (GitHub) for historical
  match data, `eloratings.net` and FIFA rankings for strength priors — use these
  when upgrading from calibrated to genuinely fitted ratings.

---

## 9. Roadmap / next steps (good resume material)

1. **Results tracker + recalibration.** After each R32 match, log the actual
   result, update ratings (blend gently: ~80% old / 20% new), and record model
   accuracy + **Brier score**. A documented track record is the credible resume
   story — far better than a bankroll screenshot.
2. **Extend to Round of 16 / quarters** as the bracket fills in.
3. **Dixon–Coles correction** for low-scoring games and draw frequency.
4. **Monte-Carlo tournament sim** → each team's title odds.
5. **Bot, read-only first.** Wire Kalshi auth so the bot can *read* live prices
   and print edges in dry run. Only consider live orders after a tracked,
   profitable paper-trading period — and only where it's legal for the owner.
6. **Backtest** on past tournaments (300–500+ matches) before trusting any edge.

---

## 10. Conventions for Claude Code in this repo

- Keep the **honesty rules in Section 1** in every user-facing string and doc.
- Say **"calibrated,"** not "trained," unless the model is actually fit on data.
- Headlines are **winner + probability**, never a single predicted scoreline.
- The app must stay a **single self-contained HTML file** (no build step, no
  external runtime deps) so the owner can just open it.
- When you change ratings, **regenerate `r32_data.json` and re-embed** it in the
  HTML — the two must not drift apart.
- Never add code that places real trades without an explicit, separate,
  clearly-confirmed request from the owner. Default everything to dry-run.
- Owner is a beginner-friendly audience: explain math in plain language, prefer
  small clear steps over big opaque ones.
