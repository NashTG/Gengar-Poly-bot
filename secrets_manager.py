"""Secure credential management using OS-level keyring.

On Windows: Windows Credential Manager.
On macOS:   Keychain.
On Linux:   Secret Service (gnome-keyring/kwallet).

Falls back to environment variables if keyring is unavailable, but warns
loudly. Provides a migration path to move credentials from .env to keyring.

CLI usage:
    python secrets_manager.py status       # show where each secret lives
    python secrets_manager.py migrate      # move .env secrets to keyring
    python secrets_manager.py delete       # remove all from keyring

Library usage:
    from secrets_manager import get_secret
    private_key = get_secret("PRIVATE_KEY")
"""

import os
import sys

SERVICE_NAME = "polybot"
SENSITIVE_NAMES = ["PRIVATE_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False


def get_secret(name: str, fallback_to_env: bool = True) -> str:
    """Retrieve a secret. Prefers OS keyring; falls back to env if missing.

    Returns empty string if not found anywhere.
    """
    if KEYRING_AVAILABLE:
        try:
            value = keyring.get_password(SERVICE_NAME, name)
            if value:
                return value
        except Exception as e:
            print(f"[secrets] keyring lookup failed for {name}: {e}", file=sys.stderr)

    if fallback_to_env:
        value = os.getenv(name, "")
        if value:
            print(
                f"[secrets] WARNING: {name} loaded from .env, not OS keyring. "
                f"Run `python secrets_manager.py migrate` to secure it.",
                file=sys.stderr,
            )
            return value

    return ""


def set_secret(name: str, value: str) -> bool:
    if not KEYRING_AVAILABLE:
        print(
            "[secrets] keyring not installed — run: pip install keyring",
            file=sys.stderr,
        )
        return False
    try:
        keyring.set_password(SERVICE_NAME, name, value)
        return True
    except Exception as e:
        print(f"[secrets] failed to store {name}: {e}", file=sys.stderr)
        return False


def delete_secret(name: str) -> bool:
    if not KEYRING_AVAILABLE:
        return False
    try:
        keyring.delete_password(SERVICE_NAME, name)
        return True
    except Exception:
        return False


def _load_dotenv_if_present():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass


def migrate_from_env(names=None):
    if not KEYRING_AVAILABLE:
        print("[secrets] Cannot migrate — install keyring first: pip install keyring")
        return

    names = names or SENSITIVE_NAMES
    _load_dotenv_if_present()

    migrated, missing = [], []
    for name in names:
        value = os.getenv(name, "")
        if not value:
            missing.append(name)
            continue
        if set_secret(name, value):
            migrated.append(name)

    print(f"\n[secrets] Migrated {len(migrated)} credential(s) to OS keyring:")
    for n in migrated:
        print(f"  OK  {n}")
    if missing:
        print(f"\n[secrets] Not found in environment ({len(missing)}):")
        for n in missing:
            print(f"  --  {n}")

    if migrated:
        print(
            "\n[secrets] IMPORTANT next steps:\n"
            "  1. Open .env and DELETE the lines for the migrated keys above.\n"
            "  2. Verify with: python secrets_manager.py status\n"
            "  3. The bot will now read these from OS keyring automatically.\n"
        )


def status():
    backend = "keyring" if KEYRING_AVAILABLE else "ENV ONLY (insecure)"
    print(f"\n[secrets] Backend: {backend}\n")
    print("  keyring  env      name")
    print("  -------  -------  ----")
    _load_dotenv_if_present()
    for n in SENSITIVE_NAMES:
        in_keyring = False
        if KEYRING_AVAILABLE:
            try:
                in_keyring = bool(keyring.get_password(SERVICE_NAME, n))
            except Exception:
                pass
        in_env = bool(os.getenv(n))
        kr = " OK    " if in_keyring else "       "
        ev = " WARN  " if in_env else "       "
        print(f"  [{kr}] [{ev}] {n}")
    print()
    if any(os.getenv(n) for n in SENSITIVE_NAMES):
        print("[secrets] WARN: secrets present in .env. Run `migrate` to secure them.\n")


def delete_all():
    if not KEYRING_AVAILABLE:
        print("[secrets] keyring not installed.")
        return
    for n in SENSITIVE_NAMES:
        if delete_secret(n):
            print(f"  deleted {n}")
        else:
            print(f"  not present: {n}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Manage PolyBot credentials in OS keyring")
    p.add_argument(
        "command",
        choices=["migrate", "status", "delete"],
        help="migrate: copy .env -> keyring; status: show where each secret lives; delete: wipe keyring entries",
    )
    args = p.parse_args()
    if args.command == "migrate":
        migrate_from_env()
    elif args.command == "status":
        status()
    elif args.command == "delete":
        delete_all()
