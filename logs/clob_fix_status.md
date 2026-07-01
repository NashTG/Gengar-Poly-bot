# CLOB Fix Status Monitor — 2026-07-01

## Overall Verdict

**No direct fix in py-clob-client-v2.** All tracked issues remain open, still on v1.0.1.

**`polymarket-client` (py-sdk) is now at v0.1.0b11 (June 29, 2026)** — 4 releases since the last report (b7 → b11). The deposit-wallet default introduced in b4 remains the fix path; b11 includes "clean up deposit wallet deployment" and RPC batch handling fixes, improving stability.

---

## New Since Last Report (2026-06-16)

### py-sdk b8 → b11 released
Four new releases since the last report:

| Tag | Date | Notable change |
|-----|------|----------------|
| v0.1.0-b8 | Jun 17, 2026 | Support protected market orders; add `parent_event_id` to event models |
| v0.1.0-b9 | Jun 19, 2026 | (see GitHub release notes) |
| v0.1.0-b10 | Jun 23, 2026 | (see GitHub release notes) |
| **v0.1.0-b11** | **Jun 29, 2026** | **"clean up deposit wallet deployment"**; RPC batch handling fixes; type validation corrections |

b11 is the current install target: `pip install polymarket-client==0.1.0b11`

### py-clob-client-v2 — no change
Still at v1.0.1 (May 9, 2026). All 11 tracked issues remain open. No auth-fixing PRs merged. No staff comments on #70, #75, #76.

---

## Reference: Original Fix Discovery (2026-05-27 / 2026-06-08)

### py-sdk v0.1.0-b4 — "default secure clients to deposit wallet" (2026-06-08)
- **Repo:** https://github.com/Polymarket/py-sdk
- **Changelog entry:** `"default secure clients to deposit wallet"`
- **Significance:** This is the direct fix to the auth bug. `SecureClient.create()` now accepts a `wallet` parameter that defaults to the signer's current Deposit Wallet. Users no longer need to manually specify `signature_type=3` / POLY_1271 — the SDK handles it.

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

## Tracked Issue Status (as of 2026-07-01)

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
pip install polymarket-client==0.1.0b11
```

Key migration points for `executor.py`:
1. Replace `ClobClient` + `create_or_derive_api_key()` with `SecureClient.create(private_key=..., nonce=0)` — deposit wallet binding is automatic.
2. Replace `create_order(OrderArgs(...))` with `SecureClient` order placement API.
3. Verify the complement engine routing and integer-shares / 2-decimal-price constraints still hold (the decimal precision bug may need re-checking in the new SDK).
4. Test with small bankroll ($5 bet) before restoring full BANKROLL.

**Note:** py-sdk is still Beta (v0.1.0-b11). Check Polymarket/py-sdk issues for any order-rejection bugs before live deployment. The "clean up deposit wallet deployment" note in b11 is a positive signal that this path is stabilising.
