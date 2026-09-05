#!/usr/bin/env python3
"""
APEX AIR-GAPPED SENSITIVE DATA SCRUBBER & PII SANITIZER
Standard: Pre-flight sanitization for SSNs, credit cards, private API keys, and internal dockets before outbound dispatch.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple


class ApexDataScrubber:
    """
    Sanitizes sensitive information from prompts, logs, and telemetry.
    """

    PATTERNS: List[Tuple[str, re.Pattern, str]] = [
        ("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED_SSN]"),
        ("CREDIT_CARD", re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"), "[REDACTED_CREDIT_CARD]"),
        ("OPENAI_KEY", re.compile(r"\bsk-[a-zA-Z0-9]{32,64}\b"), "[REDACTED_API_KEY]"),
        ("AWS_KEY", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[REDACTED_AWS_KEY]"),
        ("GITHUB_TOKEN", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{36,255}\b"), "[REDACTED_GITHUB_TOKEN]"),
        ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"), "[REDACTED_EMAIL]"),
    ]

    @classmethod
    def sanitize(cls, text: str) -> Tuple[str, Dict[str, int]]:
        counts: Dict[str, int] = {}
        sanitized = text
        for name, pattern, replacement in cls.PATTERNS:
            matches = pattern.findall(sanitized)
            if matches:
                counts[name] = len(matches)
                sanitized = pattern.sub(replacement, sanitized)
        return sanitized, counts



SCRUB_PATTERNS = [
    (r"sk-ant-[a-zA-Z0-9_\-]{30,}", "[REDACTED_ANTHROPIC_KEY]"),
    (r"sk-proj-[a-zA-Z0-9_\-]{30,}", "[REDACTED_OPENAI_KEY]"),
    (r"AIzaSy[a-zA-Z0-9_\-]{30,}", "[REDACTED_GOOGLE_KEY]"),
    (r"AKIA[0-9A-Z]{16}", "[REDACTED_AWS_ACCESS_KEY]"),
    (r"-----BEGIN (RSA|EC|OPENSSH|DSA|PRIVATE) KEY-----[\s\S]*?-----END \1 KEY-----", "[REDACTED_PRIVATE_KEY]"),
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[REDACTED_EMAIL]"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]"),
    (r"\b(?:\+?1[-.]?)?\(?[2-9]\d{2}\)?[-.]?\d{3}[-.]?\d{4}\b", "[REDACTED_PHONE]"),
]


def scrub_text(content: str) -> Tuple[str, int]:
    """Scrub sensitive keys, tokens, and PII patterns returning (cleaned_text, count)."""
    scrubbed = content
    total_redactions = 0
    for pattern, replacement in SCRUB_PATTERNS:
        matches = len(re.findall(pattern, scrubbed))
        if matches > 0:
            total_redactions += matches
            scrubbed = re.sub(pattern, replacement, scrubbed)
    return scrubbed, total_redactions


if __name__ == "__main__":
    sample = "Test prompt containing SSN 000-12-3456 and email user@example.com with key sk-9NFouS05ZeDtJpoTsRRWy0hhOvPsjvFwxg9NiF4OUpD2aULz8Vc3RgZDX5jEvY0p"
    cleaned, stats = ApexDataScrubber.sanitize(sample)
    print("Original:", sample)
    print("Cleaned :", cleaned)
    print("Stats   :", stats)
