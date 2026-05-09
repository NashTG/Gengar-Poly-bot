# Technology Stack

**Analysis Date:** 2026-05-07

## Languages

**Primary:**
- Python 3.x - Core trading bot, strategy engine, market discovery, order execution

## Runtime

**Environment:**
- Python 3.x (native interpreter)

**Package Manager:**
- pip
- Lockfile: `requirements.txt` present

## Frameworks

**Core:**
- py-clob-client >=0.34.5 - Polymarket CLOB SDK for order placement and market data
- websockets >=12.0 - Real-time BTC price feed from Binance WebSocket stream
- aiohttp >=3.9.0 - Asynchronous HTTP client for WebSocket support
- httpx[socks] >=0.27.0 - HTTP client with SOCKS proxy support (Tor routing)
- pysocks >=1.7.1 - SOCKS5 proxy implementation

**Utilities:**
- python-dotenv >=1.0.0 - Environment variable management from `.env` files

## Key Dependencies

**Critical:**
- py-clob-client (>=0.34.5) - Provides ClobClient, OrderArgs, MarketOrderArgs, BalanceAllowanceParams types for market interaction. Fix in v0.34.6 ensures proper complement engine routing and decimal precision handling.
- websockets (>=12.0) - Enables real-time BTC price feed from Binance (`wss://stream.binance.com:9443/ws/btcusdt@trade`). Falls back to REST polling via urllib if unavailable.

**Infrastructure:**
- aiohttp (>=3.9.0) - Powers async WebSocket connection to Binance
- httpx[socks] (>=0.27.0) - Routes CLOB API requests through SOCKS5 proxy (Tor) to bypass geo-restrictions on POST /order endpoints
- pysocks (>=1.7.1) - SOCKS5 implementation underlying proxy routing

**Standard Library (no imports required):**
- threading - Concurrent price feed and Telegram notification threads
- urllib.request, urllib.parse - HTTP GET/POST for Gamma API market discovery and REST API fallback
- json - JSON parsing for Gamma API responses (clobTokenIds, outcomes fields return as JSON strings)
- csv - Trading and signal log persistence
- dataclasses - TradeSignal, StrategyConfig, MarketWindow, HourlyStats, OrderResult structures
- time - Unix timestamp operations for market window calculations
- math, statistics - Brownian motion probability and statistics

## Configuration

**Environment:**
- `.env` file required for:
  - `PRIVATE_KEY` - Ethereum private key for Polymarket CLOB authentication
  - `SAFE_ADDRESS` - Polymarket Safe proxy contract address (enables signature type 2)
  - Strategy parameters: `MIN_EDGE`, `MIN_PROB`, `SAFETY_FACTOR`, `KELLY_FRACTION`, `MIN_BET`, `MAX_BET`
  - Bankroll: `BANKROLL` (starting capital in USDC)
  - Safety: `DAILY_LOSS_LIMIT`
  - Notifications: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
  - Tor/Proxy: Optional Tor exit node countries configuration

**Build:**
- start.sh - Bash launcher script (`#!/bin/bash`)
- Python entry point: `bot.py` (executable `#!/usr/bin/env python3`)

## Platform Requirements

**Development:**
- Python 3.7+ (dataclasses, async/await, type hints required)
- pip for dependency installation
- `.venv` virtual environment (directory present: `venv/`)
- Tor daemon (optional but required for production trading — blocks datacenter/VPN IPs)

**Production:**
- Polygon blockchain connection (via Polymarket CLOB API `https://clob.polymarket.com`)
- Binance WebSocket connectivity (`wss://stream.binance.com:9443/ws/btcusdt@trade`)
- Polymarket Gamma API connectivity (`https://gamma-api.polymarket.com`)
- Tor daemon running (if trading with VPN/datacenter IP)
- USDC token on Polygon (balance required)
- Polymarket account with CLOB API access

## External Connectivity

**Polymarket CLOB API:**
- Health check: `GET https://clob.polymarket.com/` → `get_ok()`
- Server time: `GET https://clob.polymarket.com/time`
- Order placement: `POST https://clob.polymarket.com/order` (requires authentication, routed via Tor)

**Polymarket Gamma API:**
- Market discovery: `GET https://gamma-api.polymarket.com/events?slug=btc-updown-5m-{ts}`
- Returns market data with token IDs, outcome prices, condition IDs

**Binance WebSocket:**
- Trade stream: `wss://stream.binance.com:9443/ws/btcusdt@trade`
- Fallback REST: `https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT`

**Telegram API:**
- Message endpoint: `https://api.telegram.org/bot{TOKEN}/sendMessage`
- Async notifications via threading (non-blocking)

---

*Stack analysis: 2026-05-07*
