# Codebase Concerns — Security Audit

**Analysis Date:** 2026-05-07

## Critical Security Issues

### 1. Private Key Exposure in Plain Environment

**Issue:** Private key loaded from `.env` file and stored in memory without encryption

**Files:** 
- `bot.py:101` — Loads `PRIVATE_KEY` via `os.getenv("PRIVATE_KEY", "")`
- `executor.py:79-82` — Stores `self.private_key` as plain string instance variable
- `.env` — Contains unencrypted `PRIVATE_KEY=0x...` (present on disk)

**Impact:** CRITICAL
- Private key sits in plaintext memory during entire bot runtime
- Core dumps, memory dumps, or debugger access = full wallet compromise
- `.env` file on disk is a single failure point
- No key rotation mechanism; compromised key requires manual intervention

**Current State:** 
- `.env` file exists but marked as "environment configuration"
- No warning in code about key exposure risks
- No cleanup/zeroing of key after initialization

**Mitigation:**
- Use OS-level secret storage (keychain, credential manager) instead of `.env`
- Implement key provider interface allowing pluggable backends
- Clear key from memory after `ClobClient` initialization
- Consider hardware wallet signing for production (remove private key entirely)

**Recommended Fix Path:**
1. Extract `Executor.__init__` to accept key bytes only at initialization time
2. Call `self.private_key = None` after passing to `ClobClient`
3. Use environment variable only as fallback; prefer `getpass` or system vault
4. Document that `.env` must be added to `.gitignore` with file permissions `600`

---

### 2. Telegram Bot Token and Chat ID in Plain Environment

**Issue:** Telegram credentials exposed in unencrypted `.env` file

**Files:**
- `telegram_notifier.py:13-14` — Loads `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` via `os.getenv()`
- `telegram_notifier.py:28` — Bot token embedded in URL: `f"https://api.telegram.org/bot{self.bot_token}/sendMessage"`
- `.env` — Contains unencrypted `TELEGRAM_BOT_TOKEN=...` and `TELEGRAM_CHAT_ID=...`

**Impact:** HIGH
- Telegram token allows attacker to:
  - Send arbitrary messages to the configured chat
  - Impersonate bot alerts (send fake loss/win alerts)
  - Enumerate chat history via telegram-cli
  - Potentially revoke token and lock owner out
- Chat ID reveals the Telegram account being targeted
- Token may be logged in HTTP libraries' debug output

**Current State:**
- Credentials passed to `urllib.request` as plain HTTP POST
- Thread-based sending means tokens may persist in thread locals
- No rate limiting on Telegram sends (spam vulnerability)

**Mitigation:**
- Store token with same OS-level secret storage as private key
- Rotate token periodically
- Never log full token in error messages
- Implement retry backoff for Telegram failures

---

### 3. Unencrypted Network Communication for Trading Orders

**Issue:** While Tor proxy is used for CLOB API, the implementation has routing gaps

**Files:**
- `proxy.py:238-289` — Routes httpx (CLOB trades) through Tor, BUT Gamma API (market discovery) intentionally unproxied
- `proxy.py:283` — Comment: "Gamma is read-only, not geoblocked, and proxying it...adds massive latency"
- `bot.py:176-181` — Tor proxy only applied if `not self.dry_run`
- `executor.py:228-229` — Order posting via httpx (proxied), but order details logged

**Impact:** MEDIUM
- Polymarket CLOB requests proxied through Tor — good
- But market discovery via `get_current_market()` → `market.py:57` → plain HTTPS to Gamma API
- ISP/network observer can see:
  - All market lookups (market discovery pattern)
  - Timestamps correlating with trades
  - Implied trading strategy from market slugs (`btc-updown-5m-{timestamp}`)
- Dry run mode (`DRY_RUN=true`) does NOT route through Tor — testing can leak location

**Current State:**
- Intentional design choice to skip Tor for Gamma (performance optimization)
- No warning about this privacy trade-off
- Dry run defaults to `DRY_RUN=true` in config examples

**Recommendations:**
- Document that market discovery patterns are visible to ISP
- Add optional Gamma proxy routing with latency warning
- Force `apply_proxy()` even in dry run if trading real keys
- Consider caching market data locally to reduce API calls

---

### 4. Trading Data Exfiltration via Telegram

**Issue:** Sensitive trading data sent to external Telegram service

**Files:**
- `telegram_notifier.py:42-51` — `trade_alert()` sends: side, price, amount, edge, kelly_size, market_slug
- `telegram_notifier.py:53-57` — Win/loss alerts include profit amounts
- `telegram_notifier.py:59-92` — Hourly summaries include: wins/losses, P&L, bankroll
- `bot.py:225-233` — Startup alert includes: kelly fraction, min edge, bet range, entry window
- `bot.py:815-819` — Every trade sent: `side`, `price`, `amount`, `edge`, `kelly_size`

**Impact:** MEDIUM
- Telegram stores chat history on Telegram servers (encryption at rest unclear)
- Attacker with Telegram account access (phishing, account takeover) gets full trading history
- Bot alerts leak:
  - Trade frequency and timing
  - Win/loss patterns (allows probability inference)
  - Exact bankroll and position sizes
  - Strategy parameters (kelly fraction, entry timing)
- Telegram API logs requests; Telegram server sees `TELEGRAM_CHAT_ID` in payload

**Current State:**
- No data minimization — full details sent for every event
- Telegram token unrotated; no expiration
- No e2e encryption (Telegram secret chats not used)

**Recommendations:**
1. **Minimal alerts:** Send only `WIN/LOSS` without amounts initially; details on-demand
2. **Digest mode:** Batch hourly summaries instead of per-trade alerts
3. **Encrypted channel:** Use Telegram secret chats or implement message encryption
4. **Token rotation:** Set Telegram bot token rotation schedule (monthly)
5. **Log sanitization:** Never send full edge/kelly values; round to nearest 5%

---

### 5. Subprocess Execution in `proxy.py` — Tor Process Management

**Issue:** `proxy.py` spawns and manages system Tor process without strong validation

**Files:**
- `proxy.py:219-232` — `subprocess.Popen([tor_bin, "-f", str(torrc)])`
- `proxy.py:117-130` — `_kill_port()` kills any process on port 9050 using `lsof` + `os.kill()`
- `proxy.py:115` — Hardcoded port 9050; no validation of `tor_bin` path beyond `shutil.which()`

**Impact:** MEDIUM
- `shutil.which("tor")` returns first `tor` in PATH — vulnerable to PATH injection
- `subprocess.Popen` without `cwd` or full path validation
- `os.kill(pid, signal.SIGTERM)` kills **any** process on port 9050, not just our Tor
  - Could accidentally kill legitimate system Tor, Privoxy, or VPN service
  - On macOS/Linux, `lsof` may not be available (code handles gracefully but silently)
- No `shell=False` explicit (subprocess uses shell if command is string) — handled correctly here
- Tor config written to `.tor/torrc` — not validated before being passed to Tor

**Current State:**
- `_kill_port()` silently fails if `lsof` not found (OK, but non-obvious)
- `ensure_tor()` raises `RuntimeError` if Tor not installed (good)
- Bootstrap timeout 120s — long wait with unclear error messages

**Recommendations:**
1. Use full path to Tor (`/usr/local/bin/tor`, `/usr/bin/tor`) instead of PATH search
2. Add check: before killing port, verify process is actually Tor
3. Validate torrc syntax before passing to Tor (dry-run mode: `tor -f <file> --verify-config`)
4. Document that calling `ensure_tor()` multiple times may kill other services
5. Add warning: "Do not run Tor proxy on shared/multi-tenant systems"

---

### 6. Balance Verification Timing Windows & Race Conditions

**Issue:** Multi-step balance verification creates windows where orders can be lost or double-counted

**Files:**
- `executor.py:214-244` — Buy: snapshot balance, wait 5s, verify 3 times at 3s intervals
- `executor.py:267-322` — `_verify_buy_via_balance()` — never cancels, returns `UNVERIFIED_BUY` after ~14s
- `bot.py:515-536` — Window boundary: detects pending buy by checking if balance dropped
- `executor.py:379-416` — Sell: snapshot balance, wait 2s, verify via balance change

**Impact:** MEDIUM
- **Ghost buy detection:** Relies on balance change > $1.0 (line 520: `if spent > 1.0`)
  - If order fills for exactly $0.99, it won't be detected
  - If two orders partially fill, balance logic breaks (can't distinguish which filled)
- **Window boundary sync:** May misattribute balance drops to pending buy when it was actually:
  - Network lag settling an old sell from previous window
  - Polygon reorg causing balance fluctuation
  - Unrelated contract interaction
- **Retry logic:** `_verify_buy_via_balance` tries order API + balance check, but doesn't distinguish:
  - Order not found (never submitted) vs. order pending (needs time)
  - API down vs. order legitimately failed
- **No transaction hash tracking:** Can't verify order actually landed on-chain

**Current State:**
- Code comments explicitly state "never cancel" (line 313-314), which is defensive
- Window boundary logic retroactively tracks "late fills" (line 523-536)
- But this assumes no concurrent orders or fast-settling partial fills
- No idempotency keys or nonce tracking

**Risk Assessment:** MEDIUM → HIGH if:
- Multiple markets trade in parallel
- Network conditions cause frequent reorgs
- Partial fills become common

**Recommendations:**
1. Lower ghost-buy threshold from $1.0 to $0.10 for better detection
2. Add order submission timestamp + `nonce` to prevent duplicate tracking
3. Query order status API first before balance check (order API is source of truth)
4. Log all balance snapshots for forensic reconciliation
5. Add warning: "Concurrent trades in multiple windows not supported"

---

### 7. Logging of Sensitive Trade Metadata

**Issue:** Tracker CSV files log sensitive trading data without access controls

**Files:**
- `tracker.py:113-123` — Creates CSV files: `signals.csv`, `trades.csv`, `executions.csv`
- `tracker.py:185-207` — `log_signal()` writes: btc_price, market_price, edge, kelly_size, side
- `tracker.py:227-248` — `log_trade_entry()` writes: entry_price, entry_cost, entry_shares, edge, prob
- `tracker.py:97-105` — `SESSION_FIELDS` logs: start_balance, end_balance, trades, wins, losses
- `logs/` directory created but no permission restrictions

**Impact:** MEDIUM
- CSV files written to `logs/` directory (default) with default umask
  - On shared systems, files world-readable (permissions likely `0644`)
  - Contains full P&L history, bankroll, strategy parameters
  - Timestamps allow inference of trading patterns and times
- No encryption or access controls
- CSV format is easily parsed and re-published
- Signal logs reveal model confidence and decision boundaries

**Current State:**
- Tracker always enabled (no opt-in for privacy-conscious users)
- No redaction mode or sampling
- Files accumulate indefinitely

**Recommendations:**
1. Set file permissions to `0600` after creation: `os.chmod(file, 0o600)`
2. Add config option: `TRACKER_ENABLED=false` to skip logging in production
3. Implement log rotation: keep only last 7 days of signals/trades
4. Add sanitization mode: log signals but omit exact prices/sizes
5. Document: "Logs contain sensitive trading data; store securely"

---

### 8. Telegram Message Injection via Unescaped Strings

**Issue:** Error messages and trade details passed directly to Telegram without sanitization

**Files:**
- `telegram_notifier.py:106` — `error_alert(error[:200])` sends raw error string
- `telegram_notifier.py:45-50` — `trade_alert()` inserts user parameters into markdown
- `bot.py:250` — `self.telegram.error_alert(str(e))` — exception message is untrusted
- `bot.py:696-700` — Status alerts with `msg` containing user-controlled data

**Impact:** LOW-MEDIUM
- Telegram markdown injection: if error contains `*bold*` or `_italic_`, it will render
  - Allows attacker to:
    - Format fake alerts (e.g., "**CRITICAL ISSUE**" false alarm)
    - Inject links via markdown (`[link](url)`)
    - Obfuscate real errors
- Not RCE, but allows social engineering via bot alerts

**Current State:**
- `error_alert()` truncates to 200 chars (good), but doesn't escape
- Markdown mode enabled (`"parse_mode": "Markdown"` in line 32)
- User inputs: exception text, market slugs, P&L numbers

**Recommendations:**
1. Add function to escape markdown:
   ```python
   def escape_markdown(text):
       for char in '*_`~|[]()':
           text = text.replace(char, '\\' + char)
       return text
   ```
2. Use `parse_mode=None` (disable markdown) or sanitize all user input
3. Log injection attempts (rare, but indicates compromise)

---

### 9. Clock Dependency Without Validation

**Issue:** Bot relies on system clock for market window timing; no validation or time sync check

**Files:**
- `market.py:35-39` — `current_window_ts()` uses `int(time.time())` directly
- `bot.py:256` — `window_ts = int(now) - (int(now) % period_secs)` determines trading window
- `bot.py:254-263` — Tick loop checks `if window_ts != self._current_window` to detect window change
- No NTP sync check; no clock skew correction

**Impact:** MEDIUM
- If system clock is >5 minutes slow:
  - Bot may trade in the wrong market window
  - Can place orders for wrong window's market
  - Confusion with resolved/active markets
- If clock is fast:
  - Bot may skip windows entirely (ticks jump ahead)
  - Trades never execute
- Polymarket server clock vs. bot clock skew >30s causes order rejections

**Current State:**
- No warning if system time is incorrect
- No validation of Polymarket server time
- `market.py:59` fetches Gamma API with no clock-sync check

**Recommendations:**
1. Add startup check:
   ```python
   server_time = self.executor.client.get_time()  # CLOB API endpoint
   local_time = int(time.time())
   skew = abs(server_time - local_time)
   if skew > 30:
       raise RuntimeError(f"System clock skew {skew}s — sync your clock!")
   ```
2. Log clock skew every hour
3. Validate market slug matches current window before trading
4. Add `--force` flag to override clock check (development only)

---

### 10. No Rate Limiting on Telegram Sends

**Issue:** Bot can send unlimited Telegram messages in rapid succession

**Files:**
- `telegram_notifier.py:19-24` — `send()` spawns unlimited threads, no rate limiting
- `telegram_notifier.py:26-40` — `_send_sync()` makes HTTP request synchronously in thread
- `bot.py:815-819`, `471`, `490` — Multiple telegram calls per trade window

**Impact:** LOW-MEDIUM
- Telegram API rate limit: ~30 messages/sec per bot
- If bot enters error loop, could spam Telegram and hit rate limit
- Rate-limited requests get `429` response; no retry logic
- Could trigger Telegram's "flood wait" (exponential backoff for hours)

**Current State:**
- Threads spawned without control
- No queue, no backoff
- No alerting if Telegram requests fail

**Recommendations:**
1. Implement queue with rate limiting:
   ```python
   from queue import Queue
   self.telegram_queue = Queue(maxsize=100)
   # Spawn 1 sender thread that dequeues + sends with 0.1s delay
   ```
2. Drop oldest messages if queue full (prevent memory leak)
3. Alert on Telegram send failures (log locally, don't retry indefinitely)

---

## Design Flaws & Anti-Patterns

### 11. Monkey-Patching Global HTTP Client

**Issue:** `proxy.py` globally patches `httpx.Client.__init__` at runtime

**Files:**
- `proxy.py:257-277` — Replaces `httpx.Client.__init__` and `httpx.AsyncClient.__init__`

**Impact:** MEDIUM
- **Side effects:** Any library imported after `apply_proxy()` gets patched httpx
- **Debugging nightmare:** Hard to trace why httpx behaves differently
- **Fragility:** If httpx changes its `__init__` signature, patch breaks silently
- **Library conflicts:** Other code expecting direct httpx control now goes through proxy
- **State sharing:** Patch is global; can't easily run multiple proxy configs in same process

**Better approach:**
- Pass proxy URL to `ClobClient` constructor instead of patching globally
- Create custom `httpx.Client` subclass with proxy pre-configured

**Recommendations:**
1. Refactor to pass proxy URL directly to executor:
   ```python
   executor = Executor(..., proxy_url="socks5h://..." if not dry_run else None)
   ```
2. Let `ClobClient` handle proxy configuration
3. Document: "Monkey-patching is a fragile pattern; avoid if possible"

---

### 12. Unvalidated Gamma API Responses

**Issue:** Market data from Gamma API not validated before use

**Files:**
- `market.py:54-66` — `fetch_market_by_slug()` trusts Gamma response completely
- `market.py:69-113` — `extract_token_ids()` has minimal validation:
  - No check if JSON parsing succeeds
  - No check if token IDs are valid hex
  - No check if `outcomes` matches `clobTokenIds` length
- `market.py:135-153` — Outcome prices parsed but not validated (could be null, negative, >1.0)

**Impact:** MEDIUM
- Malicious/corrupted Gamma API response could lead to:
  - Wrong token IDs (trader buys wrong market)
  - Invalid outcome prices (crashes probability model)
  - Empty data structures (crashes executor)
- MITM attack (if proxied through untrusted network) can inject fake markets

**Current State:**
- API response trusted as-is
- JSON parsing wrapped in try-except, but broadly catches all exceptions
- No schema validation

**Recommendations:**
1. Add Pydantic model for market response validation:
   ```python
   from pydantic import BaseModel, validator
   class MarketResponse(BaseModel):
       token_id_up: str  # validate hex
       token_id_down: str
       up_price: float  # validate 0 < x < 1
       down_price: float
   ```
2. Validate token IDs are valid Polymarket format
3. Check `up_price + down_price ≈ 1.0` (within 0.5%)
4. Fail loudly if validation fails (don't silently skip)

---

### 13. Unsafe Float Arithmetic in Position Sizing

**Issue:** Float rounding errors not explicitly handled in position sizing

**Files:**
- `executor.py:56-75` — `calculate_order_size()` converts to cents (good), but:
  - Line 62: `max_shares = max_usd_cents // price_cents` uses integer division
  - Rounding is implicit; no comment on intentional truncation
  - Edge case: if `max_usd_cents < price_cents`, returns (0, 0) silently
- `bot.py:725` — `trade_amount = round(sig.kelly_size, 2)` rounds to 2 decimals
- `strategy.py` — Kelly formula uses float division without explicit rounding

**Impact:** LOW-MEDIUM
- Accumulated rounding errors over many trades (Benford's law issues)
- User expects to trade $25, but rounding errors → actual $24.87
- Over 100 trades, ~$15 total error (0.15% drift)
- No audit trail of which trades were rounded vs. exact

**Current State:**
- Comments in `executor.py` explain the cents-based approach (good)
- But no explicit "rounding down is intentional" note
- No logging of actual vs. requested amounts

**Recommendations:**
1. Add explicit comment:
   ```python
   # Intentionally floor shares to avoid exceeding budget
   # (remainder stays in bankroll)
   shares = max_shares  # already floored by //
   ```
2. Log rounding: `if spend < max_usd: print(f"Rounding loss: ${max_usd - spend:.2f}")`
3. Quarterly audit: compare tracked bankroll vs. sum(executed amounts)

---

## Dependency Risks

### 14. `py-clob-client` Library Dependency

**Issue:** Bot depends on `py-clob-client>=0.34.5` — a community library with unclear maintenance

**Files:**
- `requirements.txt:1` — No version pinning (any >= 0.34.5)
- `executor.py:19-27` — Uses `ClobClient`, `OrderArgs`, `MarketOrderArgs`, etc.
- `CLAUDE.md:167-168` — Notes "decimal precision bug" in float division (line 1.0 - 0.71)

**Impact:** MEDIUM
- `py-clob-client` is maintained by Polymarket developers, but:
  - No pinned version (could auto-upgrade to breaking API)
  - Bug fixes require upstream merge (no control)
  - If maintainer loses interest, critical security fixes may be delayed
  - Float precision bugs documented (line 168 of CLAUDE.md) suggest precision issues

**Current State:**
- Requires explicit use of `create_order(OrderArgs)` to avoid precision bug
- Workaround documented in CLAUDE.md (version 10 fix, had to be re-applied)
- No automated tests to catch regressions

**Recommendations:**
1. Pin version: `py-clob-client==0.34.6` (specific, not >= range)
2. Monitor upstream changelog: check for security advisories
3. Add test that verifies decimal precision:
   ```python
   def test_no_decimal_precision_bug():
       order = OrderArgs(token_id="...", price=0.71, size=21.0)
       assert 21.0 * 0.71 == 14.91  # or fuzzy match
   ```
4. Fork/mirror library if upstream goes stale

---

## Missing Safeguards

### 15. No Circuit Breaker for Telegram Service Failure

**Issue:** If Telegram is unreachable, bot silently continues trading without alerting user

**Files:**
- `telegram_notifier.py:15` — `self.enabled` set based on token presence
- `telegram_notifier.py:26-40` — Failures printed locally, not escalated
- `bot.py:250` — `except Exception as e: ... self.telegram.error_alert(str(e))` — if Telegram fails, outer error not caught

**Impact:** MEDIUM
- User may not realize they're not receiving alerts
- Critical alerts (daily loss limit, CLOB halted) go unsent
- False sense of monitoring
- Dry run mode doesn't catch Telegram failures (no real alerts sent)

**Recommendations:**
1. Track Telegram send failures; if > 3 consecutive failures, **stop trading**
2. Add heartbeat: every 30 minutes, send keepalive message
   - If not received, user knows bot is down
3. Store failed messages to disk (recovery queue)
4. Require explicit `--assume-telegram-down` flag to trade without notifications

---

### 16. No Validation of Safe Address

**Issue:** Safe address (`SAFE_ADDRESS`) not validated before use

**Files:**
- `bot.py:102` — `safe_address=os.getenv("SAFE_ADDRESS", "")`
- `executor.py:90-93` — Passed to `ClobClient` with `signature_type=2` (Safe signature)
  - No validation that it's a valid Safe contract
  - No check if address matches the private key

**Impact:** LOW-MEDIUM
- Mistyped address → orders signed but routed to wrong Safe
- Shares transferred to wrong account
- P&L tracked against wrong account
- User loses funds without realizing

**Current State:**
- CLAUDE.md documents the specific address (line 228) but no code validation
- If user updates address but not private key, mismatch silently fails

**Recommendations:**
1. Add validation:
   ```python
   if not safe_address or not safe_address.startswith("0x"):
       raise ValueError("Invalid SAFE_ADDRESS format")
   if len(safe_address) != 42:
       raise ValueError("SAFE_ADDRESS must be 42 characters (0x + 40 hex)")
   ```
2. Query Safe contract to verify signer (private key owner) is authorized
3. Log Safe address at startup for user verification

---

### 17. No Kill Switch for Runaway Trading

**Issue:** No emergency stop mechanism if bot enters error loop

**Files:**
- `bot.py:243-251` — Main loop catches exceptions but continues
- `bot.py:703-715` — Daily loss limit halt, but no "kill by command" option
- No environment variable or external signal handler for emergency stop

**Impact:** MEDIUM
- If bot has a bug and enters infinite trade loop:
  - Could exhaust entire bankroll in minutes
  - User must kill process (loses position tracking)
  - Ctrl+C triggers shutdown (line 237: `signal.signal(signal.SIGINT, ...)`)
  - But on VPS or background process, no terminal access
- Daily loss limit works, but only if losses > threshold

**Current State:**
- `_handle_shutdown()` exists (line 1115) but only on SIGINT/SIGTERM
- No file-based kill switch (e.g., `touch /tmp/polybot-kill-me`)

**Recommendations:**
1. Add kill switch file:
   ```python
   def _check_kill_switch(self):
       if Path("/tmp/polybot-kill-me").exists():
           print("Kill switch activated — shutting down")
           self._running = False
   ```
2. Call in main loop before trading
3. Add flag: `--emergency-stop-loss` (e.g., `--emergency-stop-loss 50` stops at -$50)
4. Monitor bankroll; if drops >50% per hour, auto-halt

---

## Test & Validation Gaps

### 18. No Automated Tests

**Issue:** CLAUDE.md explicitly states "No automated tests yet" (line 316)

**Files:**
- No test directory
- No test files
- Validation is manual (terminal logs + CSV audit)

**Impact:** MEDIUM-HIGH
- Regressions not caught automatically
- Float precision bugs can reappear (was lost in v10, re-applied in v13)
- Edge cases in balance verification never validated
- New developer can break critical paths

**Recommendations:**
1. Add `tests/` directory
2. Start with critical path:
   ```python
   def test_buy_balance_verification():
       # Verify mock balance change is detected
   
   def test_decimal_precision():
       # Verify no float errors in order sizing
   
   def test_telegram_escaping():
       # Verify markdown injection fails
   ```
3. Add dry-run mode tests against mock market data
4. CI/CD: run tests on every push

---

## Summary by Severity

| Level | Count | Issues |
|-------|-------|--------|
| **CRITICAL** | 2 | Private key in plaintext; Telegram token in plaintext |
| **HIGH** | 3 | Balance verification race conditions; Data exfiltration via Telegram; Missing tests |
| **MEDIUM** | 10 | Network routing gaps; Logging of sensitive data; Subprocess execution; Monkey-patching; Float arithmetic; Dependency pinning; Circuit breakers; Validation gaps; Clock skew; Rate limiting |
| **LOW** | 3 | Markdown injection; Kill switch; Float rounding |

---

*Security audit: 2026-05-07*
