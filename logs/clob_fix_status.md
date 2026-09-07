# CLOB Fix Monitor Status

**Date checked:** 2026-09-07

## What changed since last baseline (v1.0.1, 2026-05-09)

### New releases
| Version | Released | Notes |
|---------|----------|-------|
| v1.0.2 | 2026-07-02 | Tick size fixes — no auth changes |
| v1.1.0 | 2026-07-17 | Async execution / transactionHash→tradeID handling — no auth changes |

- GitHub: https://github.com/Polymarket/py-clob-client-v2/releases

### Relevant merged PRs
| PR | Title | Merged |
|----|-------|--------|
| #39 | feat: add deposit wallet order support | 2026-05-01 |

- PR #39 added POLY_1271 (signature_type=3) signing in the OrderBuilder but did **NOT** fix `create_or_derive_api_key` EOA-binding.
- Issues #70, #75, #76 were all filed **after** PR #39 merged, confirming the core bug remains unresolved.
- GitHub: https://github.com/Polymarket/py-clob-client-v2/pull/39

## Tracked issue status (as of 2026-09-07)

| Issue | Status | Summary |
|-------|--------|---------|
| #70 | **OPEN** | "POLY_1271 (sig type 3) order placement fails: L1 auth always binds API key to EOA" — no staff response |
| #75 | **OPEN** | "POLY_1271 deposit-wallet orders rejected: order signer address ≠ API KEY address" — no staff response |
| #76 | **OPEN** | "CLOB V2 Python SDK unusable for deposit wallets - /auth/api-key doesn't support EIP-1271" — no staff response |

Issues #55–#64, #71 not individually confirmed this run (page out of range). Issues #70, #75, #76 confirmed open as of today.

clob-client-v2 issue #65: not fetched this run.

## Assessment

**The core bug is NOT fixed.** The "order signer address has to be the address of the API KEY" error persists because:
1. `create_or_derive_api_key()` signs with the EOA as `POLY_ADDRESS`
2. Orders placed with `POLY_1271` use the deposit wallet contract as signer
3. These addresses never match → every order rejected

v1.0.2 and v1.1.0 do not touch `l1_auth.py` / key derivation. No Polymarket staff have commented on any of the tracked issues.

## Next step

**Do not upgrade yet — the fix is not in the SDK.**

Monitor for:
- Issue #70 closure or a staff comment (Polymarket eng acknowledged it)
- A PR targeting `l1_auth.py`, `api_key.py`, or `create_or_derive_api_key`
- A release specifically mentioning deposit wallet API key binding

When a genuine fix lands: upgrade `py-clob-client-v2` and re-test `executor.py` with `MANUAL_MODE=false`.
