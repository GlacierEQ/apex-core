#!/usr/bin/env python3
"""
APEX OPERA NEON BROWSER AUTOMATION & MCP DRIVER
Standard: Drives Opera Neon via OAuth MCP (https://mcp.neon.opera.com/mcp) and Chromium CDP / Playwright.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

OPERA_MCP_URL = "https://mcp.neon.opera.com/mcp"
OPERA_APP_PATH = Path("/Applications/Opera Neon.app/Contents/MacOS/Opera")


def check_opera_status() -> dict:
    p = subprocess.run(["pgrep", "-f", "Opera Neon"], capture_output=True, text=True)
    running = bool(p.stdout.strip())
    pids = p.stdout.strip().splitlines() if running else []
    return {
        "installed": OPERA_APP_PATH.exists(),
        "running": running,
        "pids": pids,
        "mcp_endpoint": OPERA_MCP_URL,
    }


def launch_opera_neon_with_cdp(port: int = 9222, url: str = "https://casey-barton-glaciereq.netlify.app"):
    if not OPERA_APP_PATH.exists():
        print(f"[-] Opera Neon executable not found at: {OPERA_APP_PATH}")
        sys.exit(1)

    cmd = [
        str(OPERA_APP_PATH),
        f"--remote-debugging-port={port}",
        url,
    ]
    print(f"🚀 Launching Opera Neon with Remote Debugging (Port {port})...")
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"✓ Opera Neon Launched (PID: {proc.pid}) -> {url}")
    return proc.pid


def ping_opera_mcp() -> dict:
    req = urllib.request.Request(
        OPERA_MCP_URL,
        headers={"Accept": "application/json, text/event-stream"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return {"status": resp.status, "message": "Connected"}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "message": "OAuth Authentication / Pairing required"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def main():
    parser = argparse.ArgumentParser(description="APEX Opera Neon Driver")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Check Opera Neon and MCP status")
    subparsers.add_parser("mcp-ping", help="Ping Opera Neon remote OAuth MCP endpoint")

    launch_p = subparsers.add_parser("launch", help="Launch Opera Neon with remote CDP debugging")
    launch_p.add_argument("--port", "-p", type=int, default=9222)
    launch_p.add_argument("--url", "-u", default="https://casey-barton-glaciereq.netlify.app")

    args = parser.parse_args()

    if args.command == "status" or not args.command:
        st = check_opera_status()
        print("=" * 80)
        print("🌐 OPERA NEON STATUS & MCP INTEGRATION")
        print("=" * 80)
        print(f"  • App Installed  : {'✓ Present' if st['installed'] else '[-] Missing'}")
        print(f"  • Process Status : {'🟢 Running' if st['running'] else '[-] Stopped'} (PIDs: {len(st['pids'])})")
        print(f"  • OAuth MCP URL  : {st['mcp_endpoint']}")
        mcp_res = ping_opera_mcp()
        print(f"  • MCP Auth State : HTTP {mcp_res['status']} ({mcp_res['message']})")
    elif args.command == "mcp-ping":
        res = ping_opera_mcp()
        print("Opera MCP Response:", json.dumps(res, indent=2))
    elif args.command == "launch":
        launch_opera_neon_with_cdp(port=args.port, url=args.url)


if __name__ == "__main__":
    main()
