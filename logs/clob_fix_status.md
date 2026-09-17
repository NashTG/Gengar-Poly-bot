# CLOB Fix Status Monitor — 2026-09-17

## Summary

New releases exist (v1.0.2 and v1.1.0, both > v1.0.1), and two directly-related issues on
py-clob-client-v2 (#65, #98) are now CLOSED with the exact POLY_1271/create_or_derive_api_key
bug description. However, the new releases do NOT appear to contain the auth fix, and all
originally tracked issues remain open. **Recommend upgrade + manual re-test to confirm.**

---

## What Changed

### New Releases (both > v1.0.1)

| Version | Date | Content | Auth Fix? |
|---------|------|---------|-----------|
| v1.0.2 | 2026-07-02 | Add tick sizes 0.005 and 0.0025 | ❌ No |
| v1.1.0 | 2026-07-17 | Async execution: resolve tradeIDs → transactionHashes internally (PR #101) | ❌ No |

### Closed Related Issues (not in original tracked list, but directly about this bug)

| Issue | Repo | Title | Status |
|-------|------|-------|--------|
| #65 | py-clob-client-v2 | "Cannot submit POLY_1271 orders — `create_or_derive_api_key` binds API key to EOA, not deposit wallet" | **CLOSED** — reason unknown |
| #98 | py-clob-client-v2 | "signature_type=3 (POLY_1271) cannot post orders: 'the order signer address has to be the address of the API KEY'" | **CLOSED** — reason unknown |

### Tracked Issues Still Open

All originally tracked issues remain unresolved:
- py-clob-client-v2: #55, #56, #57, #58, #61, #63, #64, #70, #71, #75, #76 — all OPEN
- clob-client-v2: #65 — OPEN, no staff comments

Checked #70, #75, #76 specifically: **no Polymarket staff (JonathanAmenechi, suhailkakar) responses found.**

---

## Relevant Links

- [v1.1.0 release](https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.1.0)
- [v1.0.2 release](https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.0.2)
- [py-clob-client-v2 #65 (closed)](https://github.com/Polymarket/py-clob-client-v2/issues/65)
- [py-clob-client-v2 #98 (closed)](https://github.com/Polymarket/py-clob-client-v2/issues/98)
- [py-clob-client-v2 #70 (open, no staff response)](https://github.com/Polymarket/py-clob-client-v2/issues/70)
- [clob-client-v2 #65 (open)](https://github.com/Polymarket/clob-client-v2/issues/65)

---

## Assessment

Issues #65 and #98 on py-clob-client-v2 were closed with the exact bug description being
monitored. Closure reason is unclear from public page content — could be:
- A fix was merged that doesn't appear in the PR list (unlikely given PRs #95/#96/#101 are unrelated)
- Issues were closed as "duplicate" pointing to tracked #70+
- Issues were closed as "by design / use py-sdk instead" (Polymarket added a py-sdk redirect in PR #78)

**PR #78 (merged 2026-05-25):** "docs: recommend new unified py-sdk in README" — Polymarket may be
redirecting users to `polymarket/py-sdk` instead of fixing py-clob-client-v2 directly.

---

## Next Step

**Upgrade py-clob-client-v2 to v1.1.0 and re-test executor.py with MANUAL_MODE=false.**

Also check: `pip install polymarket-py-sdk` — Polymarket may have landed the fix in a separate
unified SDK (`py-sdk`) rather than patching py-clob-client-v2. If py-sdk supports
POLY_1271/deposit-wallet flow, migrate executor.py to that library.
