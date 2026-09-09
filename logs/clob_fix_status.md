# CLOB Fix Status — 2026-09-09

## Fix Signal Detected

**Date found:** 2026-09-09
**Monitoring baseline:** v1.0.1 (2026-05-09), no auth fix as of 2026-05-23

---

## What Changed

### New releases (both > v1.0.1)

| Version | Date | Notes |
|---------|------|-------|
| v1.0.2  | 2026-07-02 | Adds tick sizes 0.005 / 0.0025 — no auth fix |
| v1.1.0  | 2026-07-17 | Async execution (tradeIDs) — no auth fix |

- v1.0.2 release: https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.0.2
- v1.1.0 release: https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.1.0

### Issue #98 closed (2026-07-03)
"signature_type=3 (POLY_1271) cannot post orders: 'the order signer address has to be the address of the API KEY'"
- URL: https://github.com/Polymarket/py-clob-client-v2/issues/98
- Closure reason: UNKNOWN — may be "won't fix" / redirect to new SDK

### PR #78 merged (2026-05-25) — Polymarket redirects to new unified SDK
"docs: recommend new unified py-sdk in README"
- URL: https://github.com/Polymarket/py-clob-client-v2/pull/78
- Points users to: https://github.com/Polymarket/py-sdk

---

## What Was NOT Fixed

**The core auth bug remains unfixed in py-clob-client-v2.**

- Issues #70, #75, #76 are **still OPEN** as of 2026-09-09
- No merged PR in py-clob-client-v2 touches `create_or_derive_api_key`, `l1_auth`, or deposit wallet auth binding
- Neither v1.0.2 nor v1.1.0 release notes mention EIP-7702, POLY_1271, or API key binding

---

## Key Interpretation

Polymarket appears to be abandoning py-clob-client-v2 in favor of a new unified `Polymarket/py-sdk`.
The fix for the POLY_1271/EIP-7702 deposit wallet auth bug is likely in that new SDK rather than in this one.
Issue #98 may have been closed as "resolved in py-sdk" rather than fixed here.

---

## Next Steps

1. **Investigate `Polymarket/py-sdk`**: https://github.com/Polymarket/py-sdk
   - Check if it supports signature_type=3 / POLY_1271 deposit wallet order placement
   - Check if `create_or_derive_api_key` equivalent binds to deposit wallet correctly
   - Check latest version and PyPI package name

2. **If py-sdk fixes the bug**: Migrate executor.py to use `Polymarket/py-sdk` instead of upgrading py-clob-client-v2

3. **If upgrading py-clob-client-v2**: `pip install py-clob-client-v2==1.1.0` and re-test executor.py with MANUAL_MODE=false — but the auth bug is likely still present

4. **Upgrade py-clob-client-v2 and re-test executor.py with MANUAL_MODE=false** (per original instruction, after confirming whether py-sdk is the real fix path)
