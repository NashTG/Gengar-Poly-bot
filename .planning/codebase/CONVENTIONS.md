# Coding Conventions

**Analysis Date:** 2026-05-07

## Naming Patterns

**Files:**
- Module files: lowercase with underscores: `bot.py`, `price_feed.py`, `telegram_notifier.py`
- Main entry point: `bot.py`
- Archive/obsolete files: placed in `archive/` directory

**Functions:**
- Private methods (class methods prefixed with underscore): `_main_loop()`, `_tick()`, `_manage_position()`
- Public methods (no underscore): `start()`, `get_price()`, `wait_for_price()`
- Helper functions: lowercase with underscores: `current_window_ts()`, `market_slug()`, `extract_token_ids()`

**Variables:**
- Instance variables: lowercase with underscores: `self._running`, `self._trade_side`, `self._current_window`
- Constants (module-level): UPPERCASE: `PERIOD_SECONDS`, `MAX_BUY_PRICE`, `POLY_MIN_NOTIONAL`, `PERIOD_SECONDS`, `BINANCE_WS_URL`
- Local variables: lowercase: `btc_price`, `seconds_remaining`, `edge`
- Trade state tracking: prefixed with underscore for private state, descriptive names: `_trade_attempted`, `_trade_cost`, `_trade_shares`

**Types:**
- Data classes: PascalCase: `MarketWindow`, `OrderResult`, `TradeSignal`, `StrategyConfig`, `HourlyStats`, `TradingStats`
- Enum-like constants: UPPERCASE: `FILLED`, `PARTIAL`, `REJECTED`, `FAILED` (status codes in `executor.py`)

## Code Style

**Formatting:**
- No linter or formatter configured (raw Python, manually formatted)
- Indentation: 4 spaces
- Line wrapping: implied max ~100 characters (observed in real code, not strictly enforced)
- String formatting: f-strings exclusively (`f"Value: {var:.2f}"`)
- Spacing: two blank lines between top-level functions/classes, one blank line between methods

**Conventions in use:**
- Docstring placement: module-level docstrings at top (triple quotes with description)
- Class docstrings: immediately after class definition
- Function docstrings: immediately after `def` line, used inconsistently (some functions have them, most don't)
- Comments: inline comments explain "why", not "what" — used sparingly

## Import Organization

**Order:**
1. Standard library imports: `os`, `sys`, `time`, `signal`, `math`, `json`, `threading`, `subprocess`, `urllib.request`, `logging`, etc.
2. Third-party imports: `dotenv`, `websockets`, `httpx`, `py_clob_client`, etc.
3. Local module imports: `from market import`, `from strategy import`, `from executor import`, etc.

**Path Aliases:**
- No path aliases configured (all imports are direct)
- Relative imports: not used; all imports are absolute from project root

**Example imports from `bot.py`:**
```python
import os
import sys
import time
import signal
import math
import statistics
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    # Custom fallback implementation
    def load_dotenv(dotenv_path: str = ".env") -> None:
        ...

from market import get_current_market, current_window_ts, PERIOD_SECONDS
from price_feed import BinancePriceFeed
from strategy import evaluate, estimate_true_probability, get_skip_reason, StrategyConfig, TradingStats
```

## Error Handling

**Patterns:**
- Broad exception catching: `except Exception as e:` used throughout (catches all exceptions)
- Specific exception types: used in a few places: `except (ValueError, ProcessLookupError, PermissionError):` in `proxy.py`
- Exception logging: caught exceptions are printed to stdout or logged via Telegram: `print(f"[error] {e}")` or `self.telegram.error_alert(str(e))`
- No exception re-raising in most cases; instead, functions return error states or `None`
- Ghost fill detection: balance snapshots before/after orders catch API exceptions that hide fills (see `executor.py`)

**Error recovery:**
- Circuit breaker pattern: CLOB API failures trigger `_consecutive_buy_failures` counter; after 3 failures, `_clob_halted = True` (see `bot.py` line 169-171)
- Auto-recovery: circuit breaker resets on new window boundary when `get_ok()` succeeds
- Pending buy safety net: unverified buys are checked via balance sync at next window boundary

**No exception type discrimination:**
Most exception handlers don't distinguish between connection errors, JSON parsing failures, API errors, etc. They all get the same treatment: print/alert and continue or fail gracefully.

## Logging

**Framework:** `print()` statements only (no logger module)

**Patterns:**
- All logging uses `print()` with tagged prefixes: `[market]`, `[price]`, `[executor]`, `[error]`, `[telegram]`, `[tracker]`
- Stdout is the only log destination (see `bot.py` line 56-57 suppresses httpx logging to WARNING level)
- Log formatting: minimal — prefix + message, sometimes with f-string interpolation
- No structured logging (no JSON, no log levels beyond what print provides)

**When to log:**
- Entry/exit of major operations: price feed start (`[price] WebSocket connected`)
- API failures: `[market] Failed to fetch {slug}: {e}` (see `market.py` line 65)
- Alert-worthy events: trades, wins, losses printed to stdout + sent to Telegram
- Window transitions: `print(f"  📌 Open: ${btc_price:,.2f}")` (see `bot.py` line 269)

**What NOT to log:**
- Every tick (100+ per second) — only position management and entries
- Stack traces — exceptions printed as simple strings
- Debug variables — only error conditions or state transitions

**Telegram logging:**
- All major alerts sent via `self.telegram.send()` (see `telegram_notifier.py`)
- Async send (non-blocking) via threading daemon
- Alert types: `trade_alert()`, `win_alert()`, `loss_alert()`, `error_alert()`, `hourly_summary()`

## Comments

**When to Comment:**
- Algorithm explanation: Brownian motion model comments at top of `strategy.py` (see module docstring)
- Non-obvious logic: balance verification steps in `executor.py` (see comments on ghost fills)
- Safety systems: circuit breaker purpose documented at class-level (see `bot.py` line 168-170)

**JSDoc/TSDoc:**
- Not used (Python doesn't have standard JSDoc equivalent)
- Module docstrings used instead: detailed explanation at file top (see `executor.py`, `tracker.py`)
- Data class docstrings: brief, in-line (see `HourlyStats` line 43 in `strategy.py`)

## Function Design

**Size:**
- Methods: vary widely from 10 lines (`_stop_tor()`) to 200+ lines (`_execute_trade()`)
- No explicit size limit enforced
- Large functions encapsulate related state: `_execute_trade()` handles entry decision → order submission → verification (see `bot.py` line 680+)

**Parameters:**
- Positional parameters: used for required inputs: `def buy(self, side, price, shares, token_id)`
- Keyword arguments: used with defaults for optional config: `def send(self, message: str, silent: bool = False)` (see `telegram_notifier.py` line 19)
- Type hints: used throughout (see `executor.py`, `price_feed.py`, `strategy.py`)
- Type annotations: parameter and return types specified: `def current_window_ts(period_minutes: int = 5) -> int:`

**Return Values:**
- Single value: `def get_price(self) -> tuple[float, bool]:` returns (price, is_fresh)
- Tuples for multiple returns: `def extract_token_ids(event_data: dict) -> tuple[str, str]:`
- Data classes: `OrderResult` wraps multiple return fields (see `executor.py` line 42-53)
- None for failures: `def get_current_market(...) -> Optional[MarketWindow]:` (see `market.py` line 116)

## Module Design

**Exports:**
- No `__all__` declarations observed
- All module-level functions implicitly exported
- Classes and functions used directly by name

**Barrel Files:**
- Not used (no index.py or __init__.py files with re-exports)

**Module organization:**
Each module owns a specific domain:
- `bot.py`: Main event loop, position lifecycle, entry/exit decisions
- `strategy.py`: Probability models, position sizing, stats tracking
- `executor.py`: Order placement, balance verification, fill detection
- `market.py`: Market discovery, token ID extraction, price retrieval
- `price_feed.py`: BTC price subscription (WebSocket + REST fallback)
- `telegram_notifier.py`: All alert dispatch and message formatting
- `tracker.py`: Three-file CSV logging (signals, trades, executions)
- `proxy.py`: Tor routing configuration and lifecycle

**Circular imports:**
- Checked: no circular dependencies found (each module imports only its dependencies, never back-imports)

## Data Classes and Dataclasses

**Usage:**
- `@dataclass` decorator used throughout (see `strategy.py`, `executor.py`, `market.py`, `price_feed.py`)
- Default values provided: `@dataclass` fields with `= field(default_factory=list)` for mutable defaults
- Property methods used to compute derived values: `@property` decorators in `HourlyStats`, `MarketWindow`, `PriceState`

**Example:**
```python
@dataclass
class MarketWindow:
    slug: str
    condition_id: str
    token_id_up: str
    token_id_down: str
    window_start: int
    window_end: int
    opening_price: Optional[float] = None
    up_price: float = 0.50
    down_price: float = 0.50

    @property
    def seconds_remaining(self) -> float:
        return max(0, self.window_end - time.time())
```

## Threading and Concurrency

**Model:**
- Single main thread: bot event loop runs in main thread
- Background threads: used for non-blocking operations only
  - Price feed WebSocket reader (daemon thread, see `price_feed.py` line 58)
  - REST price poller (daemon thread, see `price_feed.py` line 62)
  - Telegram sender (daemon thread, see `telegram_notifier.py` line 22)

**Thread-safety:**
- `PriceState` class uses `threading.Lock` for safe concurrent reads/writes (see `price_feed.py` line 25-36)
- No other explicit thread synchronization used
- Assumption: main thread waits for price updates before making trades

**Concurrency strategy:**
Never blocks the main trading loop. Price updates, Telegram sends, and price polling all happen in background threads.

## Configuration

**Environment Variables:**
- Loaded via `dotenv` library (or custom fallback in `bot.py` line 38-54)
- `.env` file read at startup
- No runtime reloading (changes require restart)

**Examples from `.env` (not actual secrets, see CLAUDE.md):**
```
DRY_RUN=true
MARKET_PERIOD=5
MIN_EDGE=0.05
MIN_PROB=0.80
KELLY_FRACTION=0.25
MIN_BET=5.0
MAX_BET=25.0
BANKROLL=100.0
DAILY_LOSS_LIMIT=30
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

## Type Hints

**Policy:**
- Type hints used consistently for function parameters and return types
- Union types: `Optional[T]` used for nullable returns: `Optional[MarketWindow]`, `Optional[dict]`
- Complex types: tuples used: `tuple[float, float]`, `tuple[str, str]`
- Callable types: used for callbacks: `on_price: Callable = None` (see `price_feed.py` line 50)

**Example:**
```python
def create_order(
    self, 
    side: str, 
    price: float, 
    shares: float, 
    token_id: str
) -> OrderResult:
```

---

*Convention analysis: 2026-05-07*
