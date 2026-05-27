# CLOB Fix Status Monitor — 2026-05-27

## Overall Verdict

**No direct fix in py-clob-client-v2.** All tracked issues remain open, no auth-fixing code merged, still on v1.0.1.

**However: MIGRATION SIGNAL DETECTED.** Polymarket staff have officially deprecated py-clob-client-v2 and released a new unified SDK (`polymarket-client`) as the intended replacement. This is their response to the deposit wallet auth bug — migrate rather than patch.

---

## What Changed

### PR #78 — "docs: recommend new unified py-sdk in README" (MERGED May 25, 2026)
- **Repo:** Polymarket/py-clob-client-v2
- **Author:** suhailkakar (Polymarket staff) | **Merged by:** mustafa-poly (Polymarket staff)
- **Link:** https://github.com/Polymarket/py-clob-client-v2/pull/78
- **What it does:** Adds an official notice at the top of the py-clob-client-v2 README:
  > *"We've released a new unified SDK that combines all our REST APIs and WebSockets into one package. We recommend Polymarket/py-sdk for new projects."*
- **Significance:** This is Polymarket's official, staff-authored signal that py-clob-client-v2 will not be fixed. The POLY_1271/deposit wallet auth bug will not get a patch here.

### New `polymarket-client` SDK — Active Releases
- **Repo:** https://github.com/Polymarket/py-sdk
- **Package:** `pip install polymarket-client`
- **Release timeline:**
  - v0.1.0b1 — May 21, 2026
  - v0.1.0b2 — May 26, 2026
  - **v0.1.0-b3 — May 27, 2026 (today)**
- **Status:** Beta, actively developed, 166+ commits on main

---

## Tracked Issue Status (as of 2026-05-27)

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

**py-clob-client-v2 #65** (not in original tracking list): **Closed** May 17, 2026 — title: "Cannot submit POLY_1271 orders — `create_or_derive_api_key` binds API key to EOA, not deposit wallet" — no staff comment or linked PR visible; likely closed as "won't fix / use new SDK."

---

## py-clob-client-v2 Release Status

| Tag | Date | Notes |
|-----|------|-------|
| **v1.0.1** | May 9, 2026 | **Latest — no change** |
| 1.0.1rc1 | May 1, 2026 | Pre-release |
| v1.0.0 | Apr 17, 2026 | — |

No release > v1.0.1. No auth-fixing code PRs.

---

## Staff Activity on Key Issues

- Issues #70, #75, #76: **No staff comments visible.**
- Issue #63: Reporter noted "your setup is correct, the rejection is not expected" per support — but no engineering resolution.
- PR #78 and README update are the only staff-authored actions.

---

## What Was Fixed (and Where)

The deposit wallet / POLY_1271 auth bug (`create_or_derive_api_key` binding to EOA instead of deposit wallet) has **not been patched in py-clob-client-v2.**

Polymarket's resolution strategy: ship a new unified `polymarket-client` SDK and redirect all users there.

**Important caveat:** The new `polymarket-client` codebase does not yet show explicit `POLY_1271`, `deposit_wallet`, or `signature_type` terminology in its source. Its deposit wallet auth support is **unverified** as of this report. It may use a different architecture (Privy integration, unified wallet abstraction) that sidesteps the issue differently.

---

## Next Step

1. **Evaluate `polymarket-client` for deposit wallet support:**
   ```bash
   pip install polymarket-client==0.1.0b3
   ```
   Check `src/polymarket/` for auth/signing modules. Look for how API keys are derived and whether deposit wallet addresses are used as signers.

2. **If it handles deposit wallets correctly:** Rewrite `executor.py` to use `polymarket-client` instead of `py-clob-client-v2`. Key areas to replace: `create_or_derive_api_key()`, `ClobClient` init with `sig_type=3`, order submission.

3. **If it does not yet handle deposit wallets:** Continue monitoring. Check issues on Polymarket/py-sdk repo directly. The v0.1.0 beta cycle is active (3 releases in 1 week) — a deposit wallet fix could land any day.

4. **Alternative path:** Manually implement the EIP-7739 L1 auth wrapping fix described in py-clob-client-v2 issue #70 (bjklemmer-prog's ~50-line patch proposal). Wire it into current `executor.py` without changing SDKs.

**Primary recommendation:** `Upgrade to polymarket-client and re-test executor.py with DRY_RUN=false`
