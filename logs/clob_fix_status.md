# CLOB Fix Status

**Date checked:** 2026-10-06

## New Releases Found (> v1.0.1)

| Version | Published | Notes |
|---------|-----------|-------|
| v1.0.2  | 2026-07-02 | Adds CLOB tick sizes 0.005 / 0.0025 — no auth changes |
| v1.2.0  | 2026-09-25 | Adds `position_id` support for limit/market orders — no auth changes |

- GitHub: https://github.com/Polymarket/py-clob-client-v2/releases

## Auth Bug Status (EIP-7702 / POLY_1271 API Key Issue)

**Core bug:** `create_or_derive_api_key()` binds the API key to the EOA instead of the deposit wallet, causing all orders to be rejected with "the order signer address has to be the address of the API KEY".

### Tracked Issues — Current State (as of 2026-10-06)

| Issue | Title | Status |
|-------|-------|--------|
| #70 | "POLY_1271 (sig type 3) order placement fails: L1 auth always binds API key to EOA" | **OPEN** |
| #75 | "POLY_1271 deposit-wallet orders rejected: 'order signer address must be API KEY'" | **OPEN** |
| #76 | "CLOB V2 Python SDK unusable for deposit wallets - /auth/api-key doesnt support EIP-1271" | **OPEN** |

Additional open issues confirming bug still unresolved: #85, #87, #90, #91, #104.

**No Polymarket staff comments** on issues #70, #75, or #76.

**Issue #98** ("signature_type=3 (POLY_1271) cannot post orders") was closed 2026-07-03, but with no visible resolution details or linked PR — may have been closed as duplicate or won't-fix. The bug pattern continues to appear in newer issues.

## What Changed

Neither v1.0.2 nor v1.2.0 addresses the API key/signer address authentication bug for POLY_1271 deposit wallets. The new releases add tick size support and position order support respectively.

## Next Step

Upgrade py-clob-client-v2 and re-test executor.py with MANUAL_MODE=false — but note the core auth bug (EOA-bound API key vs deposit wallet signer) is likely still present until a release explicitly addresses it. Monitor issues #70, #75, #76 for resolution.
