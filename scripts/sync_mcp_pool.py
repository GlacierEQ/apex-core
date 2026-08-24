#!/usr/bin/env python3
"""
APEX UNIFIED MCP POOL SYNCHRONIZER
Standard: Single-source deployment of Light Local vs Heavy Remote MCP servers across Antigravity, OpenCode, Kilo, and Mermicorn.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

POOL_FILE = Path("/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/MCP_SERVERS/unified_mcp_pool.json")


def load_pool() -> Dict[str, Any]:
    if not POOL_FILE.exists():
        raise FileNotFoundError(f"Master pool file not found at {POOL_FILE}")
    return json.loads(POOL_FILE.read_text(encoding="utf-8"))


def build_antigravity_mcp_config(pool: Dict[str, Any]) -> Dict[str, Any]:
    """Compile MCP servers for Antigravity CLI format."""
    servers: Dict[str, Any] = {}

    # 1. Light Local Servers
    for name, s_info in pool["tiers"]["light_local"]["servers"].items():
        if s_info.get("command"):
            srv: Dict[str, Any] = {
                "command": s_info["command"],
                "args": s_info.get("args", []),
            }
            if s_info.get("env"):
                srv["env"] = s_info["env"]
            servers[name] = srv

    # 2. Heavy Remote Servers
    for name, s_info in pool["tiers"]["heavy_remote"]["servers"].items():
        if s_info.get("serverUrl"):
            srv = {
                "serverUrl": s_info["serverUrl"]
            }
            if s_info.get("authProviderType"):
                srv["authProviderType"] = s_info["authProviderType"]
            servers[name] = srv
        elif s_info.get("command"):
            srv = {
                "command": s_info["command"],
                "args": s_info.get("args", []),
            }
            if s_info.get("env"):
                srv["env"] = s_info["env"]
            servers[name] = srv

    # Preserve any existing datacloud extensions if present
    existing_file = Path.home() / ".gemini" / "config" / "mcp_config.json"
    if existing_file.exists():
        try:
            existing = json.loads(existing_file.read_text(encoding="utf-8")).get("mcpServers", {})
            for k, v in existing.items():
                if "antigravityide" in str(v) and k not in servers:
                    servers[k] = v
        except Exception:
            pass

    return {"mcpServers": servers}


def build_opencode_mcp_config(pool: Dict[str, Any]) -> Dict[str, Any]:
    """Compile MCP servers for OpenCode Zen format."""
    mcp: Dict[str, Any] = {}

    # Light Local
    for name, s_info in pool["tiers"]["light_local"]["servers"].items():
        cmd = s_info.get("command")
        args = s_info.get("args", [])
        if cmd:
            full_cmd = [cmd] + args if isinstance(cmd, str) else cmd + args
            mcp[name] = {
                "type": "local",
                "command": full_cmd,
                "enabled": True,
            }
            if s_info.get("env"):
                mcp[name]["environment"] = s_info["env"]

    # Heavy Remote
    for name, s_info in pool["tiers"]["heavy_remote"]["servers"].items():
        if s_info.get("serverUrl"):
            mcp[name] = {
                "type": "remote",
                "url": s_info["serverUrl"],
                "enabled": True,
            }
        elif s_info.get("command"):
            cmd = s_info.get("command")
            args = s_info.get("args", [])
            full_cmd = [cmd] + args if isinstance(cmd, str) else cmd + args
            mcp[name] = {
                "type": "local",
                "command": full_cmd,
                "enabled": True,
            }
            if s_info.get("env"):
                mcp[name]["environment"] = s_info["env"]

    return mcp


def build_kilo_mcp_config(pool: Dict[str, Any]) -> Dict[str, Any]:
    """Compile MCP servers for Kilo Hub format."""
    mcp: Dict[str, Any] = {}

    # Light Local
    for name, s_info in pool["tiers"]["light_local"]["servers"].items():
        cmd = s_info.get("command")
        args = s_info.get("args", [])
        if cmd:
            full_cmd = [cmd] + args if isinstance(cmd, str) else cmd + args
            mcp[name] = {
                "type": "local",
                "command": full_cmd,
                "enabled": True,
            }
            if s_info.get("env"):
                mcp[name]["environment"] = s_info["env"]

    # Heavy Remote
    for name, s_info in pool["tiers"]["heavy_remote"]["servers"].items():
        if s_info.get("serverUrl"):
            mcp[name] = {
                "type": "remote",
                "url": s_info["serverUrl"],
                "enabled": True,
            }
        elif s_info.get("command"):
            cmd = s_info.get("command")
            args = s_info.get("args", [])
            full_cmd = [cmd] + args if isinstance(cmd, str) else cmd + args
            mcp[name] = {
                "type": "local",
                "command": full_cmd,
                "enabled": True,
            }
            if s_info.get("env"):
                mcp[name]["environment"] = s_info["env"]

    return mcp


def sync_all() -> int:
    print("======================================================================")
    print("🔄 APEX UNIFIED MCP POOL SYNCHRONIZER (LIGHT LOCAL + HEAVY REMOTE)")
    print("======================================================================")

    pool = load_pool()
    local_count = len(pool["tiers"]["light_local"]["servers"])
    remote_count = len(pool["tiers"]["heavy_remote"]["servers"])

    print(f"Master Pool Loaded: {local_count} Light Local + {remote_count} Heavy Remote = {local_count + remote_count} Servers")

    # 1. Sync Antigravity
    ag_path = Path.home() / ".gemini" / "config" / "mcp_config.json"
    ag_data = build_antigravity_mcp_config(pool)
    ag_path.write_text(json.dumps(ag_data, indent=2), encoding="utf-8")
    print(f"  ✓ Synced Antigravity CLI MCP Config -> {ag_path} ({len(ag_data['mcpServers'])} servers)")

    # 2. Sync OpenCode
    oc_path = Path.home() / ".config" / "opencode" / "config.json"
    if oc_path.exists():
        oc_raw = json.loads(oc_path.read_text(encoding="utf-8"))
        oc_raw["mcp"] = build_opencode_mcp_config(pool)
        oc_path.write_text(json.dumps(oc_raw, indent=2), encoding="utf-8")
        print(f"  ✓ Synced OpenCode Zen MCP Config     -> {oc_path} ({len(oc_raw['mcp'])} servers)")

    # 3. Sync Kilo
    kilo_path = Path.home() / ".config" / "kilo" / "kilo.json"
    if kilo_path.exists():
        kilo_raw = json.loads(kilo_path.read_text(encoding="utf-8"))
        kilo_raw["mcp"] = build_kilo_mcp_config(pool)
        kilo_path.write_text(json.dumps(kilo_raw, indent=2), encoding="utf-8")
        print(f"  ✓ Synced Kilo MCP Hub Config         -> {kilo_path} ({len(kilo_raw['mcp'])} servers)")

    # 4. Sync Mermicorn (Scoped)
    mermi_path = Path.home() / "Dropbox-Cyber.lazer.mermicor" / "opencode.json"
    if mermi_path.exists():
        mermi_raw = json.loads(mermi_path.read_text(encoding="utf-8"))
        mermi_raw["mcp"] = build_opencode_mcp_config(pool)
        # Ensure filesystem is strictly scoped to Mermicorn
        mermi_raw["mcp"]["filesystem"] = {
            "type": "local",
            "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/Users/kcbflux/Dropbox-Cyber.lazer.mermicor"],
            "enabled": True
        }
        mermi_path.write_text(json.dumps(mermi_raw, indent=2), encoding="utf-8")
        print(f"  ✓ Synced Mermicorn Isolated Config   -> {mermi_path} (Scoped)")

    print("\n======================================================================")
    print("✅ UNIFIED MCP POOL SYNCHRONIZATION COMPLETE: 100% GREEN")
    print("======================================================================")
    return 0


if __name__ == "__main__":
    sys.exit(sync_all())
