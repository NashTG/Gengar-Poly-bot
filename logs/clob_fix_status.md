# CLOB Fix Status — 2026-11-06

## Status: MAJOR UPDATE — Package deprecated, migrate to polymarket-client

---

## What changed since last check (2026-05-23)

### New releases (all > v1.0.1)

| Version | Date | Notes |
|---------|------|-------|
| v1.0.2  | 2026-07-02 | Tick size support only, no auth changes |
| v1.1.0  | 2026-07-17 | Async execution support, no auth changes |
| v1.2.0  | 2026-09-25 | (details not checked) |
| **v1.2.1** | **2026-10-15** | **Package DEPRECATED — migrate to `polymarket-client`** |

Release page: https://github.com/Polymarket/py-clob-client-v2/releases

### Relevant merged PR

- **#39** — "feat: add deposit wallet order support" — merged 2026-05-01 by suhailkakar, approved by JonathanAmenechi
  - Adds POLY_1271 order signing via `signature_type=3` and `funder` parameter
  - Was included in v1.0.1rc1 / v1.0.1
  - This is the foundational fix, but community reports suggest the EIP-7702 `create_or_derive_api_key` binding issue persisted
  - PR: https://github.com/Polymarket/py-clob-client-v2/pull/39

---

## Issue status (tracked issues: 55 56 57 58 61 63 64 70 71 75 76)

- **#70** (POLY_1271 L1 auth binds API key to EOA): Still **OPEN**. No staff comments. Community workaround: use `signature_type=3` + `funder` in existing SDK.
- **#75** (deposit-wallet signer address rejected): Still **OPEN**. Community reports POLY_1271 working since June if set up correctly.
- **#76** (email/deposit-wallet path blocked): Still **OPEN**. No staff comments. Workaround via MetaMask (not email login) reported by community.
- **#115** (signature_type=2 orders rejected): **CLOSED** 2026-09-05.
- Other tracked issues not confirmed closed via this check.

---

## Critical: py-clob-client-v2 is now DEPRECATED

As of v1.2.1 (Oct 15, 2026), Polymarket officially deprecated `py-clob-client-v2`.

> "This package is deprecated. Please migrate to the unified Polymarket Python SDK (`polymarket-client`)."

The new unified SDK: **`polymarket-client`**
- PyPI: https://pypi.org/project/polymarket-client/
- Latest version: **v0.17.0** (released 2026-11-05)
- GitHub: https://github.com/Polymarket/py-sdk

The EIP-7702/POLY_1271 fix likely lives in `polymarket-client`, not in a future py-clob-client-v2 patch — no more patches will come to the old SDK.

---

## Next step

**Migrate executor.py to `polymarket-client` v0.17.0** — this is the official Polymarket path forward and where the deposit-wallet auth fix is expected to reside.

1. `pip install polymarket-client==0.17.0`
2. Check the migration guide at https://github.com/Polymarket/py-sdk
3. Rewrite `executor.py` using the new unified SDK's order creation API
4. Test with `DRY_RUN=true` first, then live with small bankroll
5. The old `py-clob-client-v2` will not receive further fixes
