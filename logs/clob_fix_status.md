# CLOB SDK Fix Status

## Date found: 2026-10-20

## CRITICAL: py-clob-client-v2 is NOW DEPRECATED

`py-clob-client-v2` v1.2.1 (released 2026-10-15) adds a deprecation notice:
> "This package is deprecated. Please migrate to the unified Polymarket Python SDK (`polymarket-client`)."

Migration guide: https://docs.polymarket.com/migrate/clob-sdk-to-unified-sdk

---

## What changed since last check (was v1.0.1)

| Release | Date | What's in it |
|---------|------|-------------|
| v1.0.2 | 2026-07-02 | Unknown (minor) |
| v1.1.0 | 2026-07-17 | Refactor: resolve transaction hashes internally |
| v1.2.0 | 2026-09-25 | **feat: PolyV2 position orders + Exchange V3 signing** (PR #119) |
| v1.2.1 | 2026-10-15 | DEPRECATION NOTICE — package deprecated, points to polymarket-client |

### PR #119 — "feat: support PolyV2 position orders" (merged 2026-09-25)
- https://github.com/Polymarket/py-clob-client-v2/pull/119
- Adds V3 signature support including deposit-wallet signatures
- Adds configurable EIP-712 domain version
- **This may partially address the deposit-wallet signing issue**, but was framed as a feature, not the full auth bugfix

---

## Tracked issue status (as of 2026-10-20)

All tracked issues (55, 56, 57, 58, 61, 63, 64, 70, 71, 75, 76) on py-clob-client-v2 are **still OPEN**.

The auth bug was NOT fixed in py-clob-client-v2. Instead, Polymarket deprecated the package entirely and moved to a new unified SDK.

---

## New unified SDK: polymarket-client

- PyPI package: `polymarket-client` (install: `pip install polymarket-client`)
- GitHub: https://github.com/Polymarket (look for py-sdk repo)
- Currently in **beta**
- Uses `createSecureClient({ wallet, signer })` — may handle deposit wallets correctly
- Official Python SDK going forward

---

## Community workaround (working now)

A community starter repo implements deposit-wallet auth (POLY_1271/SIG_TYPE=3) correctly:
- https://github.com/dcpf1/polymarket-v2-starter
- Implements: deposit-wallet auth, order placement with double-fill trap avoidance, fill confirmation, redemption

---

## Next steps

1. **DO NOT wait for a fix in py-clob-client-v2** — it is deprecated and will not receive the auth fix
2. Evaluate `polymarket-client` (new unified SDK) — test if POLY_1271/deposit-wallet auth works
3. Review https://github.com/dcpf1/polymarket-v2-starter as a working reference implementation
4. Update `executor.py` to use the new SDK or the community auth pattern
5. Test with `DRY_RUN=true` first, then live with small bankroll

**Action: Upgrade to `polymarket-client` and re-test executor.py with MANUAL_MODE=false**
