# CLOB Fix Status — 2026-10-14

## Date detected
2026-10-14 (automated monitoring run)

## What changed

### New releases (all newer than v1.0.1, the previous baseline)

| Version | Released | What changed |
|---------|----------|--------------|
| v1.0.2  | Jul 2, 2026  | Tick size support (0.005, 0.0025). No auth changes. |
| v1.1.0  | Jul 17, 2026 | Async execution: POST /order now returns tradeIDs. No auth changes. |
| v1.2.0 (latest) | Sep 25, 2026 | PolyV2 position orders (position_id field, Exchange V3 signing). No auth changes in release notes. |

### Relevant merged PR

**PR #39 — "feat: add deposit wallet order support"** (merged May 1, 2026, included in v1.0.1rc1 → v1.0.1)
- https://github.com/Polymarket/py-clob-client-v2/pull/39
- Added POLY_1271 (signature_type=3) order signing: `OrderBuilder` and `ExchangeOrderBuilderV2` now accept `funder` as the V2 signer and generate a custom POLY_1271 signature.
- References issue #49 (signer field set to EOA instead of deposit wallet). Does NOT explicitly fix `create_or_derive_api_key` API key binding.

## Issue status (as of 2026-10-14)

All tracked issues remain **OPEN**:

| Issue | Title | Status | Notes |
|-------|-------|--------|-------|
| #55 | POLY_1271 order signer set to EOA instead of funder | Open | — |
| #56 | 400 "maker address not allowed" for Magic.link proxy wallets | Open | — |
| #57 | Cannot place sigtype=3 orders, Privy TSS mismatch | Open | — |
| #58 | How CLOB API credentials are bound for deposit wallets | Open | — |
| #61 | "maker address not allowed" for new MetaMask accounts | Open | — |
| #63 | post_order rejected for new MetaMask deposit wallets | Open | — |
| #64 | POLY_1271 + Deposit Wallet signer mismatch | Open | — |
| #70 | POLY_1271 (sig type 3) order placement fails | Open | Community: vladII987 (Oct 8) reported v1.2.0 order filled with EOA-addressed auth; EIP-7702 still fails |
| #71 | POLY_1271 orders fail | Open | — |
| #75 | POLY_1271 deposit-wallet orders rejected | Open | Workaround: derive API key with signature_type=3 and funder set; unconfirmed official fix |
| #76 | CLOB V2 Python SDK unusable for deposit wallets | Open | Workaround: use browser wallet (MetaMask) instead of email; unconfirmed for Python SDK |
| clob-client-v2 #65 | (not checked this run — GitHub MCP scoped only to nashtg/gengar-poly-bot) | — | — |

## No Polymarket staff comments found
Issues #70, #75, #76 show no responses from org members (JonathanAmenechi, suhailkakar, or other staff).

## Summary

The original bug (`create_or_derive_api_key` binding the API key to the EOA instead of the deposit wallet) has **no confirmed fix in any release**. However:
- v1.2.0 is the latest release (Sep 25, 2026), 3 versions ahead of v1.0.1
- PR #39 added POLY_1271 order signing support
- Community reports (issue #70, Oct 8, 2026) suggest orders MAY work in v1.2.0 under certain configurations, but EIP-7702 delegated wallets still fail

**Note for this bot**: CLAUDE.md documents signature_type=2 (Safe/proxy), not type 3. The POLY_1271 bug may not directly affect this bot's trading path.

## Next step

Upgrade py-clob-client-v2 to v1.2.0 and re-test executor.py with MANUAL_MODE=false.

Test specifically:
1. Can `create_or_derive_api_key()` succeed with the Safe wallet (signature_type=2)?
2. Do orders reach the complement engine book and fill?
3. If still blocked, try the community workaround: instantiate `ClobClient` with `signature_type=3` and `funder` set to the deposit wallet address before calling `create_or_derive_api_key()`.
