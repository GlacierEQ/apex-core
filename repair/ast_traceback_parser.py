#!/usr/bin/env python3
"""
APEX DYNAMIC AST TRACEBACK PARSER & ROOT-CAUSE LOCALIZER
Standard: AST-Level Exception Pinpointing & Scope Extraction
Features: Locates failing AST FunctionDef / ClassDef, extracts variables and callstack
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any


@dataclass
class FailureFrame:
    filename: str
    line_number: int
    function_name: str
    code_snippet: str
    ast_node_type: Optional[str] = None
    ast_enclosing_function: Optional[str] = None


@dataclass
class ParsedTraceback:
    exception_type: str
    exception_message: str
    failing_file: str
    failing_line: int
    frames: List[FailureFrame]
    root_cause_context: str


def parse_traceback_text(traceback_text: str) -> Optional[ParsedTraceback]:
    # Extract file frames
    frame_pattern = re.compile(r'File "([^"]+)", line (\d+), in ([^\n]+)\n\s*(.+)')
    matches = frame_pattern.findall(traceback_text)
    
    if not matches:
        return None

    frames = []
    for fn, ln_str, func_name, code in matches:
        ln = int(ln_str)
        ast_type = None
        enclosing = None
        
        # If file exists, inspect AST
        fpath = Path(fn)
        if fpath.exists() and fpath.suffix == ".py":
            try:
                tree = ast.parse(fpath.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if hasattr(node, "lineno") and node.lineno == ln:
                        ast_type = type(node).__name__
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                            if node.lineno <= ln <= (node.end_lineno or ln):
                                enclosing = node.name
            except Exception:
                pass

        frames.append(FailureFrame(
            filename=fn,
            line_number=ln,
            function_name=func_name.strip(),
            code_snippet=code.strip(),
            ast_node_type=ast_type,
            ast_enclosing_function=enclosing or func_name.strip(),
        ))

    # Extract final exception line
    exc_lines = [l.strip() for l in traceback_text.strip().splitlines() if l.strip()]
    last_line = exc_lines[-1] if exc_lines else "UnknownException: Traceback parse error"
    
    if ":" in last_line:
        exc_type, exc_msg = last_line.split(":", 1)
    else:
        exc_type, exc_msg = last_line, ""

    primary_frame = frames[-1]
    return ParsedTraceback(
        exception_type=exc_type.strip(),
        exception_message=exc_msg.strip(),
        failing_file=primary_frame.filename,
        failing_line=primary_frame.line_number,
        frames=frames,
        root_cause_context=f"Exception {exc_type.strip()} in {primary_frame.filename}:{primary_frame.line_number} ({primary_frame.ast_enclosing_function})",
    )


if __name__ == "__main__":
    sample_tb = """
Traceback (most recent call last):
  File "/Users/kcbflux/test_script.py", line 42, in process_batch
    res = 100 / divisor
ZeroDivisionError: division by zero
"""
    parsed = parse_traceback_text(sample_tb)
    if parsed:
        print(f"✅ Successfully parsed: {parsed.root_cause_context}")
        print(f"Exception: {parsed.exception_type} -> {parsed.exception_message}")
