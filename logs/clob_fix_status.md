# CLOB Fix Status — 2026-10-22 (updated)

## CRITICAL: py-clob-client-v2 is DEPRECATED

**Last checked:** 2026-10-22  
**Previous check:** 2026-10-21  
**Checked by:** Scheduled CLOB monitor

---

## What changed (since v1.0.1 baseline)

### New releases

| Version | Date | Notes |
|---------|------|-------|
| v1.0.2 | 2026-07-02 | Added tick size support (0.005, 0.0025). No auth changes. |
| v1.1.0 | 2026-07-17 | Async order execution pipeline. No auth changes. |
| v1.2.0 | 2026-09-25 | Position-backed orders (Exchange V3 signing). No auth changes. |
| **v1.2.1** | **2026-10-15** | **DEPRECATION NOTICE — package archived. Migrate to `polymarket-client`.** |

GitHub releases page: https://github.com/Polymarket/py-clob-client-v2/releases

### Relevant merged PRs

| PR | Title | Merged | Notes |
|----|-------|--------|-------|
| #39 | feat: add deposit wallet order support | 2026-05-01 | POLY_1271 order signing; does NOT fix API key binding |
| #78 | docs: recommend new unified py-sdk in README | 2026-05-25 | Points to Polymarket/py-sdk |
| #120 | docs: add package deprecation warning | 2026-10-15 | Official deprecation |

---

## POLY_1271 / EIP-7702 bug status

**NOT FIXED in py-clob-client-v2.** The bug where `create_or_derive_api_key()` binds the API key to the EOA instead of the deposit wallet — causing "the order signer address has to be the address of the API KEY" — was **never properly patched**.

### Issues closed in py-clob-client-v2 (partial/disputed fixes)

| Issue | Title | Closed |
|-------|-------|--------|
| #65 | Cannot submit POLY_1271 orders — `create_or_derive_api_key` binds API key to EOA, not deposit wallet | 2026-05-17 |
| #98 | signature_type=3 (POLY_1271) cannot post orders: "the order signer address has to be the address of the API KEY" | 2026-07-03 |

**Note:** These closures are disputed. Users continued reporting identical errors through at least August 2026 (see clob-client-v2 #65 below).

### Issues still open

**py-clob-client-v2:**
- https://github.com/Polymarket/py-clob-client-v2/issues/56 — "maker address not allowed" (Magic.link proxy)
- https://github.com/Polymarket/py-clob-client-v2/issues/57 — POLY_1271 / Privy architecture mismatch
- https://github.com/Polymarket/py-clob-client-v2/issues/61 — "Maker address not allowed" (new MetaMask)
- https://github.com/Polymarket/py-clob-client-v2/issues/64 — POLY_1271 signer vs API key error
- https://github.com/Polymarket/py-clob-client-v2/issues/70 — L1 auth binds API key to EOA (not deposit wallet)
- https://github.com/Polymarket/py-clob-client-v2/issues/75 — POLY_1271 deposit-wallet orders rejected

**clob-client-v2 (upstream TypeScript SDK):**
- https://github.com/Polymarket/clob-client-v2/issues/65 — **STILL OPEN** as of 2026-10-22. Staff comment (May 2026): "There's nothing to solve." Users disputed this through August 2026.

**Bottom line:** The core auth bug is unresolved in py-clob-client-v2, which is why Polymarket archived the package.

---

## Resolution path

Polymarket deprecated py-clob-client-v2 and directed all users to the unified **`polymarket-client`** SDK.

- Migration guide: https://docs.polymarket.com/migrate/clob-sdk-to-unified-sdk
- New package: `pip install polymarket-client`
- New repo: https://github.com/Polymarket/py-sdk

**Next step:** Migrate `executor.py` to `polymarket-client`. The unified SDK handles POLY_1271/signature_type=3 deposit wallet flows. Test with `DRY_RUN=true` before going live.

Do NOT attempt to upgrade within py-clob-client-v2 — the POLY_1271 auth bug is unresolved there and the package is archived.
