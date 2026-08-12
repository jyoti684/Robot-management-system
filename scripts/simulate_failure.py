from __future__ import annotations

import json
import os
import sys
import urllib.request


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1].lower() not in {"on", "off"}:
        print("Usage: python scripts/simulate_failure.py on|off")
        return 2
    enabled = sys.argv[1].lower() == "on"
    url = os.getenv("ROBOT_ADMIN_URL", f"http://127.0.0.1:8001/admin/failure/{str(enabled).lower()}")
    request = urllib.request.Request(url, method="POST")
    request.add_header("X-Admin-Token", os.getenv("ROBOT_ADMIN_TOKEN", "demo-admin-token"))
    with urllib.request.urlopen(request, timeout=5) as response:
        print(json.loads(response.read().decode("utf-8")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
