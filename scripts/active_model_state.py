#!/usr/bin/env python3
"""
APEX ACTIVE MODEL STATE CONTROLLER FOR ANTIGRAVITY CLI
Standard: Dynamic model switching inside AGY sessions across OpenRouter free loadout, MiMo, and OpenCode.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

STATE_FILE = Path("/Users/kcbflux/.gemini/antigravity-cli/active_model_engine.json")

MODEL_ALIASES: Dict[str, Dict[str, Any]] = {
    "mimo": {
        "id": "xiaomi/mimo-v2.5-pro",
        "name": "Xiaomi MiMo v2.5 Pro (1.05M ctx Multimodal Audio/Video/Photo)",
        "multimodal": True,
        "context_length": 1050000,
        "type": "openrouter",
    },
    "mimo-pro": {
        "id": "xiaomi/mimo-v2.5-pro",
        "name": "Xiaomi MiMo v2.5 Pro (1.05M ctx Multimodal)",
        "multimodal": True,
        "context_length": 1050000,
        "type": "openrouter",
    },
    "r1": {
        "id": "deepseek/deepseek-r1:free",
        "name": "DeepSeek R1 Reasoning (Free)",
        "multimodal": False,
        "context_length": 163840,
        "type": "openrouter",
    },
    "deepseek": {
        "id": "deepseek/deepseek-chat:free",
        "name": "DeepSeek V3 671B (Free)",
        "multimodal": False,
        "context_length": 65536,
        "type": "openrouter",
    },
    "llama": {
        "id": "meta-llama/llama-3.3-70b-instruct:free",
        "name": "Meta Llama 3.3 70B Instruct (Free)",
        "multimodal": False,
        "context_length": 131072,
        "type": "openrouter",
    },
    "qwen": {
        "id": "qwen/qwen-2.5-coder-32b-instruct:free",
        "name": "Qwen 2.5 Coder 32B (Free)",
        "multimodal": False,
        "context_length": 32768,
        "type": "openrouter",
    },
    "nemotron": {
        "id": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "name": "NVIDIA Nemotron 3 Ultra 550B (Free)",
        "multimodal": False,
        "context_length": 976000,
        "type": "openrouter",
    },
    "dots": {
        "id": "dots-studio/dots-3-note-preview:free",
        "name": "Dots-3-Note Preview (Free · 500k ctx)",
        "multimodal": False,
        "context_length": 500000,
        "type": "openrouter",
    },
    "gemini-free": {
        "id": "google/gemini-2.0-flash-exp:free",
        "name": "Google Gemini 2.0 Flash Exp (Free · 1M ctx)",
        "multimodal": True,
        "context_length": 1048576,
        "type": "openrouter",
    },
    "opencode": {
        "id": "opencode-zen",
        "name": "OpenCode Zen Local Runtime",
        "multimodal": False,
        "context_length": 128000,
        "type": "local_cli",
    },
    "default": {
        "id": "default",
        "name": "Antigravity Native Gemini Brain",
        "multimodal": True,
        "context_length": 1048576,
        "type": "native",
    },
}


def get_active_state() -> Dict[str, Any]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "active_model_id": "xiaomi/mimo-v2.5-pro",
        "alias": "mimo",
        "name": "Xiaomi MiMo v2.5 Pro (1.05M ctx Multimodal Audio/Video/Photo)",
        "multimodal": True,
        "type": "openrouter",
        "last_switched_utc": time.time(),
    }


def set_active_model(alias_or_id: str) -> Dict[str, Any]:
    key = alias_or_id.strip().lower()
    matched: Optional[Dict[str, Any]] = None

    if key in MODEL_ALIASES:
        matched = MODEL_ALIASES[key]
        matched_alias = key
    else:
        for a_key, info in MODEL_ALIASES.items():
            if info["id"].lower() == key or key in info["id"].lower():
                matched = info
                matched_alias = a_key
                break

    if not matched:
        # Custom model ID passed directly
        matched = {
            "id": alias_or_id.strip(),
            "name": alias_or_id.strip(),
            "multimodal": "mimo" in key or "vision" in key or "gemini" in key,
            "context_length": 128000,
            "type": "openrouter",
        }
        matched_alias = alias_or_id.strip()

    state = {
        "active_model_id": matched["id"],
        "alias": matched_alias,
        "name": matched["name"],
        "multimodal": matched.get("multimodal", False),
        "context_length": matched.get("context_length", 128000),
        "type": matched.get("type", "openrouter"),
        "last_switched_utc": time.time(),
    }

    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception:
        pass

    return state


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "get":
            print(json.dumps(get_active_state(), indent=2))
        elif arg == "set" and len(sys.argv) > 2:
            new_state = set_active_model(sys.argv[2])
            print(f"✅ Active model switched to: {new_state['name']} ({new_state['active_model_id']})")
    else:
        print(json.dumps(get_active_state(), indent=2))
