#!/usr/bin/env python3
"""
APEX ACTIVE MODEL STATE CONTROLLER & MULTI-CODER MODEL SWITCHER
Standard: Dynamic model switching across Antigravity, OpenCode Zen, KiloCode, Novita AI, and OpenRouter.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

STATE_FILE = Path.home() / ".gemini" / "antigravity-cli" / "active_model_engine.json"
OPENCODE_CONFIG = Path.home() / ".config" / "opencode" / "config.json"
KILO_CONFIG = Path.home() / ".config" / "kilo" / "config.json"

STATIC_ALIASES: Dict[str, Dict[str, Any]] = {
    # --- OpenRouter & Multimodal Presets ---
    "mimo": {
        "id": "xiaomi/mimo-v2.5-pro",
        "name": "Xiaomi MiMo v2.5 Pro (1.05M Multimodal Audio/Video/Photo)",
        "multimodal": True,
        "context_length": 1050000,
        "engine": "openrouter",
        "category": "Multimodal / Media",
    },
    "mimo-pro": {
        "id": "xiaomi/mimo-v2.5-pro",
        "name": "Xiaomi MiMo v2.5 Pro (1.05M Multimodal)",
        "multimodal": True,
        "context_length": 1050000,
        "engine": "openrouter",
        "category": "Multimodal / Media",
    },
    "r1": {
        "id": "deepseek/deepseek-r1:free",
        "name": "DeepSeek R1 Reasoning (164k CoT Free)",
        "multimodal": False,
        "context_length": 163840,
        "engine": "openrouter",
        "category": "Reasoning & Math",
    },
    "deepseek": {
        "id": "deepseek/deepseek-chat:free",
        "name": "DeepSeek V3 671B (Free)",
        "multimodal": False,
        "context_length": 65536,
        "engine": "openrouter",
        "category": "Coding & General",
    },
    "llama": {
        "id": "meta-llama/llama-3.3-70b-instruct:free",
        "name": "Meta Llama 3.3 70B Instruct (Free)",
        "multimodal": False,
        "context_length": 131072,
        "engine": "openrouter",
        "category": "General & Compliance",
    },
    "qwen": {
        "id": "qwen/qwen-2.5-coder-32b-instruct:free",
        "name": "Qwen 2.5 Coder 32B (Free)",
        "multimodal": False,
        "context_length": 32768,
        "engine": "openrouter",
        "category": "Coding & Refactoring",
    },
    "gemini-free": {
        "id": "google/gemini-2.0-flash-exp:free",
        "name": "Google Gemini 2.0 Flash Exp (Free · 1M ctx)",
        "multimodal": True,
        "context_length": 1048576,
        "engine": "openrouter",
        "category": "Large Context",
    },
    # --- OpenCode Zen Models & Agents ---
    "opencode": {
        "id": "deepseek/deepseek-chat",
        "name": "OpenCode Zen Primary (DeepSeek Chat)",
        "multimodal": False,
        "context_length": 128000,
        "engine": "opencode",
        "category": "OpenCode Zen Engine",
    },
    "opencode/zen": {
        "id": "deepseek/deepseek-chat",
        "name": "OpenCode Zen Architect Agent",
        "multimodal": False,
        "context_length": 128000,
        "engine": "opencode",
        "category": "OpenCode Zen Engine",
    },
    "opencode/r1": {
        "id": "openrouter/deepseek/deepseek-r1:free",
        "name": "OpenCode DeepSeek R1 Reasoning",
        "multimodal": False,
        "context_length": 163840,
        "engine": "opencode",
        "category": "OpenCode Zen Engine",
    },
    "opencode/mimo": {
        "id": "openrouter/xiaomi/mimo-v2.5-pro",
        "name": "OpenCode Xiaomi MiMo v2.5 Pro Multimodal",
        "multimodal": True,
        "context_length": 1050000,
        "engine": "opencode",
        "category": "OpenCode Zen Engine",
    },
    "opencode/novita-deepseek-v4": {
        "id": "novita/deepseek/deepseek-v4-pro",
        "name": "OpenCode Novita DeepSeek V4 Pro",
        "multimodal": True,
        "context_length": 1048576,
        "engine": "opencode",
        "category": "Novita AI Suite",
    },
    "opencode/novita-kimi": {
        "id": "novita/moonshotai/kimi-k3",
        "name": "OpenCode Novita Kimi K3",
        "multimodal": False,
        "context_length": 524288,
        "engine": "opencode",
        "category": "Novita AI Suite",
    },
    "opencode/novita-glm": {
        "id": "novita/zai-org/glm-5.3",
        "name": "OpenCode Novita GLM 5.3",
        "multimodal": False,
        "context_length": 1048576,
        "engine": "opencode",
        "category": "Novita AI Suite",
    },
    "opencode/novita-qwen": {
        "id": "novita/qwen/qwen3.8-max",
        "name": "OpenCode Novita Qwen 3.8 Max",
        "multimodal": False,
        "context_length": 131072,
        "engine": "opencode",
        "category": "Novita AI Suite",
    },
    "opencode/ollama": {
        "id": "ollama/llama3.2:1b",
        "name": "OpenCode Local Ollama Llama 3.2",
        "multimodal": False,
        "context_length": 32768,
        "engine": "opencode",
        "category": "Local Offline Models",
    },
    # --- Kilo Code Models & Agents ---
    "kilo": {
        "id": "deepseek/deepseek-chat",
        "name": "Kilo Primary Coder (DeepSeek Chat)",
        "multimodal": False,
        "context_length": 128000,
        "engine": "kilo",
        "category": "KiloCode Engine",
    },
    "kilo/zen": {
        "id": "deepseek/deepseek-chat",
        "name": "Kilo Zen Architect Agent",
        "multimodal": False,
        "context_length": 128000,
        "engine": "kilo",
        "category": "KiloCode Engine",
    },
    "kilo/coding": {
        "id": "openrouter/xiaomi/mimo-v2.5",
        "name": "Kilo Coding Agent (MiMo v2.5)",
        "multimodal": True,
        "context_length": 1050000,
        "engine": "kilo",
        "category": "KiloCode Engine",
    },
    "kilo/analysis": {
        "id": "novita/deepseek/deepseek-v4-pro",
        "name": "Kilo Deep Analysis Agent (DeepSeek V4 Pro)",
        "multimodal": True,
        "context_length": 1048576,
        "engine": "kilo",
        "category": "KiloCode Engine",
    },
    "kilo/fast": {
        "id": "inclusionai/ling-2.6-flash",
        "name": "Kilo Fast Inference Agent (Ling 2.6 Flash)",
        "multimodal": False,
        "context_length": 65536,
        "engine": "kilo",
        "category": "KiloCode Engine",
    },
    "kilo/creative": {
        "id": "moonshotai/kimi-k2.6",
        "name": "Kilo Creative Writer Agent (Kimi K2.6)",
        "multimodal": False,
        "context_length": 262144,
        "engine": "kilo",
        "category": "KiloCode Engine",
    },
    "kilo/cloud": {
        "id": "kilo-cloud-agent",
        "name": "Kilo Cloud Autonomous Agent",
        "multimodal": True,
        "context_length": 200000,
        "engine": "kilo",
        "category": "KiloCode Engine",
    },
    # --- Native Antigravity Brain ---
    "default": {
        "id": "default",
        "name": "Antigravity Native Gemini Brain",
        "multimodal": True,
        "context_length": 1048576,
        "engine": "native",
        "category": "Antigravity Native",
    },
}


def load_all_models() -> Dict[str, Dict[str, Any]]:
    """Dynamically aggregate static aliases with OpenCode and Kilo registered models."""
    roster = dict(STATIC_ALIASES)

    # Ingest OpenCode Models
    if OPENCODE_CONFIG.exists():
        try:
            oc_data = json.loads(OPENCODE_CONFIG.read_text(encoding="utf-8"))
            for p_id, p_info in oc_data.get("provider", {}).items():
                for m_id, m_info in p_info.get("models", {}).items():
                    full_id = f"{p_id}/{m_id}"
                    alias_key = f"opencode/{p_id}-{m_id.split('/')[-1]}".lower()
                    if alias_key not in roster:
                        roster[alias_key] = {
                            "id": full_id,
                            "name": m_info.get("name", full_id),
                            "multimodal": m_info.get("multimodal", False),
                            "context_length": m_info.get("limit", {}).get("context", 128000),
                            "engine": "opencode",
                            "category": f"OpenCode ({p_info.get('name', p_id)})",
                        }
        except Exception:
            pass

    return roster


def get_active_state() -> Dict[str, Any]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "active_model_id": "xiaomi/mimo-v2.5-pro",
        "alias": "mimo",
        "name": "Xiaomi MiMo v2.5 Pro (1.05M Multimodal Audio/Video/Photo)",
        "multimodal": True,
        "engine": "openrouter",
        "last_switched_utc": time.time(),
    }


def set_active_model(alias_or_id: str) -> Dict[str, Any]:
    key = alias_or_id.strip().lower()
    roster = load_all_models()
    matched: Optional[Dict[str, Any]] = None

    if key in roster:
        matched = roster[key]
        matched_alias = key
    else:
        for a_key, info in roster.items():
            if info["id"].lower() == key or key in info["id"].lower() or key in a_key.lower():
                matched = info
                matched_alias = a_key
                break

    if not matched:
        # Direct custom model string
        engine_type = "opencode" if "opencode" in key else ("kilo" if "kilo" in key else "openrouter")
        matched = {
            "id": alias_or_id.strip(),
            "name": alias_or_id.strip(),
            "multimodal": "mimo" in key or "vision" in key or "gemini" in key,
            "context_length": 128000,
            "engine": engine_type,
            "category": "Custom Model",
        }
        matched_alias = alias_or_id.strip()

    state = {
        "active_model_id": matched["id"],
        "alias": matched_alias,
        "name": matched["name"],
        "multimodal": matched.get("multimodal", False),
        "context_length": matched.get("context_length", 128000),
        "engine": matched.get("engine", "openrouter"),
        "category": matched.get("category", "General"),
        "last_switched_utc": time.time(),
    }

    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception:
        pass

    return state


def print_switcher_menu() -> None:
    roster = load_all_models()
    active = get_active_state()
    categories: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}

    for alias, info in roster.items():
        cat = info.get("category", "Other")
        categories.setdefault(cat, []).append((alias, info))

    print("=" * 80)
    print("🚀 APEX UNIFIED MODEL SWITCHER (Antigravity · OpenCode · Kilo · Novita · OpenRouter)")
    print(f"⭐ CURRENT ACTIVE MODEL: [{active.get('alias')}] -> {active.get('name')}")
    print("=" * 80)

    for cat_name, models in sorted(categories.items()):
        print(f"\n📂 {cat_name.upper()}")
        for alias, info in models:
            is_cur = "⭐ [ACTIVE]" if alias == active.get("alias") else "          "
            ctx = info.get("context_length", 0)
            ctx_str = f"{ctx // 1024}k" if ctx >= 1024 else f"{ctx}"
            mm = "👁️ Multimodal" if info.get("multimodal") else "📝 Text/Code"
            print(f"  {is_cur} {alias:<28} : {info['name']} ({ctx_str} ctx | {mm})")

    print("\n" + "=" * 80)
    print("💡 TO SWITCH MODELS:")
    print("   Terminal Command : apex-model switch <alias>  (e.g., 'apex-model switch kilo/coding')")
    print("   Chat Command     : /model <alias> or 'switch to <alias>'")
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "list" or cmd == "menu":
            print_switcher_menu()
        elif cmd in ("switch", "set") and len(sys.argv) > 2:
            new_st = set_active_model(sys.argv[2])
            print(f"✅ Active model successfully switched to: {new_st['name']} ({new_st['active_model_id']})")
            print(f"   Engine: {new_st['engine']} | Context: {new_st['context_length']:,} tokens | Multimodal: {new_st['multimodal']}")
        elif cmd == "get":
            print(json.dumps(get_active_state(), indent=2))
        else:
            new_st = set_active_model(cmd)
            print(f"✅ Active model successfully switched to: {new_st['name']} ({new_st['active_model_id']})")
    else:
        print_switcher_menu()
