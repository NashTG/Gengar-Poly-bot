# CLOB Fix Status — 2026-09-03 (updated; originally 2026-09-01)

## Summary

Polymarket has **not fixed** the deposit-wallet auth bug in `py-clob-client-v2`. Instead, they have released a new unified SDK — `Polymarket/py-sdk` — which appears to resolve the issue and is now the recommended migration path.

---

## py-clob-client-v2 Status (No Direct Fix)

Two releases since the monitoring baseline (v1.0.1, 2026-05-09):

| Release | Date | What changed |
|---------|------|--------------|
| v1.0.2 | 2026-07-02 | Added CLOB tick sizes 0.005 and 0.0025 |
| v1.1.0 | 2026-07-17 | Async: `POST /order` now returns `tradeIDs`; client resolves `transactionHashes` internally |

**Neither release fixes the EIP-7702 deposit-wallet API-key derivation bug.**

### Tracked issue states (as of 2026-09-01)

- Issue #57 — **OPEN**: Privy TSS / Magic Wallet incompatibility
- Issue #70 — **OPEN**: "L1 auth always binds API key to EOA, never the deposit wallet"
- Issue #71 — **OPEN**: POLY_1271 orders fail with "order signer address has to be the address of the API KEY"
- Issue #75 — **OPEN**: "POLY_1271 deposit-wallet orders rejected: signer != API KEY"
- Issue #76 — **OPEN**: "CLOB V2 Python SDK unusable for deposit wallets"
- clob-client-v2 #65 — **OPEN**: "Cannot submit POLY_1271 orders — create_or_derive_api_key binds key to EOA"

Zero Polymarket staff responses visible on #70, #75, or #76.

### Notable merged PRs (py-clob-client-v2)

- **PR #39** (merged 2026-05-01): "feat: add deposit wallet order support" — added POLY_1271 order *signing* in OrderBuilder. **Partial fix only**: order signing works, but API key *derivation* (`create_or_derive_api_key`) still binds to EOA. Issues were opened after this merge.
  - https://github.com/Polymarket/py-clob-client-v2/pull/39

- **PR #78** (merged 2026-05-25): "docs: recommend new unified py-sdk in README" — Polymarket is signaling they won't fix this in py-clob-client-v2 directly.
  - https://github.com/Polymarket/py-clob-client-v2/pull/78

---

## KEY FINDING: Polymarket/py-sdk is the actual fix path

Polymarket released a new unified SDK that combines all REST APIs and WebSockets into one package:

- Repo: https://github.com/Polymarket/py-sdk
- **Latest release: v0.7.1** (2026-08-28) — actively maintained, confirmed deposit wallet flow functional
- v0.3.0-b2 explicitly includes: "self-heal deposit wallet nonce on submit rejection" — confirms deposit wallet flow is functional
- No open issues about POLY_1271, EIP-7702, or API key binding

### py-sdk release history (relevant versions)

| Version | Date | Notable |
|---------|------|---------|
| v0.7.1 | 2026-08-28 | Session key expiration bug fixes (default expiration, restore expiration buffer) |
| v0.7.0 | 2026-08-26 | Scoped session keys, typed trading restrictions |
| v0.6.0 | 2026-08-13 | Requester-side combo RFQ support |
| v0.3.0-b2 | 2026-07-31 | Deposit wallet nonce self-healing |
| v0.1.0 | 2026-07-22 | First stable release |

### What this means for PolyBot

`py-clob-client-v2` is effectively in maintenance mode for this bug. The fix is to **migrate executor.py to Polymarket/py-sdk**.

---

## v1.1.0 Breaking Change Risk (if staying on py-clob-client-v2)

`POST /order` now returns `tradeIDs` instead of `transactionHashes`. Check `executor.py`'s order verification logic — if it reads `transactionHashes` from the response, the upgrade breaks verification.

---

## Next Step

**Upgrade py-clob-client-v2 and re-test executor.py with MANUAL_MODE=false**, or better:

**Migrate to `Polymarket/py-sdk` v0.7.1** rather than upgrading py-clob-client-v2:
1. `pip install polymarket-client==0.7.1` (verify package name from py-sdk pyproject.toml)
2. Rewrite `executor.py` authentication to use py-sdk's deposit-wallet flow
3. Confirm deposit-wallet API key derivation uses the deposit wallet address (not EOA)
4. Test with `DRY_RUN=true`, then `DRY_RUN=false` with MIN_BET=5

---

## 2026-09-03 Status Check (no new changes)

Ran scheduled check. No changes since 2026-09-01:
- py-sdk latest: **v0.7.1** (2026-08-28) — unchanged
- Issues #56, #61, #75 updated Aug 21–25 but remain **open**; no closures
- No new releases or merged auth-related PRs in py-clob-client-v2
- **Action still required**: migrate executor.py to Polymarket/py-sdk

---

## 2026-09-04 Status Check — NEW py-sdk releases

Two new `Polymarket/py-sdk` releases since the last check:

| Version | Date | Notable |
|---------|------|---------|
| **v0.9.0** | 2026-09-04 (today) | "support Poly V2 identifiers and trading"; asset ID compatibility bug fixes |
| **v0.8.0** | 2026-09-03 | Market combo status, protocol version exposure, session-key relayer improvements, multiple bug fixes |

py-clob-client-v2 status: unchanged. Issues #55, #64, #70, #71, #75, #76 still **OPEN**; no Polymarket staff responses. No new auth-related PRs merged.

**py-sdk is now at v0.9.0 — the recommended migration target has updated twice in two days. Migration to py-sdk remains the correct path for fixing the deposit-wallet auth bug.**

Next step: migrate executor.py to `Polymarket/py-sdk v0.9.0`.

---

## 2026-09-06 Status Check — Issue #115 closed (signature_type=2 blocker for PolyBot!)

**py-sdk**: No new releases. Still at **v0.9.0** (2026-09-04) — unchanged.

**py-clob-client-v2**:
- Issues #70, #71, #75, #76 remain **OPEN**. No new auth-related PRs merged.
- No Polymarket staff responses on tracked issues.

### NEW CRITICAL FINDING: Issue #115 closed 2026-09-05

**Issue #115** — "signature_type=2 orders rejected ('maker address not allowed') even with credentials proven valid via old client" — was **CLOSED on 2026-09-05** (yesterday).

This issue is directly relevant to PolyBot: the bot uses **signature_type=2 (Safe/Gnosis proxy wallet)**, and this issue describes that same setup being rejected by py-clob-client-v2 with `"maker address not allowed, please use the deposit wallet flow"`. The closure method (fix vs. wontfix/duplicate) was not visible from the issue page.

**Why this matters for PolyBot:**
- PolyBot's wallet is a Gnosis Safe at `0xbcd8Da52677827188A4c205dCC0D46eda3038A50` using signature_type=2
- Polymarket's docs claim "Existing Proxy and Safe users are unaffected and can keep using signature types 1 and 2"
- But issue #115 shows that is NOT true in py-clob-client-v2 — Safe users get "maker address not allowed"
- The issue being closed *may* indicate a fix landed — or it may have been closed as wontfix/duplicate pointing to py-sdk

**Action required**: Check how #115 was resolved (fix, wontfix, or duplicate) before attempting any live trading with py-clob-client-v2. Migration to py-sdk v0.9.0 remains the safest path.

**Link**: https://github.com/Polymarket/py-clob-client-v2/issues/115
