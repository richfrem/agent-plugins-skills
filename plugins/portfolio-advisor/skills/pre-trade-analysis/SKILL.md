---
name: pre-trade-analysis
plugin: portfolio-advisor
description: >
  Conducts comprehensive pre-trade analysis before initiating, accumulating, trimming,
  or exiting a stock. Synthesizes multi-quarter earnings transcripts, guidance direction,
  contracted backlogs, live TradingView chart structure (200/50/21 EMAs, support floors,
  trim shelves, stop losses), and concrete tranche sizing with PSU-U.TO capital sourcing.
argument-hint: "{TICKER} [ACTION: initiate|accumulate|trim|exit]"
allowed-tools: Bash, Read, Write
---

# Pre-Trade Analysis Skill (`/pre-trade-analysis`)

**Triggers**:
- `/pre-trade-analysis {TICKER}`
- "run pre-trade analysis on {TICKER}"
- "prep trade {TICKER}"
- "analyze entry and exit levels for {TICKER}"

---

## Purpose
Bridges the gap between fundamental valuation and technical execution. Before any capital is deployed (or exited), this skill executes an unskippable **5-Point Pre-Trade Checklist** ensuring the investor does not buy into a broken transcript or chase an extended chart.

---

## The 5-Point Pre-Trade Checklist (Mandatory Output)

Whenever this skill executes, the agent **MUST** output this structured markdown briefing:

```markdown
### 🎯 Pre-Trade Analysis Briefing: {TICKER} ({LIFECYCLE_ACTION})

- [x] **1. Transcript & Multi-Model Strategic Audit**:
  - *Calls & Filings Audited*: [e.g. Q1 2026, Q2 2026 10-Qs, earnings transcripts]
  - *Triangulated Model Sweep*: [Grok (real-time news/catalysts) + ChatGPT/Claude (10-Q/GAAP/debt audit)]
  - *Guidance Trajectory*: [RAISED / MAINTAINED / LOWERED / WITHDRAWN]
  - *Backlog Quality & RPO*: [Firm contracted RPO vs non-binding LOI vs customer-funded infrastructure]
  - *Adversarial Counterparty & Balance Sheet Check*: [Debt/interest burn, dilution, customer concentration]

- [x] **2. Technical Regime & TradingView Chart Structure**:
  - *Trend vs 200 EMA*: [Trading above/below institutional 200 EMA ($Price)]
  - *Dynamic Pivots*: [21 EMA ($Price), 50 EMA ($Price)]
  - *Momentum & Gas Tank*: [RSI, ADX trend strength, Squeeze status]

- [x] **3. Key Execution Shelves & Levels**:
  - *Tactical Watchlist Alert*: $[Price] (Early notice trigger)
  - *Buy Tier 1 (Starter Tranche)*: $[Price] (Tactical retracement support)
  - *Primary Buy Floor*: $[Price] (Institutional accumulation shelf)
  - *Trim Target 1 / 2*: $[Price] / $[Price] (Resistance shelves)
  - *Stop Loss / Thesis Breaker*: $[Price] (Structural invalidation floor)

- [x] **4. Concrete Tranche Sizing & Capital Sourcing**:
  - *Target Portfolio Weight*: X.X% (~$[Total USD])
  - *Tranche 1 (Immediate / Limit)*: [N shares @ $Price (~$USD)]
  - *Tranche 2 (Secondary Dip / GTC)*: [N shares @ $Price (~$USD)]
  - *Capital Sourcing (Rule #4)*:
    - TFSA: Sell [N] shares PSU-U.TO
    - RRSP: Sell [N] shares PSU-U.TO

- [x] **5. System & Alert Synchronization**:
  - [Synchronized price levels into domain_model.sqlite]
  - [Active TradingView alert verified or scripted]
```

---

## Step-by-Step Execution Protocol

### Step 1: Query Current State & Existing Levels
1. Check existing position and standing decision in `domain_model.sqlite`:
   ```bash
   python3 investment_screener/backend/py_services/portfolio_io.py --ticker {TICKER}
   ```
2. Pull recorded price levels and alerts:
   ```bash
   python3 -c "
   import sqlite3
   conn = sqlite3.connect('investment_screener/backend/data/domain_model.sqlite')
   rows = conn.execute('''
       SELECT plt.tier_kind, plt.tier_number, plt.price, plt.basis
       FROM price_level_tier plt
       JOIN price_level_set pls ON pls.price_level_set_id = plt.price_level_set_id
       WHERE pls.investment_id = '{TICKER}'
   ''').fetchall()
   print('Current levels:', rows)
   conn.close()
   "
   ```

### Step 2: Multi-Quarter Transcript & Triangulated Multi-Model Audit
1. Run the targeted adversarial prompt across **both Grok and ChatGPT/Claude**:
   - **Grok**: Surfaces breaking real-time news, X executive commentary, and sentiment inflections.
   - **ChatGPT / Claude**: Forensically checks 10-Q SEC filings, reconciles GAAP vs non-GAAP (e.g. M&A inflation like PANW), extracts all-in costs (e.g. RIOT mining depreciation), and quantifies debt/FCF burdens (e.g. CRWV debt vs backlog).
2. Determine guidance trajectory (RAISED, MAINTAINED, LOWERED).
3. Distinguish firm contracted RPO (e.g. SYM's $22.5B) from non-binding LOIs or speculative TAM claims.
4. Assess customer concentration (e.g. SYM's 90.5% Walmart dependency).

### Step 3: Technical Structure & Chart Inspection
1. Fetch live technicals from `ta_sweep_single.py` or TradingView CDP:
   ```bash
   python3 investment_screener/backend/py_services/fetch_financials.py {TICKER}
   ```
2. Identify:
   - **White Line (200 EMA)**: Institutional baseline.
   - **Green Shelves**: Buy Tier 1 (21/50 EMA pivot) and Primary Buy.
   - **Yellow/Orange Shelves**: Trim 1 and Trim 2.
   - **Red Dash**: Structural Stop Loss.

### Step 4: Sizing & Capital Sourcing Calculations
Per Toolkit Capital Policy:
- All cash is held in **PSU-U.TO** (~$100 USD/share).
- Shares to sell ≈ `ceil(N × price / 100)`.
- Split: TFSA (~75%) / RRSP (~25% / ~1/3 share count).

### Step 5: Persistence & TradingView Sync
1. Store confirmed levels in `domain_model.sqlite`:
   - `price_level_tier` (`TARGET_ENTRY`, `BUY_TIER`, `SELL_TIER`, `STOP_LOSS`)
   - `alert` table
   - `standing_decision_reason`
2. If TradingView Desktop is running, trigger thesis overlay:
   ```bash
   python3 plugins/tradingview/scripts/tv_thesis_overlay.py --ticker {TICKER}
   ```
