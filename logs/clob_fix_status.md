# CLOB Fix Status — 2026-08-26

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

### Tracked issue states (as of 2026-08-26)

- Issue #55 — unknown state (not visible in search)
- Issue #56 — **OPEN**
- Issue #57 — unknown state
- Issue #58 — unknown state
- Issue #61 — **OPEN**
- Issue #63 — unknown state
- Issue #64 — **OPEN**
- Issue #70 — **OPEN**: "L1 auth always binds API key to EOA, never the deposit wallet"
- Issue #71 — unknown state
- Issue #75 — **OPEN**: "POLY_1271 deposit-wallet orders rejected: signer != API KEY"
- Issue #76 — **OPEN**: "CLOB V2 Python SDK unusable for deposit wallets"
- clob-client-v2 #65 — **OPEN**: same root cause in JS/Rust SDK

Zero Polymarket staff responses on #70, #75, or #76.

### Notable merged PR

- **PR #39** (merged 2026-05-01): "feat: add deposit wallet order support" — added POLY_1271 order *signing* in OrderBuilder. **Partial fix only**: order signing works, but API key *derivation* (`create_or_derive_api_key`) still binds to EOA. Issues were opened after this merge.
  - https://github.com/Polymarket/py-clob-client-v2/pull/39

---

## KEY FINDING: Polymarket/py-sdk is the actual fix path

**PR #78** (merged 2026-05-25) updated the py-clob-client-v2 README to recommend the new unified SDK:

> "We've released a new unified SDK that combines all our REST APIs and WebSockets into one package. We recommend Polymarket/py-sdk for new projects."

- Repo: https://github.com/Polymarket/py-sdk
- Latest release: **v0.6.0** (2026-08-13) — actively maintained
- No open issues about deposit-wallet auth, EIP-7702, POLY_1271, or API key binding
- Merged PR: "self-heal deposit wallet nonce on submit rejection" — confirms deposit wallet flow is functional

### What this means for PolyBot

`py-clob-client-v2` is effectively in maintenance mode for this bug. The fix is to **migrate executor.py to Polymarket/py-sdk**.

---

## v1.1.0 Breaking Change Risk (if upgrading py-clob-client-v2)

`POST /order` now returns `tradeIDs` instead of `transactionHashes`. Check `executor.py`'s order verification logic — if it reads `transactionHashes` from the response, the upgrade breaks verification.

---

## Next Step

**Migrate to `Polymarket/py-sdk` v0.6.0** rather than upgrading py-clob-client-v2:
1. `pip install polymarket-client==0.6.0`
2. Rewrite `executor.py` authentication to use py-sdk's deposit-wallet flow
3. Confirm deposit-wallet API key derivation uses the correct signer address
4. Test with `DRY_RUN=true`, then `DRY_RUN=false` with MIN_BET=5
