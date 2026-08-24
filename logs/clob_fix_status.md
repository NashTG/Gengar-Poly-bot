# CLOB Fix Status — 2026-08-24

## New Releases Found

Two releases newer than v1.0.1 exist, but **neither fixes the core deposit-wallet authentication bug**:

| Release | Date | What changed |
|---------|------|--------------|
| v1.0.2 | 2026-07-02 | Added CLOB tick size support (0.005, 0.0025) |
| v1.1.0 | 2026-07-17 | Async execution: `POST /order` now returns `tradeIDs` instead of `transactionHashes`; client resolves hashes internally |

- Latest release: **v1.1.0** — https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.1.0
- Release v1.0.2: https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.0.2

## Core Auth Bug — Still Open

The bug where `create_or_derive_api_key` binds the API key to the EOA instead of the EIP-7702 deposit wallet (causing `"the order signer address has to be the address of the API KEY"`) remains **unresolved**:

- **Issue #70** (OPEN): "POLY_1271 (sig type 3) order placement fails: L1 auth always binds API key to EOA, never the deposit wallet" — https://github.com/Polymarket/py-clob-client-v2/issues/70
- **Issue #75** (OPEN): "POLY_1271 deposit-wallet orders rejected: the order signer address has to be the address of the API KEY" — https://github.com/Polymarket/py-clob-client-v2/issues/75
- **Issue #76** (OPEN): "CLOB V2 Python SDK unusable for deposit wallets - /auth/api-key doesnt support EIP-1271" — https://github.com/Polymarket/py-clob-client-v2/issues/76

**Zero staff responses** on #70, #75, or #76 from JonathanAmenechi, suhailkakar, or any Polymarket org member.

Also noted: Issue #65 on `py-clob-client-v2` ("Cannot submit POLY_1271 orders — create_or_derive_api_key binds API key to EOA") was closed 2026-05-17, but tracked issues #70/#75/#76 opened after confirm the bug persisted through v1.0.1.

## Notable Merged PR

- **PR #39** (merged 2026-05-01): "feat: add deposit wallet order support" — added POLY_1271 order *signing* support (OrderBuilder now accepts funder as signer). This is a partial improvement but does NOT fix API key derivation binding to EOA. Released as v1.0.1.
- https://github.com/Polymarket/py-clob-client-v2/pull/39

## Next Step

Upgrade `py-clob-client-v2` to v1.1.0 and re-test `executor.py` with `MANUAL_MODE=false`. The v1.1.0 async tradeID change may affect order verification in `executor.py` (currently waits for `transactionsHashes` in order response — check if the response format change breaks verification logic). The core auth bug likely still blocks POLY_1271 accounts, but test to confirm current behavior.
