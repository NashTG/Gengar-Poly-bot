# Testing Patterns

**Analysis Date:** 2026-05-07

## Test Framework

**Status:** No automated test framework configured

- No pytest, unittest, or other test runner installed
- No test files in repository (search for `*.test.py`, `*_test.py`, `test_*.py` returned no results)
- `requirements.txt` contains only production dependencies (see `requirements.txt`)

**Current testing approach:**
1. Syntax validation via `python -c "import ast; ast.parse(open('file.py').read())"` (mentioned in CLAUDE.md)
2. Dry-run mode testing: `DRY_RUN=true` in `.env` runs bot without live trades
3. Manual live testing: small bankroll + terminal log review
4. Post-session validation: compare tracker CSV output against Polymarket transaction history

## Test File Organization

**Location:**
- No test directory exists
- No test files present

**If tests were added, proposed structure:**
```
tests/
├── test_strategy.py         # Unit tests for Brownian motion model, Kelly sizing
├── test_executor.py         # Order placement logic, balance verification
├── test_market.py           # Market slug generation, token ID extraction
├── test_price_feed.py       # Price state updates, freshness checking
├── fixtures/
│   ├── market_responses.py  # Mock Gamma API responses
│   ├── price_ticks.py       # Mock Binance price data
│   └── wallet_states.py     # Test balance scenarios
└── conftest.py              # pytest configuration, shared fixtures
```

## Test Structure

**Current validation (informal):**

The bot has three built-in validation phases instead of unit tests:

1. **Initialization Check** (see `bot.py` lines 201-215):
```python
if not self.dry_run:
    if not self.executor.initialize():
        print("\n❌ Failed to initialize. Check credentials.")
        return
    balance = self.executor.get_balance()
    print(f"  USDC balance: ${balance:.2f}")
```

2. **Price Feed Check** (see `bot.py` lines 218-223):
```python
print("\n⏳ Waiting for BTC price...")
price = self.price_feed.wait_for_price(timeout=30)
if not price:
    print("❌ No price feed. Check internet.")
    return
print(f"✅ BTC: ${price:,.2f} ({self.price_feed.state.source})")
```

3. **Market Discovery Check** (implicit in `_tick()` at line 253):
If no market found after API call, `_tick()` silently returns (no trade executed).

**If unit tests were written, expected pattern:**

```python
# test_strategy.py
def test_estimate_true_probability_high_delta():
    """Test that large BTC delta produces high confidence."""
    prob = estimate_true_probability(
        btc_delta_pct=0.15,
        seconds_remaining=180,
        vol=0.12
    )
    assert prob > 0.90, "0.15% move should be 90%+ confident"

def test_kelly_sizing_boundary():
    """Test Kelly fraction clamps to min/max bets."""
    signal = evaluate(
        btc_price=50000.0,
        opening_price=50000.0,
        up_market_price=0.51,
        down_market_price=0.49,
        seconds_remaining=250,
        bankroll=100.0,
        config=StrategyConfig(min_bet=5.0, max_bet=25.0),
    )
    assert signal.kelly_size >= 5.0
    assert signal.kelly_size <= 25.0

# test_executor.py
def test_order_size_calculation_precision():
    """Test that shares × price gives 2-decimal USD amounts."""
    shares, spend = calculate_order_size(price=0.71, max_usd=15.0)
    assert shares == int(shares), "Must be integer shares"
    assert spend == round(spend, 2), "Spend must be 2 decimals"

# test_market.py
def test_extract_token_ids_parses_json_strings():
    """Test that clobTokenIds and outcomes are parsed from JSON strings."""
    event_data = {
        "markets": [{
            "clobTokenIds": '["token-up-id", "token-down-id"]',  # JSON string
            "outcomes": '["Up", "Down"]'  # JSON string
        }]
    }
    up_id, down_id = extract_token_ids(event_data)
    assert up_id == "token-up-id"
    assert down_id == "token-down-id"
```

## Mocking

**Framework:**
- No mocking library installed (pytest-mock, unittest.mock not in requirements)
- Manual mocking via replacement/injection would be required

**Patterns (if mocking were added):**

Would use `unittest.mock.patch` to stub external dependencies:
```python
from unittest.mock import patch, MagicMock

@patch('urllib.request.urlopen')
def test_fetch_market_handles_timeout(mock_urlopen):
    """Test graceful timeout handling in market fetch."""
    mock_urlopen.side_effect = urllib.error.URLError("Connection timeout")
    market = fetch_market_by_slug("btc-updown-5m-1234567890")
    assert market is None  # Should return None on error

@patch('httpx.Client.post')
def test_order_verification_polls_balance(mock_post):
    """Test that balance is checked after order submission."""
    executor = Executor(private_key="test", dry_run=False)
    # Mock balance response
    mock_post.return_value.json.return_value = {"balance": 85.50}
    # ... verify balance snapshot logic
```

**What to Mock:**
- External APIs: Gamma API (`fetch_market_by_slug`), CLOB API (executor order submission), Binance prices
- File I/O: CSV writes (tracker), .env reads
- System calls: Tor process control (`ensure_tor`, `_stop_tor`)
- Time-dependent logic: use `freezegun` or `time.time()` mocking for signal window testing

**What NOT to Mock:**
- Strategy logic: `estimate_true_probability()`, Kelly sizing — these should be tested with real calculations
- Data classes: `MarketWindow`, `OrderResult`, `TradeSignal` — test with real instances
- Balance verification flow: test that balance snapshots correctly catch ghost fills (core safety feature)
- Thread safety of `PriceState`: test actual concurrent access patterns

## Fixtures and Factories

**Test Data (currently none exist):**

If fixtures were created, organization would be:

```python
# tests/fixtures/market_responses.py
def valid_5m_market_event():
    """Realistic Gamma API response for active 5-min BTC market."""
    return {
        "id": "0x123abc...",
        "slug": "btc-updown-5m-1234567890",
        "markets": [{
            "conditionId": "0x456def...",
            "clobTokenIds": '["0x11111...", "0x22222..."]',
            "outcomes": '["Up", "Down"]',
            "outcomePrices": '[0.51, 0.49]',
        }]
    }

def stale_market_response():
    """Market data with outdated prices (should not trigger entry)."""
    return {
        "markets": [{
            "outcomePrices": '[0.70, 0.30]',  # Extreme prices
            ...
        }]
    }

# tests/fixtures/price_ticks.py
def btc_tick_sequence():
    """Sequence of Binance trade ticks simulating 5-min window movement."""
    return [
        {"p": "50000.00", "t": 1234567890000},  # Open
        {"p": "50010.00", "t": 1234567895000},  # +0.02%
        {"p": "50005.00", "t": 1234568000000},  # -0.01% (bounce)
        {"p": "50020.00", "t": 1234568100000},  # +0.04% (strong move)
    ]

# tests/conftest.py
@pytest.fixture
def default_config():
    """StrategyConfig with standard parameters."""
    return StrategyConfig(
        min_edge=0.05,
        min_prob=0.80,
        min_btc_delta=0.06,
        kelly_fraction=0.25,
        min_bet=5.0,
        max_bet=25.0,
    )

@pytest.fixture
def executor_dry_run():
    """Dry-run executor (no live wallet)."""
    return Executor(private_key="test", safe_address="test", dry_run=True)

@pytest.fixture
def price_feed_mock():
    """Mock price feed with frozen price."""
    feed = BinancePriceFeed()
    feed.state.update(50000.0, source="test")
    return feed
```

## Coverage

**Requirements:** None enforced

- No coverage.py or pytest-cov installed
- No CI pipeline (no GitHub Actions, no coverage badges)
- Manual review: logs are the only coverage evidence
  - `signals.csv` shows every evaluated opportunity (traded or skipped)
  - `trades.csv` shows every trade entry-to-resolution lifecycle
  - Comparing these to Polymarket transaction history validates execution

**View Coverage (if configured):**
```bash
# Would run (if pytest-cov installed):
pytest --cov=. --cov-report=html tests/
# Generates htmlcov/index.html
```

## Test Types

**Unit Tests:**
- Not implemented
- Would test: strategy models, order calculation, market parsing
- Scope: single function, pure logic, no external dependencies

**Integration Tests:**
- Not implemented
- Would test: price feed → signal generation → order submission → balance verification
- Scope: multi-module workflow, mocked APIs

**E2E Tests:**
- Partially implemented via dry-run mode
- `DRY_RUN=true` executes full main loop without spending capital
- Manual validation: check stdout logs for correct entries, exits, and P&L calculations
- Post-run validation: compare `tracker/` CSV files to Polymarket history (see CLAUDE.md)

**Regression testing:**
- Manual: re-run specific market scenarios from history
- No automated regression suite

## Common Patterns

**If tests were written, expected async/error patterns:**

**Async Testing (WebSocket operations):**
```python
# test_price_feed.py
import asyncio
import pytest

@pytest.mark.asyncio
async def test_websocket_reconnect_on_disconnect():
    """Test WebSocket reconnection after connection loss."""
    feed = BinancePriceFeed()
    feed.start()
    
    # Simulate connection drop
    await feed._ws_thread.join(timeout=1)
    
    # Should auto-reconnect
    price = feed.wait_for_price(timeout=10)
    assert price > 0, "Should recover price after reconnect"
```

**Error Testing:**
```python
# test_executor.py
def test_buy_ghost_fill_detection():
    """Test that balance snapshot catches fills despite API exception."""
    executor = Executor(private_key="test", dry_run=False)
    
    # Mock: order API throws, but balance actually changed
    with patch.object(executor.client, 'create_order', side_effect=ConnectionError):
        with patch.object(executor, 'get_balance', side_effect=[100.0, 85.0]):
            # Before: $100, After: $85 → order went through despite exception
            result = executor.buy(
                side="up",
                price=0.71,
                shares=21,
                token_id="0x123"
            )
    
    # Should detect fill via balance change
    assert result.status != FAILED, "Ghost fill should be detected"

def test_order_minimum_notional_guard():
    """Test that orders below $5 are skipped."""
    executor = Executor(private_key="test", dry_run=False)
    
    # Attempt to sell $3 notional (below minimum)
    result = executor.sell(
        side="up",
        shares=10,
        token_id="0x123"
    )
    
    # At price $0.30: 10 × $0.30 = $3 < $5 minimum
    assert result.status == FAILED or "minimum" in result.error
```

**Boundary Testing:**
```python
# test_strategy.py
def test_kelly_sizing_with_zero_edge():
    """Test Kelly sizing when edge is exactly 0%."""
    signal = evaluate(
        btc_price=50000.0,
        opening_price=50000.0,
        up_market_price=0.50,  # No edge
        down_market_price=0.50,
        seconds_remaining=250,
        bankroll=100.0,
        config=StrategyConfig(),
    )
    
    assert signal.edge == 0.0
    # Should not trade on zero edge
    assert signal.side is None or signal.kelly_size == 0.0
```

## Current Validation Evidence

All validation currently happens in three places:

1. **Startup checks** (`bot.py` lines 201-223):
   - Wallet initialization
   - Balance retrieval
   - Price feed connection

2. **Signal logging** (`tracker.py` signals.csv):
   - Every opportunity evaluated (with or without trade)
   - Tracks edge, probability, market price, actual trade decision
   - Post-session review: compare win rate to probability model

3. **Trade lifecycle logging** (`tracker.py` trades.csv):
   - Entry price, shares, cost
   - Hold period extremes (max/min price, prob)
   - Exit price, P&L calculation
   - Resolution P&L comparison to Polymarket CSV

## Test Coverage Gaps

**Critical untested areas:**

| Area | What's not tested | Files | Risk |
|------|------------------|-------|------|
| Float precision | Integer share calculation edge cases (MIN_SHARES, large amounts) | `executor.py` lines 56-75 | Orders rejected if calculation is wrong |
| Gamma API JSON parsing | JSON string handling for clobTokenIds, outcomes | `market.py` lines 69-113 | Market discovery fails silently if parsing breaks |
| Window boundary sync | Real balance overwrite logic, drift detection | `bot.py` lines ~500+ | Accumulated P&L tracking errors |
| Pending buy detection | Balance checks 14s after unverified buys | `bot.py` lines 145-153 | Ghost orders treated as losses instead of fills |
| Telegram send failures | Silent failures (daemon threads, exception catching) | `telegram_notifier.py` lines 27-40 | Missed alerts during outages |
| Tor proxy routing | Exit node changes, circuit rebuilding | `proxy.py` lines 204-232 | VPN blocks treated as CLOB halts |
| Circular imports | Module dependency cycles | All .py | Import failures on reload |

**Highest priority to add tests:**
1. Order size calculation (prevents rejection errors)
2. Balance verification workflow (core safety system)
3. Window boundary sync (P&L accuracy)
4. JSON parsing from Gamma API (market discovery reliability)

---

*Testing analysis: 2026-05-07*
