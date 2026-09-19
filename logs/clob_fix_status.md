# CLOB Fix Status — 2026-09-19

## TL;DR

New releases exist (v1.0.2, v1.1.0) but **neither fixes the POLY_1271 deposit-wallet auth bug**.
All tracked issues remain open. Polymarket's official response appears to be redirecting users to a new unified SDK (`Polymarket/py-sdk`).

---

## What Changed

### New releases (both newer than v1.0.1)

| Release | Date | What it fixes | Fixes auth bug? |
|---------|------|---------------|-----------------|
| **v1.0.2** | 2026-07-02 | Adds CLOB tick sizes 0.005 and 0.0025 | ❌ No |
| **v1.1.0** | 2026-07-17 | Async execution / tradeID handling (server now returns tradeIDs instead of transactionHashes) | ❌ No |

Links:
- https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.0.2
- https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.1.0

### Merged PRs

| PR | Title | Date | Relevant? |
|----|-------|------|-----------|
| #39 | feat: add deposit wallet order support | 2026-05-01 | Partial — adds POLY_1271 signing path for orders but does NOT fix `create_or_derive_api_key` L1 auth binding |
| #78 | docs: recommend new unified py-sdk in README | 2026-05-25 | Notable — official redirect to `Polymarket/py-sdk` |
| #96 | version: 1.0.2 | 2026-07-02 | No |
| #101 | refactor: resolve transaction hashes internally | 2026-07-17 | No |

**No merged PR touches `create_or_derive_api_key`, `create_l1_headers`, or the EOA→deposit-wallet API-key binding path.**

---

## Tracked Issues Status

| Issue | Repo | Status | Notes |
|-------|------|--------|-------|
| #55 | py-clob-client-v2 | Open | Not confirmed closed in search results |
| #56 | py-clob-client-v2 | Open | Not confirmed closed |
| #57 | py-clob-client-v2 | Open | Not confirmed closed |
| #58 | py-clob-client-v2 | Open | Not confirmed closed |
| #61 | py-clob-client-v2 | Open | Not confirmed closed |
| #63 | py-clob-client-v2 | Open | Not confirmed closed |
| #64 | py-clob-client-v2 | Open | Not confirmed closed |
| #70 | py-clob-client-v2 | **Open** | Confirmed. No Polymarket staff comments. |
| #71 | py-clob-client-v2 | Open | Not confirmed closed |
| #75 | py-clob-client-v2 | **Open** | Confirmed. No Polymarket staff comments. |
| #76 | py-clob-client-v2 | **Open** | Confirmed. No Polymarket staff comments. |
| #65 | clob-client-v2 | **Open** | Confirmed. No Polymarket staff comments. Only Rust SDK reportedly works. |

No Polymarket org members (JonathanAmenechi, suhailkakar) have commented on issues 70, 75, or 76.

---

## Notable: New Unified SDK

PR #78 (merged 2026-05-25) adds a README note pointing new projects to **`Polymarket/py-sdk`** (REST + WebSockets unified).
This appears to be Polymarket's strategic response — deprecate py-clob-client-v2 in favor of a new SDK that may handle deposit-wallet auth correctly.

**Action recommended**: Check `https://github.com/Polymarket/py-sdk` for POLY_1271 deposit wallet support before the next upgrade cycle.

---

## The Bug (unchanged)

`create_or_derive_api_key()` signs L1 auth using the EOA address regardless of `signature_type=POLY_1271` and `funder=deposit_wallet` config. This binds the API key to the EOA, while orders correctly set `signer=deposit_wallet`, producing:

```
HTTP 400 {"error": "the order signer address has to be the address of the API KEY"}
```

The v13 bot uses `signature_type=2` (Safe/proxy) not POLY_1271, so it is on the **legacy path** that Polymarket is phasing out. Monitor for "maker address not allowed" errors as the migration enforcement date approaches.

---

## Next Steps

1. **Check `Polymarket/py-sdk`** — this new unified SDK may be the fix vehicle. If it handles POLY_1271 deposit wallets correctly, evaluate migrating executor.py to it.
2. **Upgrade py-clob-client-v2 to v1.1.0** and re-test executor.py with `DRY_RUN=false` (v1.1.0 changes tradeID handling — verify `create_order` response parsing still works correctly in bot.py).
3. Continue monitoring weekly — no Polymarket staff engagement on auth issues yet.
