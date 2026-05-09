# Codebase Structure

**Analysis Date:** 2026-05-07

## Directory Layout

```
gengar_polymarket_bot/
├── bot.py              # Main event loop, state machines, circuit breakers (1165 lines)
├── executor.py         # CLOB order execution, fill verification (506 lines)
├── strategy.py         # Brownian motion, Kelly sizing, signal evaluation (322 lines)
├── market.py           # Polymarket market discovery (Gamma API) (181 lines)
├── price_feed.py       # Binance WebSocket + REST fallback (155 lines)
├── tracker.py          # Analytics: signals.csv, trades.csv, executions.csv (450 lines)
├── telegram_notifier.py # Mobile alerts + hourly summaries (118 lines)
├── proxy.py            # Tor proxy for geoblocked CLOB API (306 lines)
├── .env                # Configuration (PRIVATE_KEY, API tokens, thresholds)
├── .env.example        # Template with dummy values
├── logs/               # Generated: signals.csv, trades.csv, executions.csv, sessions.csv
├── archive/            # Legacy/debug scripts (not used in runtime)
│   ├── debug_book.py   # Old order book inspection
│   └── debug_geo.py    # Old geo/proxy testing
└── .planning/codebase/ # This documentation
    ├── ARCHITECTURE.md
    └── STRUCTURE.md
```

## Directory Purposes

**Root Level (Core Runtime):**
- **bot.py**: Entry point, main event loop, state machine lifecycle
- **executor.py**: Trading operations (buy/sell), balance verification
- **strategy.py**: Signal generation, probability estimation, position sizing
- **market.py**: Market metadata (token IDs, window time bounds)
- **price_feed.py**: Real-time BTC price source (Binance)
- **tracker.py**: Performance analytics (CSV logs)
- **telegram_notifier.py**: Push notifications (Telegram Bot API)
- **proxy.py**: Tor integration for geoblocked CLOB API

**Configuration:**
- **.env**: Private key, Safe address, API tokens, strategy parameters
- **.env.example**: Template (safe to commit)

**Logs Directory:**
- **signals.csv**: Every evaluate() call (traded or skipped) — used to debug entry filters
- **trades.csv**: Complete trade lifecycle (entry → hold → exit → resolve) — used for P&L analysis
- **executions.csv**: Every API call with latency — used for performance tuning
- **sessions.csv**: End-of-session summary

**Archive:**
- **debug_book.py**, **debug_geo.py**: Legacy utilities, not loaded by bot

## Key File Locations

**Entry Points:**
- `bot.py:1162-1164`: Main executable, instantiates PolyBot and calls start()
- `bot.py:174-241`: Startup sequence (env load, executor init, price feed start, main loop)
- `bot.py:243-326`: Main event loop (_tick) — 100ms resolution, price polling, window detection

**Configuration:**
- `bot.py:76-109`: PolyBot.__init__() — reads all .env vars and initializes subcomponents
- `strategy.py:28-38`: StrategyConfig dataclass — holds all thresholds (min_prob, min_edge, etc.)
- `.env`: Runtime overrides for all parameters

**Core Logic:**
- `bot.py:680-844`: Entry logic (_execute_trade) — price preview, edge re-check, order placement
- `bot.py:331-391`: Hold logic (_manage_position) — monitoring only, no exits
- `bot.py:848-1076`: Resolution logic (_resolve_previous_trade) — claim sell, balance verification
- `strategy.py:249-321`: Signal evaluation (evaluate) — probability gate, edge filter, Kelly sizing
- `executor.py:138-266`: Buy execution with verification — integer shares, balance snapshot, ghost fill defense
- `executor.py:326-462`: Sell execution — notional check, balance verification

**Market Discovery:**
- `market.py:116-164`: get_current_market() — fetches Gamma API, parses token IDs
- `market.py:69-113`: extract_token_ids() — maps outcomes to token IDs (JSON parsing)

**Price Feed:**
- `price_feed.py:45-155`: BinancePriceFeed class — WebSocket + REST polling
- `price_feed.py:68-116`: _ws_loop() and _rest_poll_loop() — background threads

**Analytics:**
- `tracker.py:147-207`: log_signal() — every evaluate() result
- `tracker.py:211-249`: log_trade_entry() — on buy fill
- `tracker.py:264-332`: log_trade_exit() + log_trade_resolve() — on sell + resolution
- `tracker.py:410-442`: log_session() — on shutdown

**Notifications:**
- `telegram_notifier.py:42-51`: trade_alert() — per trade
- `telegram_notifier.py:53-57`: win_alert() / loss_alert()
- `telegram_notifier.py:59-92`: hourly_summary() — comprehensive hourly report

**Geo-Blocking:**
- `proxy.py:191-235`: ensure_tor() — start/reload Tor, wait for bootstrap
- `proxy.py:238-288`: apply_proxy() — monkey-patch httpx.Client to route through SOCKS5

## Naming Conventions

**Files:**
- `*.py`: Python source files (no package structure, flat hierarchy)
- `.env`: Dotenv configuration (never committed with real values)
- `.csv`: Analytics logs (append-only, created on first write)

**Classes:**
- `PolyBot`: Main bot class (lowercase for instances, PascalCase for class)
- `Executor`: CLOB order handler
- `BinancePriceFeed`: Price data source
- `TelegramNotifier`: Notification service
- `Tracker`: Analytics logger
- `StrategyConfig`, `TradeSignal`: Config/data dataclasses

**Functions:**
- `_private_method()`: Underscore prefix for internal methods (e.g., `_tick`, `_on_new_window`)
- `public_function()`: Module-level functions with no prefix (e.g., `evaluate()`, `estimate_true_probability()`)
- `get_X()`, `set_X()`: Accessor patterns (e.g., `get_balance()`, `get_market_price()`)
- `_check_X()`, `_verify_X()`: Validation patterns (e.g., `_check_order()`, `_verify_buy_via_balance()`)

**Variables:**
- `snake_case`: All variables (e.g., `btc_delta_pct`, `market_price`, `kelly_fraction`)
- `_private_var`: Underscore prefix for instance variables (e.g., `_traded`, `_current_window`)
- `CONSTANT`: All-caps for module-level constants (e.g., `FILLED`, `PARTIAL`, `POLY_MIN_NOTIONAL`)

**Constants:**
- `FILLED`, `PARTIAL`, `REJECTED`, `FAILED`: Order status enums (executor.py:30-33)
- `MIN_SHARES=1.0`, `MIN_AMOUNT_USD=1.0`: Order size minimums (executor.py:35-36)
- `MAX_BUY_PRICE=0.90`: Don't buy above this — profit cap (executor.py:37)
- `POLY_MIN_NOTIONAL=5.0`: Polymarket minimum order size (executor.py:38)
- `PERIOD_SECONDS={5: 300, 15: 900}`: Window length mapping (market.py:15)

## Where to Add New Code

**New Trading Strategy (Replace evaluate()):**
- Primary: `strategy.py:249-321` (evaluate function)
- Config: `strategy.py:28-38` (StrategyConfig — add new thresholds)
- Model: `strategy.py:190-209` (estimate_true_probability — change vol or add new signals)
- Integration: `bot.py:284-293` (call site)

**New Order Type or Execution Logic:**
- Buy: `executor.py:138-266` (buy method)
- Sell: `executor.py:326-462` (sell method)
- Verification: `executor.py:267-322` (_verify_buy_via_balance — add new checks)
- Helper: `executor.py:465-497` (utilities: _extract_fill, _check_order)

**New State Machine or Entry/Exit Logic:**
- Entry: `bot.py:680-844` (_execute_trade)
- Hold: `bot.py:331-391` (_manage_position)
- Exit: `bot.py:395-448` (_exit_position)
- Resolution: `bot.py:848-1076` (_resolve_previous_trade)
- Window boundary: `bot.py:452-611` (_on_new_window)

**New Market Discovery Logic:**
- Gamma API: `market.py:54-66` (fetch_market_by_slug)
- Token extraction: `market.py:69-113` (extract_token_ids)
- Market building: `market.py:116-164` (get_current_market)

**New Price Source:**
- Add to `price_feed.py`: New thread method (e.g., `_kraken_loop()`)
- Update `BinancePriceFeed.start()` to launch new thread
- Update `state` to track source ("kraken", "binance", etc.)

**New Analytics or Metrics:**
- Add fields to `SIGNAL_FIELDS` or `TRADE_FIELDS` in `tracker.py:33-83`
- Add logging call in `bot.py` (e.g., `tracker.log_signal()`)
- New CSV will auto-create with headers

**New Notification Type:**
- Add method to `TelegramNotifier` (e.g., `debug_alert()`)
- Call from `bot.py` as needed

**New Safety System or Circuit Breaker:**
- Add state variable to `PolyBot.__init__()` (e.g., `_volatility_halted`)
- Add check in `bot.py:683-715` (before entry)
- Add recovery logic in `bot.py:612-620` (window boundary)

## Special Directories

**`.env` File:**
- Purpose: Runtime configuration (secrets + parameters)
- Contents: Private key, Safe address, Telegram tokens, strategy thresholds
- Generated: No, must be created manually from `.env.example`
- Committed: No (in .gitignore)
- Loaded: `bot.py:76` (load_dotenv())

**`logs/` Directory:**
- Purpose: Append-only CSV logs for post-session analysis
- Contents: signals.csv, trades.csv, executions.csv, sessions.csv
- Generated: Yes, on first write by Tracker
- Committed: No (gitignored, session-specific)
- Location: Configurable via `LOG_DIR` env var (default "logs")

**`archive/` Directory:**
- Purpose: Legacy debugging scripts (not part of runtime)
- Contents: debug_book.py, debug_geo.py
- Generated: No, manually added during development
- Committed: Yes (safe to keep, not imported)

## Development Notes

### Adding a New Configuration Parameter

1. Add to `.env.example`:
```env
NEW_PARAM=default_value
```

2. Add to `bot.py:76-109`:
```python
self.new_param = float(os.getenv("NEW_PARAM", "default_value"))
```

3. Use in your code:
```python
if btc_price > self.new_param:
    ...
```

### Adding a New CSV Log Column

1. Add to `SIGNAL_FIELDS`, `TRADE_FIELDS`, or `EXECUTION_FIELDS` in `tracker.py:33-95`:
```python
SIGNAL_FIELDS = [
    ...,
    "new_column_name",
]
```

2. Update the log call in `bot.py` (e.g., `tracker.log_signal()`):
```python
tracker.log_signal(
    ...,
    new_column_name=value,
)
```

3. CSV will auto-create with the new column on next session.

### Disabling a Safety System

Each safety system has a guard:

- **CLOB circuit breaker**: Check `if self._clob_halted` at `bot.py:684-686`
- **Daily loss limit**: Check `if self._daily_loss_halted` at `bot.py:703-706`
- **Balance verification**: Set `timeout=0` in `executor.py:241` to skip waits (not recommended)
- **Minimum notional**: Remove check at `executor.py:364-375`

Don't disable without understanding the consequence.

### Running in Dry Run Mode

Set `.env`:
```env
DRY_RUN=true
PRIVATE_KEY=  (can be empty)
SAFE_ADDRESS= (can be empty)
```

- No wallet connection (`executor.initialize()` skipped)
- Simulated prices via tape/math at `executor.py:155-162` (buy) and `executor.py:340-349` (sell)
- No Tor proxy (skipped at `bot.py:175`)
- All trade/exit logic runs normally, just no real orders

### Debugging Entry Failures

Check `logs/signals.csv`:
- Count each `skip_reason` value (delta_too_small, prob_below_min, edge_below_min, price_out_of_range)
- Focus on the most common skip reason

Example analysis:
```python
df = pd.read_csv("logs/signals.csv")
df[df['action']=='no_signal']['skip_reason'].value_counts()
```

---

*Structure analysis: 2026-05-07*
