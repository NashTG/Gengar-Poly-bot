# CLOB Fix Status Monitor — last updated 2026-07-25

## Overall Verdict

**No direct fix in py-clob-client-v2.** All 11 tracked issues remain open.

**`polymarket-client` (py-sdk) is now at v0.2.0 (Jul 24).** This is the only working fix path for deposit wallet / POLY_1271 order signing. Deposit wallet auth fix intact since b4.

---

## New Since Last Report (2026-07-23 → 2026-07-25)

### py-sdk v0.2.0 released July 24, 2026

New features and fixes — **no auth changes; deposit wallet binding intact**:

- `add collateral return plan/execute to secure clients` (new SecureClient methods)
- `add wait_for_order_settlement` for async order settlement
- `add fee tiers to perps fee schedule` (model definitions)
- `add isolated_only to perps instrument` parameter
- Pagination fixes: cap page_size on gamma offset-paginated endpoints, frame truncation fix
- `parse zero GTC expiration as None in OpenOrder` (#191)
- Perps: failed withdrawal status, unknown statuses passed through as strings

```bash
pip install polymarket-client==0.2.0
```

### py-clob-client-v2: No changes

- Still v1.1.0 (Jul 17). All 11 tracked auth issues remain open. No staff comments on #70, #75, #76.

---

## New Since Last Report (2026-07-18 → 2026-07-23)

### polymarket-client v0.1.0 STABLE released July 22, 2026

The py-sdk graduated from beta (b21) to **stable v0.1.0** — the deposit wallet fix path is now production-ready.

```bash
pip install polymarket-client==0.1.0
```

Changes in v0.1.0 stable:
- `condition_id` alias added to CLOB models (`market` field deprecated)
- Typed cancellation result order IDs with `OrderId`
- Stream handling improved: drops unknown frames without closing connections
- Tick-size price validation: rejects prices not a multiple of tick size

SecureClient deposit wallet binding (introduced in b4) **remains intact**.

### py-clob-client-v2: No changes

- Still v1.1.0. All 11 tracked auth issues remain open. No staff comments on #70, #75, #76.

---

## New Since Last Report (2026-07-17 → 2026-07-18)

### No new py-clob-client-v2 release today

- Still on v1.1.0 (released Jul 17). No auth fix. Issues #70, #75, #76 still open.
- 53 open issues total on the repo; all 11 tracked auth issues remain unresolved.

### py-sdk advanced to v0.1.0-b21 (2026-07-17, same day as b20)

- **b21** (Jul 17): Stop approving retired neg-risk adapter in trading setup (#179) — minor relayer fix, NOT auth-related
- The deposit wallet fix (via `SecureClient.create()`) introduced in b4 remains intact through b21

### Prior reference (established 2026-07-17)

- **py-clob-client-v2 v1.1.0** (Jul 17): Async execution — tradeIDs instead of txHashes (handled internally). No auth fix.
- **py-sdk v0.1.0-b20** (Jul 17): TokenId-keyed batch price reads, websocket improvements, Perps frames.

---

## Reference: Fix Path (established 2026-05-27 / confirmed 2026-06-08)

### `polymarket-client` py-sdk — the actual fix

**py-sdk v0.1.0-b4** introduced "default secure clients to deposit wallet" — directly resolving the API key binding bug. Now stable at v0.1.0.

```bash
pip install polymarket-client==0.1.0
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

## Tracked Issue Status (as of 2026-07-23)

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
| **v1.1.0** | **Jul 17, 2026** | Async execution: tradeIDs instead of txHashes (handled internally) — NO auth fix |
| v1.0.2 | Jul 2, 2026 | Tick sizes 0.005 / 0.0025 only — NO auth fix |
| v1.0.1 | May 9, 2026 | Added deposit wallet order signing (bug still in L1 auth) |

---

## py-sdk Release History (recommended fix path)

| Tag | Date | Notes |
|-----|------|-------|
| **v0.2.0** | **Jul 24, 2026** | Collateral return, order settlement wait, perps fee tiers, pagination fixes — NO auth change |
| v0.1.0 | Jul 22, 2026 | STABLE — condition_id alias, typed OrderIds, stream fixes, tick-size validation |
| v0.1.0-b21 | Jul 17, 2026 | Stop approving retired neg-risk adapter |
| v0.1.0-b20 | Jul 17, 2026 | TokenId-keyed batch price reads, Perps frames |
| v0.1.0-b19 | Jul 13, 2026 | RESOLVED_PARTIAL ComboPositionStatus fix |
| v0.1.0-b18 | Jul 10, 2026 | Websocket fixes, Combo activity parse |
| v0.1.0-b17 | Jul 10, 2026 | Combo data pagination, typed overloads |
| v0.1.0-b15 | Jul 7, 2026 | Perpetuals trading support |
| v0.1.0-b14 | Jul 7, 2026 | Builder-API-key management, multi-position merge, examples |
| v0.1.0-b13 | Jul 3, 2026 | GTD expiration cleanup |
| v0.1.0-b12 | Jul 2, 2026 | Require 3-min GTD expirations |
| v0.1.0-b11 | Jun 29, 2026 | "clean up deposit wallet deployment" |
| v0.1.0-b10 | Jun 26, 2026 | — |
| v0.1.0-b9  | Jun 22, 2026 | — |

---

## Next Step

**Upgrade to `polymarket-client` v0.2.0 and re-test executor.py with `DRY_RUN=false`**

```bash
pip install polymarket-client==0.2.0
```

Key migration points for `executor.py`:
1. Replace `ClobClient` + `create_or_derive_api_key()` with `SecureClient.create(private_key=..., nonce=0)` — deposit wallet binding is automatic.
2. Replace `create_order(OrderArgs(...))` with `SecureClient` order placement API.
3. Re-verify the integer-shares / 2-decimal-price constraint (decimal precision bug from v10 may resurface in new SDK).
4. Test with small bankroll ($5 bet) before restoring full BANKROLL.
