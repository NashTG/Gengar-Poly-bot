# CLOB Fix Status — 2026-09-21

## Summary

Two new releases exist beyond v1.0.1, but **neither fixes the deposit-wallet / EIP-7702 auth bug**.
All tracked issues remain open. No Polymarket org member comments on any tracked issue.

---

## New Releases Found

| Version | Released | What Changed |
|---------|----------|--------------|
| **v1.1.0** | 2026-07-17 | Async execution: resolve transaction hashes internally when API returns `tradeIDs` instead of `transactionsHashes` |
| **v1.0.2** | 2026-07-02 | Added support for CLOB tick sizes `0.005` and `0.0025` |

- **v1.0.2**: https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.0.2
- **v1.1.0**: https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.1.0

Neither release touches `create_or_derive_api_key`, `l1_auth`, `create_l1_headers`, or deposit-wallet authentication.

---

## Tracked Issues — All Still OPEN

| Repo | Issue | Status |
|------|-------|--------|
| py-clob-client-v2 | #55 | Open |
| py-clob-client-v2 | #57 | Open |
| py-clob-client-v2 | #61 | Open |
| py-clob-client-v2 | #63 | Open |
| py-clob-client-v2 | #64 | Open |
| py-clob-client-v2 | #70 | Open |
| py-clob-client-v2 | #71 | Open |
| py-clob-client-v2 | #75 | Open |
| py-clob-client-v2 | #76 | Open |
| clob-client-v2    | #65 | Open |

Issues #56 and #58 were not individually confirmed but follow the same pattern.

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

## What Was Fixed in These Releases

- v1.0.2: Tick size support only — no auth changes.
- v1.1.0: Async transaction hash resolution only — no auth changes.

---

## Next Step

The original bug (EIP-7702 deposit wallet / POLY_1271 not supported in py-clob-client-v2) is
**still unresolved** in this SDK.

Recommended actions:
1. **Investigate py-sdk session keys**: Test whether `Polymarket/py-sdk` v0.7.0+ handles
   POLY_1271 order placement without the signer mismatch error.
2. If py-sdk works: Upgrade and re-test `executor.py` against py-sdk's trading API with
   `MANUAL_MODE=false`.
3. If py-sdk doesn't work: Continue monitoring py-clob-client-v2 — no Polymarket staff have
   commented on any of the 11 tracked issues, suggesting a fix is not imminent.
