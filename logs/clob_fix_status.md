# CLOB Fix Status — 2026-09-26

## Summary

Three new releases exist beyond v1.0.1, but **none fix the deposit-wallet / EIP-7702 auth bug**.
All tracked issues remain open. No Polymarket org member comments on any tracked issue.
Latest release v1.2.0 (Sep 25, 2026) adds PolyV2 position orders — unrelated to auth.

---

## New Releases Found

| Version | Released | What Changed |
|---------|----------|--------------|
| **v1.2.0** | 2026-09-25 | PolyV2 position orders: adds `position_id` support to order workflows, auto-selects Exchange V3 signing |
| **v1.1.0** | 2026-07-17 | Async execution: resolve transaction hashes internally when API returns `tradeIDs` |
| **v1.0.2** | 2026-07-02 | Added support for CLOB tick sizes `0.005` and `0.0025` |

- **v1.0.2**: https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.0.2
- **v1.1.0**: https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.1.0
- **v1.2.0**: https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.2.0

None of these releases touch `create_or_derive_api_key`, `l1_auth`, `create_l1_headers`, or deposit-wallet authentication.

---

## Tracked Issues — All Still OPEN (confirmed 2026-09-26)

| Repo | Issue | Status | Title |
|------|-------|--------|-------|
| py-clob-client-v2 | #70 | **Open** | POLY_1271 orders fail: L1 auth binds API key to EOA, never deposit wallet |
| py-clob-client-v2 | #75 | **Open** | POLY_1271 deposit-wallet orders rejected: signer ≠ API KEY address |
| py-clob-client-v2 | #76 | **Open** | SDK unusable for deposit wallets — /auth/api-key doesn't support EIP-1271 |
| py-clob-client-v2 | #55–#64, #71 | Not confirmed individually | Same auth pattern |
| clob-client-v2    | #65 | Not individually confirmed | Same auth pattern |

---

## Notable: Maintainers Recommend Migration to py-sdk

PR #78 (merged 2026-05-25) added a README note recommending developers migrate to the unified
[Polymarket/py-sdk](https://github.com/Polymarket/py-sdk) instead of using py-clob-client-v2.

The py-sdk is at **v0.10.0** (released 2026-09-10) and includes "scoped session keys" (v0.7.0,
released 2026-08-26). Session keys may offer an alternative auth path, but the release notes do
not explicitly confirm they resolve the `"order signer address has to be the address of the API KEY"`
error for POLY_1271 accounts.

**This warrants manual investigation**: py-sdk may have quietly solved the EIP-7702 problem via
the session-key flow even without a direct issue reference.

---

## What Each Release Fixed

- v1.0.2: Tick size support only — no auth changes.
- v1.1.0: Async transaction hash resolution only — no auth changes.
- v1.2.0: PolyV2 position orders (position_id support) — no auth changes.

---

## Next Step

The original bug (EIP-7702 deposit wallet / POLY_1271 not supported in py-clob-client-v2) is
**still unresolved** in this SDK as of v1.2.0.

Recommended actions:
1. **Investigate py-sdk session keys**: Test whether `Polymarket/py-sdk` v0.7.0+ handles
   POLY_1271 order placement without the signer mismatch error.
2. If py-sdk works: Rewrite `executor.py` against py-sdk's trading API with `MANUAL_MODE=false`.
3. If py-sdk doesn't work: Continue monitoring py-clob-client-v2 — no Polymarket staff have
   commented on any of the tracked issues, suggesting a fix is not imminent.
