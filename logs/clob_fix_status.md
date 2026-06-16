# CLOB Fix Status Monitor — 2026-06-16

## Overall Verdict

**No direct fix in py-clob-client-v2.** All tracked issues remain open, still on v1.0.1.

**NEW (since 2026-05-27): DEPOSIT WALLET DEFAULT LANDED IN py-sdk v0.1.0-b4.**  
The new `polymarket-client` SDK now defaults its `SecureClient` to the deposit wallet (`wallet` param = signer's current Deposit Wallet). This is the functional fix for the `create_or_derive_api_key`/EOA-binding bug — delivered via the new SDK rather than as a patch to py-clob-client-v2.

---

## New Since Last Report (2026-05-27)

### py-sdk v0.1.0-b4 — "default secure clients to deposit wallet" (2026-06-08)
- **Repo:** https://github.com/Polymarket/py-sdk
- **Changelog entry:** `"default secure clients to deposit wallet"`
- **Significance:** This is the direct fix to the auth bug. `SecureClient.create()` now accepts a `wallet` parameter that defaults to the signer's current Deposit Wallet. Users no longer need to manually specify `signature_type=3` / POLY_1271 — the SDK handles it.

### py-sdk release timeline (all post May-27)
| Tag | Date | Notable change |
|-----|------|----------------|
| v0.1.0-b4 | Jun 8, 2026 | **"default secure clients to deposit wallet"** |
| v0.1.0-b5 | Jun 9, 2026 | Combo position lifecycle, async RFQ sessions |
| v0.1.0-b6 | Jun 10, 2026 | Combo market catalog, RFQ submission fixes |
| **v0.1.0-b7** | **Jun 10, 2026** | Bug fix: point Combos RFQ endpoints at polymarket.com |

### SecureClient API (confirmed from source)
```python
SecureClient.create(
    private_key,
    wallet=None,         # defaults to signer's current Deposit Wallet
    environment=...,
    credentials=...,     # existing API credentials (skip derivation)
    nonce=...,           # credential derivation nonce
)
```
The `wallet` parameter defaulting to the deposit wallet means the API key is now bound to the correct address — exactly the fix the tracked issues demanded.

### New py-clob-client-v2 issues (bug still widespread)
Issues #77–#92 opened since May 27, all reporting the same POLY_1271/deposit wallet rejection. Confirms py-clob-client-v2 itself is still broken; migration to py-sdk is the only resolution path.

---

## Tracked Issue Status (as of 2026-06-16)

All issues still **OPEN** in py-clob-client-v2 (no staff comments, no closures):

| Issue | Title | State |
|-------|-------|-------|
| #55 | POLY_1271: order signer always set to EOA instead of funder | Open |
| #56 | Order placement 400 for Magic.link proxy wallets | Open |
| #57 | Cannot place sigtype=3 (POLY_1271 / Magic Wallet) orders | Open |
| #58 | How should CLOB API credentials be bound for deposit wallet? | Open |
| #61 | "maker address not allowed" for new MetaMask accounts | Open |
| #63 | [BUG] post_order rejected for new MetaMask deposit wallet accounts | Open |
| #64 | POLY_1271 + Deposit Wallet: signer != api_key despite matching | Open |
| #70 | POLY_1271 (sig type 3) order placement fails | Open |
| #71 | POLY_1271 orders fail | Open |
| #75 | POLY_1271 deposit-wallet orders rejected | Open |
| #76 | CLOB V2 Python SDK unusable for deposit wallets | Open |

**clob-client-v2 #65** (TypeScript SDK): Still **Open**

---

## py-clob-client-v2 Release Status

| Tag | Date | Notes |
|-----|------|-------|
| **v1.0.1** | May 9, 2026 | **Latest — no change** |

No release > v1.0.1. No auth-fixing PRs merged.

---

## Previous Report Reference

2026-05-27 run captured: PR #78 merged (Polymarket staff deprecated py-clob-client-v2 in favour of py-sdk). py-sdk was at v0.1.0-b3 at that point with deposit wallet support unverified.

---

## Next Step

**Upgrade to `polymarket-client` and re-test executor.py with `DRY_RUN=false`**

```bash
pip install polymarket-client==0.1.0b7
```

Key migration points for `executor.py`:
1. Replace `ClobClient` + `create_or_derive_api_key()` with `SecureClient.create(private_key=..., nonce=0)` — deposit wallet binding is automatic.
2. Replace `create_order(OrderArgs(...))` with `SecureClient` order placement API.
3. Verify the complement engine routing and integer-shares / 2-decimal-price constraints still hold (the decimal precision bug may need re-checking in the new SDK).
4. Test with small bankroll ($5 bet) before restoring full BANKROLL.

**Note:** py-sdk is still Beta (v0.1.0-b7). Check Polymarket/py-sdk issues for any v0.1.0 order-rejection bugs before live deployment.
