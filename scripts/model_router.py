#!/usr/bin/env python3
"""
APEX UNIFIED MODEL ROUTER & FREE LOADOUT DISPATCHER
Standard: Multi-model expansion bridging OpenRouter Free Tier, OpenCode Zen, Cline, and KiloCode.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

GATEWAY_PATH = Path("/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/MCP_SERVERS/openrouter-free-gateway")
if str(GATEWAY_PATH) not in sys.path:
    sys.path.insert(0, str(GATEWAY_PATH))

from server import (
    chat_openrouter,
    compress_kilocode_context,
    execute_opencode_zen,
    list_free_models,
)


def cmd_list_free() -> int:
    models = list_free_models()
    print("=" * 70)
    print(f"APEX FREE MODEL LOADOUT ({len(models)} Models Available)")
    print("=" * 70)
    for idx, m in enumerate(models, start=1):
        ctx = m.get("context_length", 0)
        ctx_k = f"{ctx // 1024}k" if ctx >= 1024 else f"{ctx}"
        print(f"[{idx:02d}] {m.get('id')} ({ctx_k} ctx)")
        if m.get("description"):
            desc = m["description"][:90] + ("..." if len(m["description"]) > 90 else "")
            print(f"     └─ {desc}")
    print("=" * 70)
    return 0


def cmd_chat(args: argparse.Namespace) -> int:
    print(f"[*] Dispatching prompt to {args.model} via OpenRouter...")
    res = chat_openrouter(
        model=args.model,
        prompt=args.prompt,
        system_prompt=args.system or "",
        temperature=args.temperature,
    )
    if res.get("status") == "success":
        print(f"\n=== RESPONSE ({res.get('model_used')}) ===\n")
        print(res.get("response"))
        print("\n" + "=" * 50)
        return 0
    else:
        print(f"❌ Error: {res.get('message')}")
        return 1


def cmd_opencode(args: argparse.Namespace) -> int:
    print(f"[*] Running OpenCode Zen task: {args.task}")
    res = execute_opencode_zen(task_prompt=args.task)
    if res.get("status") == "success":
        print(res.get("stdout", ""))
        return 0
    else:
        print(f"❌ OpenCode error: {res.get('stderr') or res.get('message')}")
        return 1


def cmd_optimize(args: argparse.Namespace) -> int:
    raw_text = Path(args.file).read_text(encoding="utf-8") if args.file else args.text
    if not raw_text:
        print("❌ No input text provided to optimize.")
        return 1

    opt = compress_kilocode_context(raw_text, target_ratio=args.ratio)
    print("=" * 50)
    print("KILOCODE TOKEN OPTIMIZATION RECEIPT")
    print("=" * 50)
    print(f"Original Chars:     {opt['original_chars']}")
    print(f"Compressed Chars:   {opt['compressed_chars']}")
    print(f"Compression Ratio:  {opt['compression_ratio'] * 100:.1f}%")
    print(f"Approx Tokens Saved: ~{opt['tokens_saved_approx']}")
    print("=" * 50)
    if args.output:
        Path(args.output).write_text(opt["text"], encoding="utf-8")
        print(f"[+] Compressed output saved to {args.output}")
    return 0


import subprocess
from active_model_state import get_active_state, print_switcher_menu, set_active_model


def cmd_switch(args: argparse.Namespace) -> int:
    new_st = set_active_model(args.model)
    print(f"✅ Active model successfully switched to: {new_st['name']} ({new_st['active_model_id']})")
    print(f"   Engine: {new_st['engine']} | Context: {new_st['context_length']:,} tokens | Multimodal: {new_st['multimodal']}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    state = get_active_state()
    engine = state.get("engine", "openrouter")
    model_id = state.get("active_model_id", "xiaomi/mimo-v2.5-pro")

    print(f"[*] Executing via Active Model: {state.get('name')} [{engine.upper()}]...")

    if engine == "opencode":
        cmd = ["opencode", "run", "--model", model_id, args.prompt]
        p = subprocess.run(cmd, text=True)
        return p.returncode
    elif engine == "kilo":
        agent_name = state.get("alias", "").replace("kilo/", "")
        cmd = ["kilo", "run", "--agent", agent_name, args.prompt] if agent_name in ["zen", "coding", "analysis", "fast", "creative"] else ["kilo", "run", "--model", model_id, args.prompt]
        p = subprocess.run(cmd, text=True)
        return p.returncode
    else:
        res = chat_openrouter(model=model_id, prompt=args.prompt)
        if res.get("status") == "success":
            print(f"\n=== RESPONSE ({res.get('model_used')}) ===\n")
            print(res.get("response"))
            print("\n" + "=" * 50)
            return 0
        else:
            print(f"❌ Error: {res.get('message')}")
            return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="APEX Unified Model Router & Multi-Coder Dispatcher")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="Display interactive switcher menu of all models")
    subparsers.add_parser("list-free", help="List all available zero-cost OpenRouter models")

    sw_p = subparsers.add_parser("switch", help="Switch the active model engine (e.g. 'switch kilo/coding')")
    sw_p.add_argument("model", help="Model alias or identifier")

    run_p = subparsers.add_parser("run", help="Run a prompt through the active model")
    run_p.add_argument("prompt", help="Prompt text")

    chat_p = subparsers.add_parser("chat", help="Dispatch prompt to OpenRouter model")
    chat_p.add_argument("prompt", help="Prompt text")
    chat_p.add_argument("--model", "-m", default="xiaomi/mimo-v2.5-pro", help="Model identifier")
    chat_p.add_argument("--system", "-s", default="", help="System prompt")
    chat_p.add_argument("--temperature", "-t", type=float, default=0.7, help="Temperature")

    opencode_p = subparsers.add_parser("opencode", help="Run task with OpenCode Zen")
    opencode_p.add_argument("task", help="Task description")

    opt_p = subparsers.add_parser("optimize", help="Compress context with KiloCode optimizer")
    opt_p.add_argument("--file", "-f", help="Input file to compress")
    opt_p.add_argument("--text", help="Raw text to compress")
    opt_p.add_argument("--ratio", "-r", type=float, default=0.5, help="Target ratio")
    opt_p.add_argument("--output", "-o", help="Output file for compressed text")

    args = parser.parse_args()

    if not args.command or args.command == "list":
        print_switcher_menu()
        return 0
    elif args.command == "list-free":
        return cmd_list_free()
    elif args.command == "switch":
        return cmd_switch(args)
    elif args.command == "run":
        return cmd_run(args)
    elif args.command == "chat":
        return cmd_chat(args)
    elif args.command == "opencode":
        return cmd_opencode(args)
    elif args.command == "optimize":
        return cmd_optimize(args)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
