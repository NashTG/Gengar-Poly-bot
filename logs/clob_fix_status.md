# CLOB Fix Status Monitor — 2026-07-02

## Overall Verdict

**No direct fix in py-clob-client-v2.** All tracked issues remain open.

**NEW TODAY**: py-clob-client-v2 released **v1.0.2** (2026-07-02) — tick size support only, NOT the auth fix.

**`polymarket-client` (py-sdk) remains the only working path.** Last known good: v0.1.0b11 (Jun 29, 2026).

---

## New Since Last Report (2026-07-01)

### py-clob-client-v2 v1.0.2 released (2026-07-02)
- **Repo:** https://github.com/Polymarket/py-clob-client-v2
- **Release tag:** v1.0.2
- **Change:** "Add support for CLOB tick sizes `0.005` and `0.0025`. Bump package version to `1.0.2`."
- **Auth fix?** NO. EIP-7702, POLY_1271, deposit wallet, create_or_derive_api_key, l1_auth — **none addressed.**
- **Verdict:** Do NOT upgrade expecting auth fix. v1.0.2 is safe to install if tick size support is needed, but the fundamental "order signer has to be the address of the API KEY" rejection will persist.

### py-clob-client-v2 tracked issues — all still OPEN
No closures. No auth-fixing PRs merged (PR #95 = tick sizes, PR #96 = version bump).

### Issue #70 — new community comments (as of Jun 30, 2026)
- **NSA013** (Jun 30): Confirms bug affects sig_type=1 too; "no working path exists" for programmatic trading via py-clob-client-v2
- **pmcr9367** (Jun 17): Implemented ERC-7739 TypedDataSign wrapper patch locally; reported success — but requires local SDK modification
- Community consensus: migrate to `polymarket-client` is the only clean path

### py-sdk — no new releases since b11
Last known: v0.1.0-b11 (Jun 29, 2026), "clean up deposit wallet deployment".

---

## Reference: Fix Path (established 2026-05-27 / confirmed 2026-06-08)

### `polymarket-client` py-sdk — the actual fix

**py-sdk v0.1.0-b4** introduced "default secure clients to deposit wallet" — directly resolving the API key binding bug. All releases through b11 build on this. Install target:

```bash
pip install polymarket-client==0.1.0b11
```

`SecureClient.create()` now binds the API key to the deposit wallet automatically:
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

## Tracked Issue Status (as of 2026-07-02)

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
| **v1.0.2** | **Jul 2, 2026** | **Tick sizes 0.005 / 0.0025 only — NO auth fix** |
| v1.0.1 | May 9, 2026 | Previous latest |

---

## Next Step

**Upgrade to `polymarket-client` and re-test executor.py with `DRY_RUN=false`**

```bash
pip install polymarket-client==0.1.0b11
```

Key migration points for `executor.py`:
1. Replace `ClobClient` + `create_or_derive_api_key()` with `SecureClient.create(private_key=..., nonce=0)` — deposit wallet binding is automatic.
2. Replace `create_order(OrderArgs(...))` with `SecureClient` order placement API.
3. Re-verify the integer-shares / 2-decimal-price constraint (decimal precision bug from v10 may resurface in new SDK).
4. Test with small bankroll ($5 bet) before restoring full BANKROLL.

**Note:** py-sdk is still Beta (v0.1.0-b11). The repeated "deposit wallet" cleanup across b-releases suggests this path is stabilising but not yet GA. Check Polymarket/py-sdk issues before live deployment.
