# CLOB Fix Monitor Status

**Date checked:** 2026-08-11

---

## New releases since v1.0.1

| Release | Date | Relevant to EIP-7702 bug? |
|---------|------|--------------------------|
| **v1.0.2** | 2026-07-02 | NO — adds tick sizes 0.005 and 0.0025 only |
| **v1.1.0** | 2026-07-17 | NO — resolves transaction hashes internally for async matched-order responses |

Both releases post-date the May 23 baseline. Neither contains a fix for the deposit wallet auth bug.

- v1.0.2: https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.0.2
- v1.1.0: https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.1.0

---

## Merged PRs since May 23, 2026 (auth-relevant scan)

| PR | Title | Date | Auth-related? |
|----|-------|------|--------------|
| #78 | docs: recommend new unified py-sdk in README | 2026-05-25 | No (docs only) |
| #95 | fix: support new tick sizes | 2026-07-02 | No |
| #96 | version: 1.0.2 | 2026-07-02 | No |
| #101 | refactor: resolve transaction hashes internally for matched orders | 2026-07-17 | No |

**No merged PRs touch create_or_derive_api_key, create_l1_headers, l1_auth, or deposit_wallet auth.**

---

## Tracked issue status (as of 2026-08-11)

All monitored issues remain **OPEN**:

| Repo | Issue | Status |
|------|-------|--------|
| py-clob-client-v2 | #55 | Open |
| py-clob-client-v2 | #70 | Open |
| py-clob-client-v2 | #71 | Open |
| py-clob-client-v2 | #75 | Open |
| py-clob-client-v2 | #76 | Open |
| clob-client-v2 | #65 | Open |

No Polymarket staff comments (JonathanAmenechi, suhailkakar, or org members) were found on issues #70, #75, #76.

---

## Notable development: Unified py-sdk recommended

PR #78 (merged 2026-05-25) updated the README to recommend **Polymarket/py-sdk** (REST + WebSockets unified client) as the preferred alternative to py-clob-client-v2. This SDK has not been confirmed to fix the EIP-7702/POLY_1271 deposit wallet auth issue, but may be worth evaluating.

- Repo: https://github.com/Polymarket/py-sdk
- PR: https://github.com/Polymarket/py-clob-client-v2/pull/78

---

## Core bug summary

`create_or_derive_api_key()` binds the API key to the EOA instead of the EIP-7702 deposit wallet. Orders then fail with:
> "the order signer address has to be the address of the API KEY"

The fix requires threading `funder` and `signature_type` through the L1 auth flow so the API key is registered against the deposit wallet address, not the EOA.

---

## Next steps

1. **Evaluate Polymarket/py-sdk** — the officially recommended unified SDK; check if it handles POLY_1271 / signature_type=3 correctly before investing time in py-clob-client-v2
2. **Test v1.1.0 of py-clob-client-v2** if you want to stay on the CLOB-only client; upgrade and re-test executor.py with `DRY_RUN=false` after verifying no regressions
3. **Watch issue #70** — reporter offered to submit a ~50-line PR fix; if it appears, that's the most actionable signal
