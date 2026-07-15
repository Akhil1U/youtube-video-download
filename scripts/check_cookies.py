"""Validate a Netscape cookies.txt file for YouTube auth cookies.

Usage:
    uv run python scripts/check_cookies.py [path/to/cookies.txt]

Checks that the required login/auth cookie names are present (not just
anonymous/consent cookies), and reports each cookie's expiry timestamp.
Exits non-zero if any required cookie is missing.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_AUTH_COOKIES = {
    "SID",
    "HSID",
    "SSID",
    "APISID",
    "SAPISID",
    "__Secure-1PSID",
    "__Secure-3PSID",
    "LOGIN_INFO",
}


def parse_netscape_cookies(path: Path) -> dict[str, int]:
    cookies = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 7:
            continue
        _domain, _flag, _path, _secure, expiry, name, _value = parts
        cookies[name] = int(expiry)
    return cookies


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "cookies.txt")
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(2)

    cookies = parse_netscape_cookies(path)
    if not cookies:
        print("No cookies parsed — file may be empty or malformed.")
        sys.exit(2)

    missing = REQUIRED_AUTH_COOKIES - cookies.keys()

    print(f"Parsed {len(cookies)} cookies from {path}\n")

    print("Expiry (soonest first):")
    for name, ts in sorted(cookies.items(), key=lambda kv: kv[1]):
        if name not in REQUIRED_AUTH_COOKIES:
            continue
        if ts == 0:
            print(f"  {name:30s}  session cookie (no fixed expiry)")
        else:
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            print(f"  {name:30s}  {dt.isoformat()}")

    print()
    if missing:
        print(f"MISSING required auth cookies: {', '.join(sorted(missing))}")
        print(
            "This file looks like an anonymous/logged-out export — it will "
            "NOT authenticate with YouTube. Re-export from a private window "
            "after confirming you're actually logged in."
        )
        sys.exit(1)
    else:
        print("All required auth cookies present. This is a real logged-in export.")
        print(
            "Note: the printed expiry dates are upper bounds only. YouTube can "
            "invalidate these earlier via session rotation — treat this as a "
            "snapshot, and re-export if you start seeing 'Sign in to confirm "
            "you're not a bot' errors again."
        )


if __name__ == "__main__":
    main()
