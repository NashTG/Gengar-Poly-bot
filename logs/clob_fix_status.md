# CLOB Fix Status — 2026-10-18 (updated; first detected 2026-10-17)

## Summary

Multiple new releases of `py-clob-client-v2` have shipped since v1.0.1, and the package has been **deprecated** in favour of the new unified `polymarket-client` SDK.

---

## What changed

| Item | Detail |
|------|--------|
| **New releases** | v1.0.2 (2026-07-02), v1.1.0 (2026-07-17), v1.2.0 (2026-09-25), v1.2.1 (2026-10-15) |
| **Relevant merged PR** | [#39 – feat: add deposit wallet order support](https://github.com/Polymarket/py-clob-client-v2/pull/39) (merged 2026-05-01, shipped in v1.0.1) — adds POLY_1271 / signature_type=3 signer support to `OrderBuilder` |
| **Package deprecated** | [v1.2.1](https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.2.1) carries a deprecation notice: *"This package is deprecated. Please migrate to the unified Polymarket Python SDK (`polymarket-client`)."* PR [#78](https://github.com/Polymarket/py-clob-client-v2/pull/78) added a README recommendation for the new SDK (merged 2026-05-25). |
| **Issue status** | Issues [#75](https://github.com/Polymarket/py-clob-client-v2/issues/75) and [#76](https://github.com/Polymarket/py-clob-client-v2/issues/76) remain **OPEN**. The original `create_or_derive_api_key` / EOA-binding bug has **not** been officially fixed in py-clob-client-v2; community workaround: derive API credentials from a client already configured with `signature_type=3` and `funder`. |

---

## Community workaround (from issue #75, Aug 2026)

Configure the CLOB client with `signature_type=3` and `funder=<deposit_wallet>` **before** calling `create_or_derive_api_key()`. The key is then bound to the deposit wallet address rather than the EOA.

---

## Next step

**Migrate to `polymarket-client`** (unified Polymarket Python SDK) — the official long-term fix path.  
Alternatively, if staying on py-clob-client-v2, upgrade to v1.2.1 and apply the community workaround above, then re-test `executor.py` with `DRY_RUN=false`.
