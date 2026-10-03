# CLOB Fix Status — py-clob-client-v2

## Date Found
2026-10-03

## Fix Signals Detected

### 1. PR #39 Merged — "feat: add deposit wallet order support"
- **URL**: https://github.com/Polymarket/py-clob-client-v2/pull/39
- **Merged**: May 1, 2026 (released in v1.0.1rc1)
- **What it fixes**: Adds POLY_1271 signature type support to `OrderBuilder` and `ExchangeOrderBuilderV2`, enabling deposit wallet order creation. Uses the funder address as the V2 signer with custom POLY_1271 signature payloads — directly addressing the EOA-vs-deposit-wallet auth binding.

### 2. Issue #98 CLOSED — Exact same error message as the tracked bug
- **URL**: https://github.com/Polymarket/py-clob-client-v2/issues/98
- **Closed**: July 3, 2026
- **Title**: "signature_type=3 (POLY_1271) cannot post orders: 'the order signer address has to be the address of the API KEY'"
- **What it fixes**: The exact error reported in the monitored issues — ordering with POLY_1271 credentials now resolves without the signer-mismatch rejection.

### 3. New Releases (all newer than v1.0.1)
| Release | Date | Notes |
|---------|------|-------|
| v1.0.2 | July 2, 2026 | Tick size support; includes PR #39 deposit wallet fix |
| v1.1.0 | July 17, 2026 | Async execution support; internal tradeID handling |
| v1.2.0 | September 25, 2026 | Position-backed orders (`position_id` support) — **latest** |

Latest release URL: https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.2.0

### 4. Unified SDK Now Recommended (PR #78)
- **URL**: https://github.com/Polymarket/py-clob-client-v2/pull/78
- **Merged**: May 25, 2026
- **Note**: Polymarket now recommends `Polymarket/py-sdk` (REST + WebSockets) for new projects over py-clob-client-v2. This may be the cleaner path forward.

## Caveats — Still Open Issues
The original tracked issues remain open:
- py-clob-client-v2 #70: "POLY_1271 order placement fails: L1 auth always binds API key to EOA" — **still open**
- py-clob-client-v2 #76: "CLOB V2 Python SDK unusable for deposit wallets - /auth/api-key doesn't support EIP-1271" — **still open**
- clob-client-v2 #65: "createApiKey() doesn't EIP-1271-wrap L1 auth for POLY_1271 deposit wallets" — **still open**

The fix may be partial or require additional configuration. Issue #98 (same error, different reporter) was closed, suggesting some configurations now work.

## Next Step
Upgrade py-clob-client-v2 to v1.2.0 and re-test executor.py with MANUAL_MODE=false — specifically test `create_or_derive_api_key()` with `signature_type=3` (POLY_1271) to confirm the signer-mismatch error is resolved. If issues persist, evaluate migrating to the unified `Polymarket/py-sdk`.
