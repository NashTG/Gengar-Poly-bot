# CLOB Fix Status — 2026-08-25

## New Releases Found

Two releases newer than v1.0.1 exist, but **neither directly fixes the core deposit-wallet API key derivation bug**:

| Release | Date | What changed |
|---------|------|--------------|
| v1.0.2 | 2026-07-02 | Added CLOB tick size support (0.005, 0.0025) |
| v1.1.0 | 2026-07-17 | Async execution: `POST /order` now returns `tradeIDs` instead of `transactionHashes`; client resolves hashes internally |

- Latest release: **v1.1.0** — https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.1.0
- Release v1.0.2: https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.0.2

## Core Auth Bug — Partially Fixed (Ambiguous)

The bug where `create_or_derive_api_key` binds the API key to the EOA instead of the EIP-7702 deposit wallet (causing `"the order signer address has to be the address of the API KEY"`) is **partially addressed** but tracked issues remain open:

### Closed issues (fix signals)

- **Issue #65** (py-clob-client-v2, CLOSED 2026-05-17): "Cannot submit POLY_1271 orders — create_or_derive_api_key binds API key to EOA, not deposit wallet" — https://github.com/Polymarket/py-clob-client-v2/issues/65
- **Issue #98** (py-clob-client-v2, CLOSED 2026-07-03): "signature_type=3 (POLY_1271) cannot post orders: 'the order signer address has to be the address of the API KEY'" — https://github.com/Polymarket/py-clob-client-v2/issues/98 *(NEW — not in yesterday's report)*

### Still-open tracked issues

- **Issue #70** (OPEN): "POLY_1271 (sig type 3) order placement fails: L1 auth always binds API key to EOA, never the deposit wallet" — https://github.com/Polymarket/py-clob-client-v2/issues/70
- **Issue #75** (OPEN): "POLY_1271 deposit-wallet orders rejected: the order signer address has to be the address of the API KEY" — https://github.com/Polymarket/py-clob-client-v2/issues/75
- **Issue #76** (OPEN): "CLOB V2 Python SDK unusable for deposit wallets - /auth/api-key doesnt support EIP-1271" — https://github.com/Polymarket/py-clob-client-v2/issues/76
- **Issue #65** (clob-client-v2, OPEN): "createApiKey() / create_or_derive_api_key() doesn't EIP-1271-wrap L1 auth for POLY_1271 deposit wallets — orders rejected with signer != api_key" — https://github.com/Polymarket/clob-client-v2/issues/65

**Zero staff responses** on #70, #75, or #76 from JonathanAmenechi, suhailkakar, or any Polymarket org member.

## Notable Merged PR

- **PR #39** (merged 2026-05-01): "feat: add deposit wallet order support" — added POLY_1271 order *signing* support (OrderBuilder now accepts funder as V2 signer, generates custom POLY_1271 signature payloads). Released in v1.0.1.
  - This is a partial fix: order *signing* now works with POLY_1271, but API key *derivation* (`create_or_derive_api_key`) may still bind to EOA — tracked issues #70/#75/#76 were opened after this merge.
  - https://github.com/Polymarket/py-clob-client-v2/pull/39

## Assessment

Mixed signal. Issue #98 (exact error message match) was closed July 3, and two new releases exist. But #70/#75/#76 were opened after these fixes and remain unresolved with no staff engagement. **Test recommended.**

## Next Step

Upgrade `py-clob-client-v2` to v1.1.0 and re-test `executor.py` with `MANUAL_MODE=false`.

**⚠️ v1.1.0 breaking change risk**: The async tradeID change means `POST /order` now returns `tradeIDs` instead of `transactionsHashes`. Check if `executor.py`'s order verification logic expects `transactionsHashes` in the response — if so, upgrade may break verification. Review before deploying.
