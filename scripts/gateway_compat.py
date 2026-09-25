#!/usr/bin/env python3
"""Compatibility adapters for the current OpenRouter gateway contract.

The recovered APEX scripts historically called ``chat_openrouter`` and
``chat_novita_ai`` helpers that returned a result dictionary.  The current
FastMCP gateway exposes ``chat(model, messages, ...)`` and returns text.  Keep
that boundary in one module so callers retain their existing behavior without
changing the gateway or inventing a second provider path.
"""

from __future__ import annotations

from typing import Any, Dict, List

from server import chat as _gateway_chat
from server import list_free_models as _list_free_models


def list_free_models() -> List[Dict[str, Any]]:
    """Proxy the current gateway's model-discovery function."""
    return _list_free_models()


def chat_openrouter(
    *,
    model: str,
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.7,
    max_tokens: int = 2048,
    top_p: float = 1.0,
    **_: Any,
) -> Dict[str, Any]:
    """Call the current gateway while preserving the legacy result shape."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = _gateway_chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )
    except Exception as exc:  # preserve the callers' non-raising fallback path
        return {
            "status": "error",
            "message": str(exc),
            "response": "",
            "model_used": model,
            "usage": {},
        }

    return {
        "status": "success",
        "message": "",
        "response": response,
        "model_used": model,
        "usage": {},
    }


def chat_novita_ai(**kwargs: Any) -> Dict[str, Any]:
    """Retain the legacy Novita helper name using the same provider path."""
    return chat_openrouter(**kwargs)
