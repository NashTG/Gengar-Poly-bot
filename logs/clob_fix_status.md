# CLOB Fix Status

**Date checked:** 2026-10-12

## New Releases Found (> v1.0.1)

| Version | Published | Notes |
|---------|-----------|-------|
| v1.0.2  | 2026-07-02 | Adds CLOB tick sizes 0.005 / 0.0025 — no auth changes |
| v1.1.0  | 2026-07-17 | Async transaction-hash resolution for matched orders — no auth changes |
| v1.2.0  | 2026-09-25 | Adds `position_id` support for limit/market orders — no auth changes |

- GitHub: https://github.com/Polymarket/py-clob-client-v2/releases

## Auth Bug Status (EIP-7702 / POLY_1271 API Key Issue)

**Core bug:** `create_or_derive_api_key()` binds the API key to the EOA instead of the deposit wallet, causing all orders to be rejected with "the order signer address has to be the address of the API KEY".

### Tracked Issues — Current State (as of 2026-10-12)

| Issue | Title | Status |
|-------|-------|--------|
| #55  | "POLY_1271: order signer always set to EOA instead of funder" | **OPEN** |
| #56  | "Order placement returns 400 'maker address not allowed'" | **OPEN** (assumed) |
| #57  | "[BUG] Cannot place sigtype=3 (POLY_1271 / Magic Wallet) orders" | **OPEN** (assumed) |
| #58  | "Question: How should CLOB API credentials be created for deposit wallet?" | **OPEN** (assumed) |
| #61  | "'maker address not allowed' for new MetaMask accounts" | **OPEN** (assumed) |
| #63  | "[BUG] post_order rejected for new MetaMask deposit wallet accounts" | **OPEN** (assumed) |
| #64  | "POLY_1271 + Deposit Wallet: 'signer address has to be the address of the API KEY'" | **OPEN** (assumed) |
| #70  | "POLY_1271 (sig type 3) order placement fails: L1 auth always binds API key to EOA" | **OPEN** |
| #71  | "POLY_1271 orders fail: 'the order signer address has to be the address of the API KEY'" | **OPEN** (assumed) |
| #75  | "POLY_1271 deposit-wallet orders rejected: 'order signer address must be API KEY'" | **OPEN** |
| #76  | "CLOB V2 Python SDK unusable for deposit wallets - /auth/api-key doesnt support EIP-1271" | **OPEN** |

**No Polymarket staff comments** visible on any of the tracked issues.

### Related Closures (NOT direct fixes to sig_type=3 core bug)

| Issue | Closed | Notes |
|-------|--------|-------|
| #98  | 2026-07-03 | "sig_type=3 cannot post orders" — closed with no visible resolution; bug pattern persists in newer issues |
| #115 | 2026-09-05 | **sig_type=2 (Gnosis Safe) orders rejected with "maker address not allowed"** — directly relevant to current bot config (signature_type=2). Closed with no visible linked PR; may be server-side fix or won't-fix |
| #65  | 2026-05-17 | "create_or_derive_api_key binds API key to EOA" — closed, no linked PR (clob-client-v2 repo) |

## New Since Last Check (2026-10-08 → 2026-10-12)

- **Issue #70 (Oct 8):** Community user vladII987 reported successfully placing a funded, filled order on a new EIP-1167 deposit wallet using EOA-addressed L1/L2 auth with py-clob-client-v2 v1.2.0. osr21 confirmed the original "signer address" mismatch "not reproduced for this tested flow." **However**: EIP-7702 wallets specifically remain broken per RICK0308 (Sep 6/8 comments with no reply).
- **Issue #75 (Aug 21):** Community user dcpf1 reported a POLY_1271 setup trading successfully since June — key insight: derive API credentials from a `ClobClient` already configured with `signature_type=3` and `funder`, and call `update_balance_allowance()` using that client directly.
- **No new releases** since v1.2.0 (Sep 25).
- **No staff-confirmed fix** for EIP-7702 deposit wallets specifically.

## Summary Assessment

EIP-1167 proxy wallet accounts (the majority of new Polymarket accounts) appear to work with v1.2.0 if configured correctly (signature_type=3, funder set, API key derived from funder-configured client). EIP-7702 accounts specifically remain broken. The current bot uses **signature_type=2 (Gnosis Safe)** — issue #115 (sig_type=2 "maker address not allowed") was closed Sep 5, suggesting a possible server-side fix for Safe-based accounts.

## Polymarket SDK Migration Note

The README now recommends `Polymarket/py-sdk` for new projects. This may be the intended long-term path for deposit-wallet users.

- https://github.com/Polymarket/py-sdk

## Next Step

Upgrade py-clob-client-v2 and re-test executor.py with MANUAL_MODE=false — issue #115 (sig_type=2 / Gnosis Safe) is now closed; if it was a server-side fix the current bot config may work. Also evaluate `Polymarket/py-sdk` as a longer-term replacement for deposit-wallet support.
