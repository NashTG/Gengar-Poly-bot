# CLOB Fix Status Monitor — last updated 2026-08-05

## Overall Verdict

**No direct fix in py-clob-client-v2.** All 11 tracked issues remain open.

**`polymarket-client` (py-sdk) is now at v0.3.0 STABLE (Aug 4).** This is the only working fix path for deposit wallet / POLY_1271 order signing. Recommended install: `pip install polymarket-client==0.3.0`.

---

## New Since Last Report (2026-08-04 → 2026-08-05)

### py-sdk v0.3.0 STABLE released August 4, 2026

- Graduated from v0.3.0b2 (pre-release) to **stable v0.3.0**.
- Changes over v0.2.0 (the previous stable): includes b1 + b2 improvements — "self-heal deposit wallet nonce on submit rejection", Chainlink TWAP subscriptions, perps fills pagination, `DEPOSIT`/`WITHDRAWAL` activity types, `retry_after` on `RequestRejectedError`.
- **No new auth changes** in v0.3.0 vs b2. Deposit wallet binding via `SecureClient.create()` remains intact.
- **Updated install command**: `pip install polymarket-client==0.3.0`

### py-clob-client-v2: No changes

- Still v1.1.0. Two new unrelated issues filed (#107 Aug 4, #108 Aug 5 — not auth-related).
- All 11 tracked auth issues remain open. No staff comments on #70, #75, #76.

---

## New Since Last Report (2026-08-01 → 2026-08-04)

### py-clob-client-v2: No changes

- Still v1.1.0. Now **57 open issues** (up from ~53 on Jul 18).
- Three new auth-related issues filed since last report:
  - **#103** (Jul 19): "Deposit wallet rejects exported EOA signatures — investigate signature_type=3 validation and CLOB auth flow"
  - **#104** (Jul 22): "POLY_PROXY order signature rejected as invalid...POLY_1271 rejects as invalid signer address"
  - **#105** (Aug 1): "get_balance_allowance() returns balance=0, allowance=0 for signature_type=1 (POLY_PROXY) despite funder wallet holding real pUSD"
- All 11 originally tracked auth issues remain open.
- No staff comments on #70, #75, #76.

### py-sdk (polymarket-client): No new releases

- Still v0.3.0b2 (Jul 31). No stable v0.3.0 yet.
- Deposit wallet binding via `SecureClient.create()` remains the only working fix path.

---

## New Since Last Report (2026-07-25 → 2026-08-01)

### py-sdk v0.3.0b2 (Jul 31, 2026)

- "self-heal deposit wallet nonce on submit rejection" — deposit wallet reliability improvement
- `TAKER_REBATE`, `DEPOSIT`, `WITHDRAWAL` activity types added

### py-sdk v0.3.0b1 (Jul 29, 2026)

- Chainlink TWAP subscriptions support
- Perps fills pagination with native cursor and sorting
- Account notifications in perps session reads/events
- Granular quote validation errors for RFQ
- Exposed `retry_after` on `RequestRejectedError`

**No auth or deposit wallet breaking changes in either beta. Deposit wallet binding via `SecureClient.create()` remains intact.**

### py-clob-client-v2: No changes

- Still v1.1.0. All 11 tracked auth issues remain open. No staff comments on #70, #75, #76.

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

## Tracked Issue Status (as of 2026-08-04)

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
| **v0.3.0** | **Aug 4, 2026** | STABLE — includes all b1+b2 changes; deposits/withdrawals in list_activity by default — NO auth change |
| v0.3.0b2 | Jul 31, 2026 | self-heal deposit wallet nonce on submit rejection; new activity types — NO auth change |
| v0.3.0b1 | Jul 29, 2026 | Chainlink TWAP, perps fills pagination, account notifications, quote validation — NO auth change |
| v0.2.0 | Jul 24, 2026 | Collateral return, order settlement wait, perps fee tiers, pagination fixes — NO auth change |
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

**Upgrade to `polymarket-client` (stable v0.3.0) and re-test executor.py with `DRY_RUN=false`**

```bash
pip install polymarket-client==0.3.0        # latest stable (nonce self-healing included)
```

Key migration points for `executor.py`:
1. Replace `ClobClient` + `create_or_derive_api_key()` with `SecureClient.create(private_key=..., nonce=0)` — deposit wallet binding is automatic.
2. Replace `create_order(OrderArgs(...))` with `SecureClient` order placement API.
3. Re-verify the integer-shares / 2-decimal-price constraint (decimal precision bug from v10 may resurface in new SDK).
4. Test with small bankroll ($5 bet) before restoring full BANKROLL.
