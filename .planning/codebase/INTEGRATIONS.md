# External Integrations

**Analysis Date:** 2026-05-07

## APIs & External Services

**Polymarket CLOB (Order Execution):**
- CLOB API - Primary order execution endpoint for Polymarket binary markets
  - SDK/Client: `py-clob-client` (v0.34.5+)
  - Endpoint: `https://clob.polymarket.com`
  - Auth: Ethereum signature (PRIVATE_KEY in `.env`) with Safe/proxy signature type 2
  - Routing: All POST /order requests route through SOCKS5 Tor proxy to bypass geo-blocking
  - Key methods: `create_order(OrderArgs)` for buys, `create_market_order(MarketOrderArgs)` for sells
  - Health check: `client.get_ok()` (unauthenticated GET /) before every trade; 3 consecutive failures trigger circuit breaker

**Polymarket Gamma API (Market Discovery):**
- Gamma API - Market metadata and token discovery
  - Endpoint: `https://gamma-api.polymarket.com`
  - Key endpoint: `GET /events?slug=btc-updown-5m-{window_ts}`
  - Returns: Market data including `clobTokenIds` (JSON string, requires `json.loads()`), `outcomes` (JSON string), `conditionId`, `outcomePrices`
  - Used by: `market.py::fetch_market_by_slug()` and `extract_token_ids()`
  - Client: Native `urllib.request` (no SDK)

**Binance WebSocket (BTC Price Feed):**
- Binance Trade Stream - Real-time BTC/USDT price updates
  - Endpoint: `wss://stream.binance.com:9443/ws/btcusdt@trade`
  - Used by: `price_feed.py::BinancePriceFeed`
  - Library: `websockets` (v12.0+) with `asyncio`
  - Fallback: REST API polling via `https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT` (every 2s if WebSocket stale)
  - Data flow: Price updates trigger `self._on_price()` callback in bot.py for strategy evaluation

## Data Storage

**Databases:**
- None — Polymarket blockchain serves as order/execution ledger

**File Storage:**
- Local filesystem only
- CSV logs: `logs/signals.csv`, `logs/trades.csv`, `logs/executions.csv` (append-only tracking)
- Configuration: `.env` file (secrets stored locally, not committed)

**Caching:**
- None — Real-time price and market data fetched on-demand

## Authentication & Identity

**Auth Provider:**
- Custom Ethereum signature-based auth (no external identity provider)
- Implementation:
  - Private key: `PRIVATE_KEY` env var (raw hex string)
  - Safe address: `SAFE_ADDRESS` env var (Polymarket Safe/proxy contract)
  - Signature type: 2 (Safe/proxy compatible)
  - SDK: `py-clob-client` ClobClient handles signature generation and order signing
  - Per-trade auth: Every order includes signed timestamp and nonce to prevent replay attacks

## Monitoring & Observability

**Error Tracking:**
- None (no external service)

**Logs:**
- Local CSV files:
  - `logs/signals.csv` — Every signal evaluated (entry/skip decision)
  - `logs/trades.csv` — Full lifecycle: entry price, exit, resolution, P&L
  - `logs/executions.csv` — API call timing and success/failure
- Files created by: `tracker.py::Tracker` class
- Location configurable: `LOG_DIR` env var (default: `logs/`)

**Telegram Notifications:**
- Used for: Real-time trade alerts, hourly summaries, error alerts, startup confirmation
- Implementation: `telegram_notifier.py::TelegramNotifier`
- Endpoint: `https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage`
- Auth: Bot token in `TELEGRAM_BOT_TOKEN` env var, chat ID in `TELEGRAM_CHAT_ID`
- Delivery: Async via threading (non-blocking, fire-and-forget)
- Message types:
  - `trade_alert()` — Entry signal with price, amount, Kelly size, edge
  - `win_alert()` / `loss_alert()` — Immediate P&L feedback
  - `hourly_summary()` — Trades in last hour, win rate, P&L, bankroll
  - `status_update()` — Silent periodic reports
  - `error_alert()` — Exceptions and circuit breaker triggers
  - `startup_alert()` — Config summary on bot launch

## CI/CD & Deployment

**Hosting:**
- Local development machine (no cloud deployment)
- Optional: VPS with systemd/pm2 for persistent uptime (not yet implemented)

**CI Pipeline:**
- None — Manual testing only (dry run mode available)
- Validation:
  1. Python syntax check: `python -c "import ast; ast.parse(open('file.py').read())"`
  2. Dry run: `DRY_RUN=true python bot.py` (simulates trades without executing)
  3. Live testing: Low bankroll + CSV analysis against Polymarket transaction history

## Environment Configuration

**Required env vars:**
- `PRIVATE_KEY` — Hex-encoded Ethereum private key (secret)
- `SAFE_ADDRESS` — Polymarket Safe proxy contract address
- `DRY_RUN` — "true" for simulation, "false" for live trading
- `BANKROLL` — Starting USDC balance (e.g., 100.0)
- `DAILY_LOSS_LIMIT` — Max daily loss before circuit breaker (e.g., 30.0)
- `MIN_PROB`, `MIN_EDGE`, `SAFETY_FACTOR` — Strategy thresholds
- `KELLY_FRACTION`, `MIN_BET`, `MAX_BET` — Position sizing bounds
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` — Telegram notifications (optional)
- `MARKET_PERIOD` — Market duration in minutes (default: 5)
- `LOG_DIR` — Path to CSV logs (default: logs/)

**Optional env vars:**
- `ROLLING_VOL_WINDOWS` — Windows for vol estimation (default: 12)
- `VOL_FLOOR`, `VOL_CAP` — Volatility bounds (default: 0.06, 0.30)
- Tor exit countries (auto-generated if needed)

**Secrets location:**
- `.env` file (local, not committed; see `.gitignore`)
- Never committed to git
- Never logged or transmitted

## Webhooks & Callbacks

**Incoming:**
- None — Bot is pull-based (queries market/price data on schedule)

**Outgoing:**
- Telegram webhook-style: Bot sends messages to Telegram API (push notifications)
- No Polymarket webhooks; bot uses polling for market data and price feed

## Tor Proxy Configuration

**Purpose:**
- Bypass Polymarket CLOB geo-restrictions on POST /order endpoint (datacenter/VPN blocks)

**Implementation:**
- `proxy.py` — Dynamically generates `torrc` config and manages Tor daemon
- SOCKS5 listening on: `localhost:9050` (default TOR_SOCKS_PORT)
- Configuration:
  - Exit node countries: Polymarket-friendly list (CH, SE, RO, CZ, AT, ES, DK, FI, NO, PT, BR, JP, KR, IN)
  - StrictNodes: 1 (enforces country pinning)
  - Data directory: `.tor/data/`
  - PID file: `.tor/tor.pid`
- Integration:
  - `httpx[socks]` client routes all requests through SOCKS5 proxy
  - Auto-restart if exit node gets blocked (restart Tor daemon for new circuit)
  - Applied once at startup via `apply_proxy()` before any HTTP calls

## Data Flows

**Market Entry Signal:**
1. Price feed: Binance WS → `BinancePriceFeed.state` (real-time)
2. Market data: Gamma API poll → `get_current_market()` returns `MarketWindow`
3. Strategy: `strategy.evaluate()` compares BTC delta vs Polymarket prices
4. Output: `TradeSignal` (side, confidence, edge, kelly_size)
5. Execution: If signal passes gates, `executor.buy()` creates limit order via CLOB API (routed via Tor)
6. Tracking: `tracker.log_signal()`, `tracker.log_trade_entry()` write to CSV

**Position Resolution:**
1. Hold: All positions held until market window closes (no stops)
2. Balance sync: Window-boundary refresh queries real USDC balance (source of truth)
3. Resolution: Query Binance final BTC price; claim shares on CLOB if won
4. P&L: `profit = (claim_value or sell_price * shares) - entry_cost`
5. Logging: `tracker.log_trade_resolve()`, session P&L update

**Safety Circuit Breakers:**
1. CLOB health check: `get_ok()` before every trade; 3 fails → `_clob_halted = True` + Telegram alert
2. Daily loss limit: `session_pnl <= -DAILY_LOSS_LIMIT` → halt trading + Telegram alert
3. Balance-verified buys: Snapshot USDC before/after; ghost fills caught even if API exception
4. Pending buy safety: Unverified buys detected at next window boundary via balance drop
5. Minimum notional guard: Skip sells below $5 notional (avoids Polymarket rejection error)

---

*Integration audit: 2026-05-07*
