# Architecture

**Analysis Date:** 2026-05-07

## System Overview

PolyBot is a real-time trading bot that exploits oracle lag in Polymarket's 5-minute binary BTC Up/Down markets. The core architecture follows a **pipeline pattern**: event-driven loop → market evaluation → signal generation → order execution → position management → resolution.

```text
┌──────────────────────────────────────────────────────────────────┐
│                     MAIN EVENT LOOP (_tick)                      │
│                      `bot.py:253-326`                            │
│  - Polls BTC price from Binance feed every 100ms                 │
│  - Detects 5-min window boundaries (event trigger)               │
│  - Stateful: tracks trade lifecycle per window                   │
└───────┬──────────────────────────┬──────────────────┬────────────┘
        │                          │                  │
        ▼ (Entry phase)            ▼ (Holding)       ▼ (Exit)
┌──────────────────┐      ┌──────────────────┐  ┌──────────────┐
│  Market Prices   │      │ Position Monitor │  │ Exit Handler │
│  `_get_market..` │      │ `_manage_pos..`  │  │ `_exit_pos`  │
│  `bot.py:637`    │      │ `bot.py:331`     │  │ `bot.py:395` │
└────────┬─────────┘      └────────┬─────────┘  └──────┬───────┘
         │                         │                   │
         ▼                         ▼                   ▼
┌──────────────────────────────────────────────────────────────────┐
│              STRATEGY ENGINE (evaluate → TradeSignal)             │
│                     `strategy.py:249-321`                        │
│  - Brownian motion probability estimation (vol=0.12)             │
│  - Two-filter: min_prob >= 80%, edge >= 5%                       │
│  - Kelly criterion position sizing (quarter-Kelly)               │
└────────┬─────────────────────────────────────────────────────────┘
         │
         ▼ (if signal)
┌──────────────────────────────────────────────────────────────────┐
│         ORDER EXECUTION (buy → verify → track)                   │
│                     `executor.py:138-322`                        │
│  - create_order(OrderArgs) with integer shares, 2-decimal price  │
│  - Balance-verified fill detection (Polygon settlement tracking) │
│  - Ghost fill defense: monitors balance before/after             │
└────────┬──────────────────────┬──────────────────────────────────┘
         │                      │
         ▼ (success)            ▼ (unverified)
    [POSITION]             [PENDING BUY]
    _traded=true       (retry at next window)
                       `bot.py:514-537`
         │
         └──────────────────────────┬────────────────────────────────┐
                                    ▼ (on exit signal)               │
                            ┌──────────────────┐                     │
                            │ Claim Sell (0.99)│                     │
                            │ `executor.py:326`│                     │
                            └────────┬─────────┘                     │
                                     │                              │
                    ┌────────────────┼────────────────┐              │
                    │                │                │              │
            (filled) ▼          (no match)▼      (unconfirmed)▼      │
        [RESOLVED]    [LOSS]       [DEFERRED]                │
      claim_result                phantom_sell              │
                                (next window)               │
                                                      (hold to res.)│
                                                                    │
         ┌──────────────────────────────────────────────────────────┤
         │                                                           │
         └──────────────────────┬──────────────────────────────────┘
                                ▼
                        ┌──────────────────┐
                        │ RECORD RESOLUTION│
                        │ `bot.py:1026`    │
                        │ Update P&L stats │
                        │ Send Telegram    │
                        │ Log to tracker   │
                        └──────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| **PolyBot** | Main event loop, state machines (entry/hold/exit), circuit breakers | `bot.py:74-1164` |
| **Strategy** | Brownian motion probability, Kelly sizing, signal evaluation | `strategy.py:160-321` |
| **Executor** | CLOB order execution, balance-verified fills, ghost fill defense | `executor.py:78-506` |
| **Market** | Polymarket market discovery (Gamma API), token ID lookup | `market.py:54-164` |
| **BinancePriceFeed** | Real-time BTC price via WebSocket + REST fallback | `price_feed.py:45-155` |
| **Tracker** | Three CSV logs: signals, trades, executions | `tracker.py:108-450` |
| **TelegramNotifier** | Mobile alerts (trades/wins/losses), hourly summaries | `telegram_notifier.py:11-118` |
| **Proxy** | Tor routing for geoblocked CLOB API (httpx only, not Gamma) | `proxy.py:191-306` |

## Pattern Overview

**Overall:** Event-driven state machine with layered validation

**Key Characteristics:**
- **Non-blocking**: 100ms tick rate with no blocking I/O in main loop
- **Resilient**: Circuit breaker (CLOB health checks), daily loss limits, balance drift detection
- **Stateful**: Per-window trade state (entry → hold → exit → resolution)
- **Asynchronous verification**: Unverified buys → phantom sell detection at window boundary
- **Real-time pricing**: Dual-source price feed (WebSocket primary, REST backup)

## Layers

**Entry Layer (Market Discovery):**
- Purpose: Identify the active 5-min market and its token IDs
- Location: `market.py:116-164`
- Contains: Gamma API market fetching, outcome parsing
- Depends on: urllib (no auth required, direct Internet)
- Used by: `bot.py:717-722` (token lookup for buy orders)

**Signal Layer (Strategy Evaluation):**
- Purpose: Determine whether BTC move warrants entry
- Location: `strategy.py:249-321` (evaluate) + `strategy.py:190-209` (estimate_true_probability)
- Contains: Brownian motion model, probability gating, edge filtering
- Depends on: math library (error function for normal CDF)
- Used by: `bot.py:284-306` (main entry decision)

**Execution Layer (Order Management):**
- Purpose: Place orders, verify fills, handle Polygon settlement delays
- Location: `executor.py:138-462`
- Contains: create_order/create_market_order wrappers, balance verification, ghost fill detection
- Depends on: py-clob-client (CLOB SDK), httpx (proxied for Tor)
- Used by: `bot.py:680-844` (buy), `bot.py:395-448` (sell)

**Price Layer (Data Feed):**
- Purpose: Supply real-time BTC prices to all other layers
- Location: `price_feed.py:45-155`
- Contains: WebSocket listener (Binance BTCUSDT), REST fallback, thread-safe state
- Depends on: websockets library (async), urllib (fallback)
- Used by: `bot.py:258-260` (every tick), `strategy.py:190` (indirectly via bot context)

**Persistence Layer (Analytics):**
- Purpose: Log all signals, trades, executions for post-session analysis
- Location: `tracker.py:108-450`
- Contains: CSV writers (signals.csv, trades.csv, executions.csv, sessions.csv)
- Depends on: csv, os (filesystem)
- Used by: `bot.py:554-568` (signal logging), `bot.py:779-808` (trade logging), etc.

**Notification Layer (Alerting):**
- Purpose: Send real-time mobile alerts and hourly summaries
- Location: `telegram_notifier.py:11-118`
- Contains: Telegram Bot API calls (threaded, non-blocking)
- Depends on: urllib, threading
- Used by: `bot.py:225-233` (startup), `bot.py:815-819` (trade alert), `bot.py:1079-1113` (hourly summary)

**Network Layer (Geoblocking):**
- Purpose: Route CLOB traffic through Tor (httpx only), leave Gamma direct
- Location: `proxy.py:191-306`
- Contains: Tor process management, SOCKS5 proxy patching, bootstrap detection
- Depends on: subprocess, signal, socket
- Used by: `bot.py:175-182` (startup only, before main loop)

## Data Flow

### Primary Request Path (Entry → Hold → Resolution)

1. **Price arrives from Binance** (`price_feed.py:85`)
   - WebSocket listener updates `state.price` (thread-safe)

2. **Main tick checks for new window** (`bot.py:262-263`)
   - `window_ts = int(now) - (now % period_secs)`
   - If `window_ts != self._current_window` → `_on_new_window()`

3. **Window boundary reset** (`bot.py:452-611`)
   - Resolve phantom sells from previous window (if any)
   - Sync real USDC balance (source of truth)
   - Log no-trade signals from last window
   - Reset all trade state variables

4. **Fetch market and market prices** (`bot.py:281`)
   - `_get_market_prices()` → calls `executor.get_market_price(token_id, "BUY", amount)`
   - CLOB complement engine returns real market prices (~1% spreads)

5. **Strategy evaluation** (`bot.py:284-293`)
   - `evaluate()` → computes BTC delta % → Brownian motion model → Kelly sizing
   - Returns `TradeSignal` if both filters pass (prob >= 80%, edge >= 5%)

6. **Execute trade** (`bot.py:680-844`)
   - Circuit breaker check (CLOB health + daily loss limit)
   - Price preview (`get_market_price()`) + re-check edge
   - Buy via `create_order(OrderArgs)` with integer shares, 2-decimal price
   - Wait 5s for Polygon settlement
   - Verify via balance snapshot or order API (3 rounds, 14s total)
   - If unverified → save pending details → retry at next window

7. **Position held until window close** (`bot.py:331-391`)
   - Monitor hold-period extremes (prob, sell price) every 3 ticks
   - Log hold stats for future optimization
   - No stops, no forced exits

8. **Resolve (claim sell at 0.99)** (`bot.py:848-1076`)
   - Attempt claim sell at $0.99 per share
   - Verify via balance change (source of truth)
   - If balance increased > 50% of expected → filled (won)
   - If "no match" error or balance unchanged → shares worthless (lost)
   - If still unconfirmed → defer to next window (phantom sell tracking)

9. **Record resolution and update stats** (`bot.py:1035-1075`)
   - Update `TradingStats.wins/losses/total_pnl`
   - Send Telegram alert
   - Log to tracker (signals.csv, trades.csv, sessions.csv)

**Circuit Breaking: CLOB Health Check**
- Before every buy: `executor.client.get_ok()` (unauthenticated ping)
- Fail → increment `_consecutive_buy_failures`
- 3 consecutive failures → `_clob_halted = True` → Telegram alert → skip all trades
- Auto-recovery: every new window boundary, retry `get_ok()` → resume if OK

### Secondary Flow: Pending Buy Detection (Unverified → Filled)

1. **Buy unverified** (Polygon settlement too slow) (`bot.py:821-832`)
   - Save order details: `_pending_buy_*` variables
   - Return `UNVERIFIED_BUY` marker
   - Never cancel the order

2. **Next window boundary** (`bot.py:514-537`)
   - Query real USDC balance
   - If balance dropped > $1 since buy attempt → retroactively track as filled
   - Estimate shares from balance drop / attempted price
   - Continue normal hold → exit → resolve flow

3. **Why this works**: 5-minute window is enough for Polygon to settle, so by next tick we know the truth

### Tertiary Flow: Phantom Sell (Filled but Balance Unconfirmed)

1. **Claim sell succeeds per API but balance didn't move yet** (`bot.py:932-957`)
   - Save state: `_pending_phantom` dict
   - Defer resolution to next window

2. **Next window boundary** (`bot.py:452-506`)
   - Query real balance
   - If balance increased > 50% of expected → real fill (record win)
   - If balance unchanged → genuine loss (record loss)
   - Clear `_pending_phantom`

### Secondary Flow: Balance Drift Correction

- **Every window boundary** (`bot.py:570-579`): Query real balance, overwrite internal tracking
- **Every hour** (`bot.py:1079-1113`): Re-sync real balance
- **On shutdown** (`bot.py:1115-1159`): Final balance sync

**Why**: Accumulated errors from partial fills, rounding, API delays → corrected at window boundary

## Key Abstractions

**TradeSignal:**
- Purpose: Encapsulate a market opportunity
- Examples: `strategy.py:16-24`
- Pattern: Immutable dataclass with all decision factors (side, prob, edge, kelly_size)

**StrategyConfig:**
- Purpose: Runtime strategy parameters (thresholds, Kelly fraction, entry window)
- Examples: `strategy.py:28-38`
- Pattern: Dataclass binding, read-only after init

**OrderResult:**
- Purpose: Unified return type for buy/sell operations
- Examples: `executor.py:41-53`
- Pattern: Contains success flag, status enum (FILLED/PARTIAL/REJECTED/FAILED), error message

**MarketWindow:**
- Purpose: Active 5-min market metadata
- Examples: `market.py:18-32`
- Pattern: Includes token IDs, time bounds, outcome prices

**TradingStats + HourlyStats:**
- Purpose: Hierarchical stat tracking (session-level + hourly rolling)
- Examples: `strategy.py:122-157`
- Pattern: Record methods (record_win/record_loss) auto-update nested hourly

**PriceState:**
- Purpose: Thread-safe price container with freshness tracking
- Examples: `price_feed.py:19-42`
- Pattern: Mutex-protected reads/writes, timestamp aging

## Entry Points

**Main Entry:**
- Location: `bot.py:1162-1164`
- Triggers: `python bot.py`
- Responsibilities: Parse `.env`, instantiate PolyBot, call `start()`

**Startup Sequence:**
- `bot.py:174-241` (PolyBot.start)
  1. Load env vars
  2. Tor proxy (if live mode)
  3. Print config
  4. Initialize executor (wallet connection)
  5. Query initial balance
  6. Start price feed (blocking wait for first price)
  7. Startup Telegram alert
  8. Enter main loop

**Main Loop:**
- `bot.py:243-251` (_main_loop)
  - Infinite `_tick()` at 100ms intervals
  - Exception handler logs to terminal + Telegram

**Tick Function:**
- `bot.py:253-326` (_tick)
  - Fetches fresh price
  - Detects window boundary (event trigger)
  - Routes to entry/hold/exit logic based on state

## Architectural Constraints

- **Event-driven without async/await**: Single-threaded main loop, price updates via background thread. No coroutine overhead.
- **Module-level singletons**: `executor`, `price_feed`, `telegram`, `tracker` created once in `__init__`, reused across all ticks. Thread-safe where needed (price_feed via lock).
- **No circular imports**: Dependency graph is acyclic: bot → strategy, executor, market, price_feed, tracker, telegram. All are imported at module level.
- **Polygon settlement latency**: UNVERIFIED_BUY and phantom sells designed to tolerate 5-15s delays — validated at next window boundary.
- **Float precision**: All prices rounded to 2 decimals, all shares cast to int before order creation. Avoids the IEEE 754 bug that broke `create_market_order`.
- **No cancellation on timeout**: Unverified buys are never cancelled. Bot detects fills via balance sync. This is intentional — the order is likely filled despite API exception.
- **Minimum notional enforcement**: Checks `shares × price >= $5.00` before selling. Polymarket rejects below-minimum orders; enforcing client-side prevents stranded shares.

## Anti-Patterns

### Float Precision Errors in Order Sizing

**What happens:** Using `create_market_order(MarketOrderArgs(amount=X))` internally divides `X / price`, producing shares with >4 decimals (e.g., 21.000000000004). CLOB rejects: "invalid amounts, max accuracy 4 decimals".

**Why it's wrong:** IEEE 754 artifact. The library's internal math breaks the 4-decimal constraint that Polymarket enforces.

**Do this instead:** Use `create_order(OrderArgs(price=round(price, 2), size=float(int(shares))))` with explicit integer shares and 2-decimal prices. Library never divides. Example: `executor.py:222-229`.

### Cancelling Orders on Verification Timeout

**What happens:** If buy verification fails in 14 seconds, cancel the order. Order may still be settling on-chain, so cancellation fails silently while shares are bought undetected.

**Why it's wrong:** Polygon settlement takes 5-15s. Cancelling early doesn't actually cancel on-chain. The next balance check catches the fill anyway.

**Do this instead:** Never cancel. Return `UNVERIFIED_BUY` marker, save order details, and detect settlement at next window boundary via balance sync. Example: `executor.py:315-322`.

### Attempting Claim Sell Without Notional Check

**What happens:** Try to sell shares below $5 notional. CLOB rejects, shares remain in position, bot loops on retry, never holds to resolution.

**Why it's wrong:** Polymarket's minimum order size is $5. Below that, the API error doesn't explain the constraint, shares appear "stuck".

**Do this instead:** Check `shares × price >= $5.00` before any sell attempt. If below minimum, skip sell and hold to resolution instead. Example: `executor.py:364-375`.

### Using Unverified Balance for Kelly Sizing

**What happens:** After a partial fill or ghost fill, internal `bankroll` tracking diverges from real USDC balance. Kelly sizing uses stale `bankroll`, producing oversized bets.

**Why it's wrong:** Accumulated drift → position sizing error → larger-than-intended bets → blow-through daily loss limit.

**Do this instead:** Sync real balance at window boundary (source of truth), overwrite internal tracking. `bot.py:570-579` runs every window. Also sync hourly and on shutdown.

## Error Handling

**Strategy:** Multi-layered with graceful degradation.

**Patterns:**

1. **API call failures** → log and return sentinel value (0.0 for prices, None for market)
   - Example: `market.py:64-66` (market fetch fails → None → skip entry)

2. **CLOB failures** → circuit breaker (3 consecutive failures → halt trading)
   - Example: `bot.py:688-700` (health check failures increment counter, halt at threshold)

3. **Balance verification failures** → assume no fill, don't update bankroll
   - Example: `executor.py:282-292` (spent <= $0.50 → not filled, return FAILED)

4. **Unverified fills** → save state, retry detection at next window
   - Example: `bot.py:821-832` (save pending_buy_*, return UNVERIFIED_BUY marker)

5. **Partial fills** → track residual shares, hold remaining to resolution
   - Example: `executor.py:405-415` (status=PARTIAL, return shares_remaining)

6. **Phantom sells** → defer outcome to next window balance sync
   - Example: `bot.py:1006-1020` (save _pending_phantom dict)

## Cross-Cutting Concerns

**Logging:** 
- Terminal: print statements with emoji/status indicators
- CSV: 3 tracker logs (signals, trades, executions)
- Telegram: trade alerts, wins/losses, hourly summaries, CLOB halts

**Validation:**
- Price: must be > 0 and fresh (< 5 seconds old)
- Market: Gamma API response parsed, tokens extracted, outcomes matched
- Trade: notional >= $5, bankroll sufficient, edge present

**Authentication:**
- CLOB: Private key + Safe address (signature type 2 for proxy wallets)
- Telegram: Bot token + chat ID (disabled if missing)
- Tor: SOCKS5 on localhost:9050 (auto-started, auto-restarted if exit node blocked)

---

*Architecture analysis: 2026-05-07*
