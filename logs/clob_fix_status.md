# CLOB Fix Status

**Date checked:** 2026-10-08

## New Releases Found (> v1.0.1)

| Version | Published | Notes |
|---------|-----------|-------|
| v1.0.2  | 2026-07-02 | Adds CLOB tick sizes 0.005 / 0.0025 — no auth changes |
| v1.1.0  | 2026-07-17 | Async transaction-hash resolution for matched orders — no auth changes |
| v1.2.0  | 2026-09-25 | Adds `position_id` support for limit/market orders — no auth changes |

- GitHub: https://github.com/Polymarket/py-clob-client-v2/releases

## Auth Bug Status (EIP-7702 / POLY_1271 API Key Issue)

**Core bug:** `create_or_derive_api_key()` binds the API key to the EOA instead of the deposit wallet, causing all orders to be rejected with "the order signer address has to be the address of the API KEY".

### Tracked Issues — Current State (as of 2026-10-08)

| Issue | Title | Status |
|-------|-------|--------|
| #70 | "POLY_1271 (sig type 3) order placement fails: L1 auth always binds API key to EOA" | **OPEN** |
| #75 | "POLY_1271 deposit-wallet orders rejected: 'order signer address must be API KEY'" | **OPEN** |
| #76 | "CLOB V2 Python SDK unusable for deposit wallets - /auth/api-key doesnt support EIP-1271" | **OPEN** |

**No Polymarket staff comments** visible on issues #70, #75, or #76.

### Related Closures (NOT direct fixes to sig_type=3 core bug)

| Issue | Closed | Notes |
|-------|--------|-------|
| #98  | 2026-07-03 | "sig_type=3 cannot post orders" — closed with no visible resolution; bug pattern persists in newer issues |
| #115 | 2026-09-05 | **sig_type=2 (Gnosis Safe) orders rejected with "maker address not allowed"** — directly relevant to current bot config (signature_type=2). Closed with no visible linked PR; may be server-side fix or won't-fix |
| #65  | 2026-05-17 | "create_or_derive_api_key binds API key to EOA" — closed, no linked PR |

### Issue #115 — Relevance to Current Bot

The current bot uses `signature_type=2` (Safe/proxy), matching issue #115. If #115 was resolved server-side by Polymarket, existing Safe-based accounts may now be able to place orders again. **Recommend testing with DRY_RUN=false to confirm.**

## What Changed Since Last Check (2026-10-06)

- Confirmed #70, #75, #76 still open with no new staff activity
- Added issue #115 (sig_type=2 / Gnosis Safe) to record — closed Sep 5, not previously noted
- Confirmed v1.2.0 (Sep 25) remains latest release with no auth changes

## Polymarket SDK Migration Note

The README now recommends `Polymarket/py-sdk` for new projects. This may be the intended path for deposit-wallet users rather than a fix to py-clob-client-v2 auth.

- https://github.com/Polymarket/py-sdk

## Next Step

Upgrade py-clob-client-v2 and re-test executor.py with MANUAL_MODE=false — issue #115 (sig_type=2 / Gnosis Safe) is now closed; if it was a server-side fix the current bot config may work. Also evaluate `Polymarket/py-sdk` as a longer-term replacement for deposit-wallet support.
