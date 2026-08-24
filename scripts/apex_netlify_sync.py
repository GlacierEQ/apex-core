#!/usr/bin/env python3
"""
APEX NETLIFY PORTAL & CASE VISUALIZER DEPLOYER
Deploy live case dashboards, exhibit portals, and legal intelligence to Netlify.
"""

import argparse
import io
import json
import os
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

NETLIFY_TOKEN = os.getenv("NETLIFY_AUTH_TOKEN", "nfp_QkyDpJGgRXf5xR14o96vRaQzHSWMaqFG5db4")


def get_sites():
    req = urllib.request.Request(
        "https://api.netlify.com/api/v1/sites",
        headers={"Authorization": f"Bearer {NETLIFY_TOKEN}"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def deploy_folder_to_site(site_id: str, folder_path: Path) -> dict:
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    # Create in-memory zip
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in folder_path.rglob("*"):
            if file.is_file():
                rel_path = file.relative_to(folder_path)
                zf.write(file, arcname=str(rel_path))

    zip_bytes = zip_buf.getvalue()

    url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys"
    req = urllib.request.Request(
        url,
        data=zip_bytes,
        headers={
            "Authorization": f"Bearer {NETLIFY_TOKEN}",
            "Content-Type": "application/zip",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="APEX Netlify Deployer")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="List all active Netlify sites")

    deploy_p = subparsers.add_parser("deploy", help="Deploy directory to a Netlify site")
    deploy_p.add_argument("folder", help="Path to build/dist directory")
    deploy_p.add_argument("--site", "-s", default="casey-barton-glaciereq", help="Site name or ID")

    args = parser.parse_args()

    if args.command == "list" or not args.command:
        sites = get_sites()
        print("=" * 80)
        print("🌐 ACTIVE GLACIEREQ NETLIFY SITES")
        print("=" * 80)
        for s in sites:
            name = s.get("name")
            url = s.get("ssl_url") or s.get("url")
            sid = s.get("id")
            print(f"  • {name:<35} : {url} (ID: {sid})")
    elif args.command == "deploy":
        sites = get_sites()
        target_site = next((s for s in sites if s.get("name") == args.site or s.get("id") == args.site), None)
        if not target_site:
            print(f"[-] Site '{args.site}' not found.")
            sys.exit(1)

        print(f"Deploying {args.folder} to {target_site.get('name')} ({target_site.get('id')})...")
        res = deploy_folder_to_site(target_site.get("id"), Path(args.folder))
        print("✓ Deploy Complete!")
        print(f"  Live URL: {res.get('ssl_url') or res.get('url')}")


if __name__ == "__main__":
    main()
