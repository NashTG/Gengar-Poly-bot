# CLOB Fix Status — 2026-10-21

## CRITICAL: py-clob-client-v2 is DEPRECATED

**Date checked:** 2026-10-21
**Checked by:** Scheduled CLOB monitor

---

## What changed

### New releases (all newer than v1.0.1 baseline)

| Version | Date | Notes |
|---------|------|-------|
| v1.0.2 | 2026-07-02 | Added tick size support (0.005, 0.0025). No auth changes. |
| v1.1.0 | 2026-07-17 | Async order execution pipeline. No auth changes. |
| v1.2.0 | 2026-09-25 | Position-backed orders (Exchange V3 signing). No auth changes. |
| **v1.2.1** | **2026-10-15** | **DEPRECATION NOTICE — package archived. Migrate to `polymarket-client`.** |

GitHub releases page: https://github.com/Polymarket/py-clob-client-v2/releases
PyPI: https://pypi.org/project/py-clob-client-v2/

---

## POLY_1271 / EIP-7702 bug status

**NOT FIXED in py-clob-client-v2.** The bug where `create_or_derive_api_key()` binds the API key to the EOA instead of the deposit wallet — causing "the order signer address has to be the address of the API KEY" — was **never patched** in any release of py-clob-client-v2.

Tracked issues still open (as of last check):
- https://github.com/Polymarket/py-clob-client-v2/issues/70
- https://github.com/Polymarket/py-clob-client-v2/issues/75
- https://github.com/Polymarket/py-clob-client-v2/issues/76
- https://github.com/Polymarket/clob-client-v2/issues/65

The repository is archived. No further fixes will be released here.

---

## Resolution path

Polymarket has deprecated py-clob-client-v2 and directed users to the unified **`polymarket-client`** SDK.

Migration guide: https://docs.polymarket.com/migrate/clob-sdk-to-unified-sdk

**Next step:** Investigate `polymarket-client` (PyPI: `polymarket-client`) to confirm it supports POLY_1271 / signature_type=3 deposit wallet flows, then rewrite `executor.py` against the new SDK and re-test with `DRY_RUN=true` before going live.

Do NOT upgrade to py-clob-client-v2 v1.2.1 — the POLY_1271 bug remains and the package is archived.
