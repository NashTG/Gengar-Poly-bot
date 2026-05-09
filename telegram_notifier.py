"""Telegram notification module with privacy controls.

Privacy modes (set via TELEGRAM_PRIVACY_MODE env var):

  minimal (default)
      Per-trade alerts: side + rounded amount only. No edge, no kelly,
      no market slug, no exact bankroll. Hourly: counts and rounded P&L.
      Designed to be useful for monitoring while leaking minimal data
      to Telegram's servers.

  digest
      No per-trade alerts. Only hourly summary (rounded values).
      Quietest mode that still surfaces problems.

  full
      Original behavior — exact prices, sizes, edges, market slugs,
      bankroll. Use only on trusted personal devices and accept the
      data-exfiltration trade-off.

Credentials are read from OS keyring (preferred) via secrets_manager,
falling back to env vars with a warning. All user-controlled strings
are escaped before being sent with parse_mode=Markdown to prevent
markdown injection in bot alerts.
"""

import os
import urllib.request
import json
import threading

from secrets_manager import get_secret


PRIVACY_MINIMAL = "minimal"
PRIVACY_DIGEST = "digest"
PRIVACY_FULL = "full"
_VALID_MODES = {PRIVACY_MINIMAL, PRIVACY_DIGEST, PRIVACY_FULL}

# Markdown special chars that need escaping in Telegram "Markdown" parse mode.
_MD_CHARS = "_*`["


def _escape_md(text: str) -> str:
    if text is None:
        return ""
    out = str(text)
    for c in _MD_CHARS:
        out = out.replace(c, "\\" + c)
    return out


def _round_money(value: float, bucket: float = 5.0) -> str:
    """Bucket dollar amounts so we don't leak exact bankroll/P&L values."""
    if value is None:
        return "$?"
    rounded = round(float(value) / bucket) * bucket
    sign = "-" if rounded < 0 else ""
    return f"{sign}${abs(rounded):.0f}"


class TelegramNotifier:
    def __init__(self, bot_token: str = None, chat_id: str = None, privacy_mode: str = None):
        self.bot_token = bot_token or get_secret("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or get_secret("TELEGRAM_CHAT_ID")
        self.enabled = bool(self.bot_token and self.chat_id)

        mode = (privacy_mode or os.getenv("TELEGRAM_PRIVACY_MODE", PRIVACY_MINIMAL)).lower()
        if mode not in _VALID_MODES:
            print(f"[telegram] Unknown privacy mode '{mode}', defaulting to '{PRIVACY_MINIMAL}'")
            mode = PRIVACY_MINIMAL
        self.privacy_mode = mode

        # Telegram API rate limit safety. We don't queue, we just drop.
        self._consecutive_failures = 0
        self._failure_lock = threading.Lock()

        if not self.enabled:
            print("[telegram] No token/chat_id configured — notifications disabled")
        else:
            print(f"[telegram] Enabled (privacy={self.privacy_mode})")

    # ── transport ──────────────────────────────────────────────────────

    def send(self, message: str, silent: bool = False):
        if not self.enabled:
            return
        threading.Thread(
            target=self._send_sync, args=(message, silent), daemon=True
        ).start()

    def _send_sync(self, message: str, silent: bool):
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = json.dumps({
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_notification": silent,
            }).encode("utf-8")
            req = urllib.request.Request(
                url, data=payload, headers={"Content-Type": "application/json"}
            )
            urllib.request.urlopen(req, timeout=10)
            with self._failure_lock:
                self._consecutive_failures = 0
        except Exception as e:
            # Don't echo the URL (contains token). Don't include `e` if it
            # might contain a request body with the token.
            with self._failure_lock:
                self._consecutive_failures += 1
                n = self._consecutive_failures
            print(f"[telegram] send failed (consecutive={n}): {type(e).__name__}")

    @property
    def consecutive_failures(self) -> int:
        with self._failure_lock:
            return self._consecutive_failures

    # ── alerts ─────────────────────────────────────────────────────────

    def trade_alert(self, side: str, price: float, amount: float, market_slug: str,
                    dry_run: bool, edge: float = 0, kelly_size: float = 0):
        if self.privacy_mode == PRIVACY_DIGEST:
            return  # only hourly digest in this mode

        side = _escape_md(side)
        mode = "PAPER" if dry_run else "LIVE"
        icon = "📝" if dry_run else "🔔"

        if self.privacy_mode == PRIVACY_MINIMAL:
            self.send(
                f"{icon} *{mode} TRADE*\n"
                f"Side: *{side}*\n"
                f"Amount: ~{_round_money(amount, 5)}"
            )
            return

        # full
        slug = _escape_md(market_slug)
        self.send(
            f"{icon} *{mode} TRADE*\n"
            f"Side: *{side}*\n"
            f"Price: ${price:.4f}\n"
            f"Amount: ${amount:.2f} (Kelly: ${kelly_size:.2f})\n"
            f"Edge: {edge*100:.1f}%\n"
            f"Market: `{slug}`"
        )

    def win_alert(self, profit: float, total_pnl: float):
        if self.privacy_mode == PRIVACY_DIGEST:
            return
        if self.privacy_mode == PRIVACY_MINIMAL:
            self.send("✅ *WIN*")
            return
        self.send(f"✅ *WIN* +${profit:.2f}\nTotal P&L: ${total_pnl:.2f}")

    def loss_alert(self, loss: float, total_pnl: float):
        if self.privacy_mode == PRIVACY_DIGEST:
            return
        if self.privacy_mode == PRIVACY_MINIMAL:
            self.send("❌ *LOSS*")
            return
        self.send(f"❌ *LOSS* -${abs(loss):.2f}\nTotal P&L: ${total_pnl:.2f}")

    def hourly_summary(self, hourly: dict, overall: dict):
        h, o = hourly, overall

        if self.privacy_mode in (PRIVACY_MINIMAL, PRIVACY_DIGEST):
            lines = [
                "📊 *HOURLY*",
                f"This hour: {h['trades']} trades ({h['wins']}W / {h['losses']}L)",
                f"P&L: ~{_round_money(h['pnl'], 5)}",
                f"Total: {o['total_trades']} trades, win rate {o['win_rate']:.0f}%",
                f"Bankroll: ~{_round_money(o['bankroll'], 10)}",
            ]
            self.send("\n".join(lines))
            return

        # full
        lines = [
            "📊 *HOURLY SUMMARY*",
            "",
            "*This hour:*",
            f"  Trades: {h['trades']} ({h['wins']}W / {h['losses']}L)",
            f"  Win rate: {h['win_rate']:.1f}%",
            f"  P&L: ${h['pnl']:+.2f}",
        ]
        if h['trades'] > 0:
            lines.append(f"  Avg edge at entry: {h['avg_edge']*100:.1f}%")
            lines.append(f"  Avg BTC delta: {h['avg_delta']:.3f}%")
            lines.append(f"  Best trade: ${h['best_trade']:+.2f}")
            lines.append(f"  Worst trade: ${h['worst_trade']:+.2f}")
        lines.append(f"  Windows seen: {h['windows_seen']}")
        lines.append(f"  Windows skipped: {h['windows_skipped']} (no signal)")
        lines.extend([
            "",
            "*Overall:*",
            f"  Total trades: {o['total_trades']} ({o['wins']}W / {o['losses']}L)",
            f"  Win rate: {o['win_rate']:.1f}%",
            f"  Total P&L: ${o['pnl']:+.2f}",
            f"  Bankroll: ${o['bankroll']:.2f}",
        ])
        self.send("\n".join(lines))

    def status_update(self, stats: dict):
        if self.privacy_mode == PRIVACY_DIGEST:
            return
        if self.privacy_mode == PRIVACY_MINIMAL:
            self.send(
                f"📊 *Status*\n"
                f"Trades: {stats.get('total_trades', 0)} "
                f"({stats.get('wins', 0)}W/{stats.get('losses', 0)}L)\n"
                f"Bankroll: ~{_round_money(stats.get('bankroll', 0), 10)}",
                silent=True,
            )
            return
        self.send(
            f"📊 *Status*\n"
            f"Trades: {stats.get('total_trades', 0)}\n"
            f"W/L: {stats.get('wins', 0)}/{stats.get('losses', 0)}\n"
            f"Win rate: {stats.get('win_rate', 0):.1f}%\n"
            f"P&L: ${stats.get('pnl', 0):.2f}\n"
            f"Bankroll: ${stats.get('bankroll', 0):.2f}",
            silent=True,
        )

    def error_alert(self, error: str):
        # Always escape: error strings may contain attacker-influenced text
        # (e.g. server response bodies, market slugs).
        self.send(f"⚠️ *ERROR*\n`{_escape_md(str(error)[:200])}`")

    def startup_alert(self, config: dict):
        kelly = config.get('kelly_fraction', 0.25)
        mode = "DRY RUN" if config.get('dry_run') else "LIVE"

        if self.privacy_mode in (PRIVACY_MINIMAL, PRIVACY_DIGEST):
            self.send(f"🚀 *Bot Started* ({mode}) — privacy={self.privacy_mode}")
            return

        self.send(
            f"🚀 *Bot Started*\n"
            f"Mode: *{mode}*\n"
            f"Kelly fraction: {kelly*100:.0f}%\n"
            f"Min edge: {config.get('min_edge', 0)*100:.1f}%\n"
            f"Bet range: ${config.get('min_bet', 1):.0f}–${config.get('max_bet', 25):.0f}\n"
            f"Entry: T-{config.get('entry_start', 60)}s to T-{config.get('entry_end', 10)}s"
        )
