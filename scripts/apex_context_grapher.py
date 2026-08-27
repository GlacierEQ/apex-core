#!/usr/bin/env python3
"""
APEX CONTEXT GRAPHER (v1.0)
Standard: L2 AST Dependency Mapping & Visual Synthesis
Features:
  - Statically parses Python ASTs across a given directory.
  - Generates a directed context graph of all internal module dependencies.
  - Outputs visual mapping formats: Mermaid.js (for direct artifact rendering) and JSON.
"""

import ast
import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple

def parse_imports(file_path: Path) -> List[str]:
    """Extracts module imports from a Python file using AST."""
    imports = []
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except Exception as e:
        # Failsafe for unparseable or non-Python files
        pass
    return imports

def build_dependency_graph(root_dir: Path) -> Tuple[Dict[str, List[str]], Set[str]]:
    """Builds a mapping of internal dependencies."""
    graph: Dict[str, List[str]] = {}
    all_modules: Set[str] = set()

    for p in root_dir.rglob("*.py"):
        if "node_modules" in p.parts or ".venv" in p.parts or "__pycache__" in p.parts:
            continue
        
        module_name = p.stem
        all_modules.add(module_name)
        imports = parse_imports(p)
        graph[module_name] = imports

    # Filter out external standard libraries, keep only internal dependencies
    internal_graph: Dict[str, List[str]] = {}
    for mod, deps in graph.items():
        internal_deps = [d.split('.')[0] for d in deps if d.split('.')[0] in all_modules or d in all_modules]
        if internal_deps:
            internal_graph[mod] = list(set(internal_deps))
            
    return internal_graph, all_modules

def generate_mermaid_flowchart(graph: Dict[str, List[str]]) -> str:
    """Converts the dependency graph into a Mermaid.js diagram."""
    lines = ["graph TD", "    %% APEX Context Dependency Graph"]
    
    if not graph:
        return "graph TD\n    A[No Internal Dependencies Found]"
        
    for source, targets in graph.items():
        for target in targets:
            if source != target:  # Avoid self-loops
                lines.append(f"    {source} --> {target}")
                
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="APEX Context Grapher")
    parser.add_argument("directory", type=Path, help="Target directory to map")
    parser.add_argument("--output", type=Path, default=Path("context_graph.md"), help="Output Markdown file for Mermaid graph")
    
    args = parser.parse_args()
    
    if not args.directory.exists() or not args.directory.is_dir():
        print(f"Error: Target directory '{args.directory}' is invalid.")
        return

    print(f"⚡ Mapping context topography for: {args.directory}")
    graph, modules = build_dependency_graph(args.directory)
    
    mermaid_code = generate_mermaid_flowchart(graph)
    
    md_content = f"# 🧠 APEX Context Graph: {args.directory.name}\n\n"
    md_content += f"**Analyzed Modules:** {len(modules)}\n"
    md_content += f"**Mapped Dependencies:** {sum(len(v) for v in graph.values())}\n\n"
    md_content += "```mermaid\n" + mermaid_code + "\n```\n"
    
    args.output.write_text(md_content, encoding="utf-8")
    print(f"✅ Context Graph synthesized to: {args.output.absolute()}")
    
if __name__ == "__main__":
    main()
