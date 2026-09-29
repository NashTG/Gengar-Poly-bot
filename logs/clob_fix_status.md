# CLOB Fix Status — 2026-09-29

## Summary (Updated)

Multiple fix signals confirmed. **Issue #115 — directly relevant to PolyBot's signature_type=2 setup —
was closed Sep 5, 2026**, indicating the "maker address not allowed" blocker for Gnosis Safe users was
resolved. Related issues #65 and #98 (POLY_1271 / deposit-wallet auth) are also closed. The three
originally-tracked issues #70, #75, #76 remain open (different reporters, same bug class).
Latest release is v1.2.0 (Sep 25, 2026).

**Next step: Upgrade py-clob-client-v2 to v1.2.0 and re-test executor.py with MANUAL_MODE=false.**
Also investigate `Polymarket/py-sdk` as the recommended replacement SDK.

---

## New Fix Signals (2026-09-29 check)

### Issue #115 CLOSED — Most Relevant to PolyBot
- **Title:** "signature_type=2 orders rejected ('maker address not allowed') even with credentials
  proven valid via old client"
- **Repo:** Polymarket/py-clob-client-v2
- **Closed:** September 5, 2026
- **URL:** https://github.com/Polymarket/py-clob-client-v2/issues/115
- **Why relevant:** PolyBot uses signature_type=2 (Gnosis Safe / Safe proxy). This is the exact error
  PolyBot would hit. Closure indicates a fix was applied or a workaround was documented.
- **Resolution detail:** Comments not accessible via web scrape; manual review needed.

### Issue #98 CLOSED
- **Title:** "signature_type=3 (POLY_1271) cannot post orders: 'the order signer address has to be
  the address of the API KEY'"
- **Repo:** Polymarket/py-clob-client-v2
- **Closed:** July 3, 2026
- **URL:** https://github.com/Polymarket/py-clob-client-v2/issues/98

### Issue #65 CLOSED (py-clob-client-v2)
- **Title:** "Cannot submit POLY_1271 orders — `create_or_derive_api_key` binds API key to EOA,
  not deposit wallet"
- **Repo:** Polymarket/py-clob-client-v2
- **Closed:** May 17, 2026
- **URL:** https://github.com/Polymarket/py-clob-client-v2/issues/65

### Relevant Merged PR: #39
- **Title:** "feat: add deposit wallet order support"
- **Merged:** May 1, 2026
- **URL:** https://github.com/Polymarket/py-clob-client-v2/pull/39
- **What it fixed:** Added POLY_1271 (`SignatureTypeV2`) support for order signing, enabling
  deposit wallet users to construct and sign orders correctly.

---

## Release Changelog (all > v1.0.1)

| Version | Released | What Changed |
|---------|----------|--------------|
| **v1.2.0** | 2026-09-25 | PolyV2 position orders: `position_id` support, auto Exchange V3 signing |
| **v1.1.0** | 2026-07-17 | Async execution: resolve transaction hashes internally (API now returns `tradeIDs`) |
| **v1.0.2** | 2026-07-02 | CLOB tick sizes `0.005` and `0.0025` added |

- v1.0.2: https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.0.2
- v1.1.0: https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.1.0
- v1.2.0: https://github.com/Polymarket/py-clob-client-v2/releases/tag/v1.2.0

---

## Tracked Issues Status (as of 2026-09-29)

| Repo | Issue | Status | Notes |
|------|-------|--------|-------|
| py-clob-client-v2 | #70 | **Open** | POLY_1271 L1 auth binds API key to EOA — no Polymarket staff response |
| py-clob-client-v2 | #75 | **Open** | POLY_1271 signer ≠ API KEY address — no Polymarket staff response |
| py-clob-client-v2 | #76 | **Open** | /auth/api-key lacks EIP-1271 support — no Polymarket staff response |
| py-clob-client-v2 | #115 | **CLOSED** (Sep 5) | sig_type=2 "maker address not allowed" — **DIRECTLY RELEVANT TO POLYBOT** |
| py-clob-client-v2 | #98 | **CLOSED** (Jul 3) | POLY_1271 order signer mismatch resolved |
| py-clob-client-v2 | #65 | **CLOSED** (May 17) | create_or_derive_api_key EOA binding resolved |
| py-clob-client-v2 | #55–64, #71 | Not individually checked | Same auth bug class |
| clob-client-v2 | #65 | Not checked | TypeScript SDK, not checked this run |

---

## Alternative Path: Polymarket/py-sdk

PR #78 (merged 2026-05-25) added a README note recommending migration to the unified
[Polymarket/py-sdk](https://github.com/Polymarket/py-sdk).

This SDK is described as the official replacement offering "one coherent, workflow-oriented
interface" covering trading, auth, and wallet workflows. The py-sdk's "scoped session keys"
feature (v0.7.0, released 2026-08-26) may offer a cleaner auth path than py-clob-client-v2's
`create_or_derive_api_key`.

---

## Recommended Next Steps

1. **Upgrade py-clob-client-v2 to v1.2.0** and re-test executor.py with `MANUAL_MODE=false`.
   - Focus: does order placement succeed for the PolyBot Safe address with signature_type=2?
   - If issue #115's fix is included, expect the "maker address not allowed" error to be resolved.

2. **Read issue #115 comments manually** at https://github.com/Polymarket/py-clob-client-v2/issues/115
   to understand exactly what changed and if a migration step is needed.

3. **Evaluate py-sdk** (https://github.com/Polymarket/py-sdk) as a longer-term replacement
   for executor.py if py-clob-client-v2 v1.2.0 still has issues.
