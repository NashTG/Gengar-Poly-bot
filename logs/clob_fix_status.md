# CLOB Fix Status Monitor — last updated 2026-07-04

## Overall Verdict

**No direct fix in py-clob-client-v2.** All 11 tracked issues remain open.

**`polymarket-client` (py-sdk) remains the only working path.** Latest: v0.1.0b13 (Jul 3, 2026).

---

## New Since Last Report (2026-07-02 → 2026-07-04)

### py-sdk advanced to v0.1.0-b13 (2026-07-03)
- **b12** (2026-07-02): "require 3 minute GTD expirations" — order timing fix
- **b13** (2026-07-03): "require 3 minute GTD expirations" — additional cleanup
- No auth-related changelog entries in either release
- Install target updated below to b13

### Issue #98 self-closed by reporter (2026-07-03)
- Title: "signature_type=3 (POLY_1271) cannot post orders: 'the order signer address has to be the address of the API KEY'"
- Closed by original poster; brief exchange confirms they resolved it ("Yep")
- **Not an official Polymarket fix.** Reporter likely migrated to py-sdk or found a workaround.

### py-clob-client-v2 — no auth changes
- v1.0.2 (released 2026-07-02) was tick sizes only — already captured in prior report
- No new merged PRs touching create_or_derive_api_key, l1_auth, or deposit wallet
- No tracked issues closed by Polymarket

---

## Reference: Fix Path (established 2026-05-27 / confirmed 2026-06-08)

### `polymarket-client` py-sdk — the actual fix

**py-sdk v0.1.0-b4** introduced "default secure clients to deposit wallet" — directly resolving the API key binding bug. All releases through b13 build on this.

```bash
pip install polymarket-client==0.1.0b13
```

`SecureClient.create()` binds the API key to the deposit wallet automatically:
```python
SecureClient.create(
    private_key,
    wallet=None,         # defaults to signer's current Deposit Wallet
    environment=...,
    credentials=...,     # skip re-derivation if you have existing creds
    nonce=...,
)
```

---

## Tracked Issue Status (as of 2026-07-04)

All issues still **OPEN** in py-clob-client-v2:

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

## py-clob-client-v2 Release History

| Tag | Date | Notes |
|-----|------|-------|
| **v1.0.2** | **Jul 2, 2026** | Tick sizes 0.005 / 0.0025 only — NO auth fix |
| v1.0.1 | May 9, 2026 | Previous latest |

---

## py-sdk Release History (recommended fix path)

| Tag | Date | Notes |
|-----|------|-------|
| v0.1.0-b13 | Jul 3, 2026 | GTD expiration cleanup — latest |
| v0.1.0-b12 | Jul 2, 2026 | Require 3-min GTD expirations |
| v0.1.0-b11 | Jun 29, 2026 | "clean up deposit wallet deployment" |
| v0.1.0-b10 | Jun 26, 2026 | — |
| v0.1.0-b9  | Jun 22, 2026 | — |

---

## Next Step

**Upgrade to `polymarket-client` and re-test executor.py with `DRY_RUN=false`**

```bash
pip install polymarket-client==0.1.0b13
```

Key migration points for `executor.py`:
1. Replace `ClobClient` + `create_or_derive_api_key()` with `SecureClient.create(private_key=..., nonce=0)` — deposit wallet binding is automatic.
2. Replace `create_order(OrderArgs(...))` with `SecureClient` order placement API.
3. Re-verify the integer-shares / 2-decimal-price constraint (decimal precision bug from v10 may resurface in new SDK).
4. Test with small bankroll ($5 bet) before restoring full BANKROLL.

**Note:** py-sdk is still Beta (v0.1.0-b13). Check Polymarket/py-sdk issues before live deployment.
