#!/usr/bin/env python3
"""
Trace all imports starting from an entrypoint file to identify used and unused files.
"""

import re
import sys
from pathlib import Path
from typing import Set


def extract_imports(file_path: Path) -> Set[Path]:
    """Extract all import paths from a JavaScript/JSX file."""
    if not file_path.exists():
        return set()

    try:
        content = file_path.read_text()
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return set()

    imports = set()

    # Match various import patterns:
    # import ... from "path"
    # import ... from 'path'
    # import "path"
    # import 'path'
    import_patterns = [
        r'import\s+.*?\s+from\s+["\']([^"\']+)["\']',  # import X from "path"
        r'import\s+["\']([^"\']+)["\']',  # import "path"
    ]

    for pattern in import_patterns:
        for match in re.finditer(pattern, content):
            import_path = match.group(1)

            # Skip node_modules and external packages
            if not import_path.startswith('.'):
                continue

            # Resolve relative path
            resolved = resolve_import_path(file_path.parent, import_path)
            if resolved:
                imports.add(resolved)

    return imports


def resolve_import_path(base_dir: Path, import_path: str) -> Path | None:
    """Resolve a relative import path to an absolute file path."""
    # Handle relative paths
    if import_path.startswith('./') or import_path.startswith('../'):
        candidate = (base_dir / import_path).resolve()
    else:
        return None

    # Try various extensions if no extension provided
    extensions = ['', '.js', '.jsx', '.css', '.module.css']

    for ext in extensions:
        file_path = Path(str(candidate) + ext)
        if file_path.exists() and file_path.is_file():
            return file_path

    # Check if it's a directory with index file
    if candidate.is_dir():
        for index_name in ['index.js', 'index.jsx']:
            index_path = candidate / index_name
            if index_path.exists():
                return index_path

    return None


def trace_imports(entrypoint: Path, src_dir: Path) -> Set[Path]:
    """Recursively trace all imports starting from entrypoint."""
    visited = set()
    to_visit = {entrypoint}

    while to_visit:
        current = to_visit.pop()

        if current in visited:
            continue

        visited.add(current)

        # Extract imports from current file
        imports = extract_imports(current)

        # Add unvisited imports to queue
        for imp in imports:
            if imp not in visited:
                to_visit.add(imp)

    return visited


def find_all_source_files(src_dir: Path) -> Set[Path]:
    """Find all JavaScript/JSX/CSS files in src directory."""
    extensions = {'.js', '.jsx', '.css'}
    files = set()

    for file_path in src_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix in extensions:
            files.add(file_path)

    return files


def main():
    # Get project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    src_dir = project_root / 'src'
    entrypoint = src_dir / 'main.jsx'

    if not entrypoint.exists():
        print(f"Error: Entrypoint {entrypoint} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Tracing imports from {entrypoint.relative_to(project_root)}...")

    # Trace all used files
    used_files = trace_imports(entrypoint, src_dir)

    # Find all source files
    all_files = find_all_source_files(src_dir)

    # Calculate unused files
    unused_files = all_files - used_files

    # Print results
    print(f"\n=== USED FILES ({len(used_files)}) ===")
    for file in sorted(used_files):
        print(f"  {file.relative_to(project_root)}")

    print(f"\n=== UNUSED FILES ({len(unused_files)}) ===")
    for file in sorted(unused_files):
        print(f"  {file.relative_to(project_root)}")

    # Summary
    print(f"\nSummary:")
    print(f"  Total files: {len(all_files)}")
    print(f"  Used files: {len(used_files)}")
    print(f"  Unused files: {len(unused_files)}")


if __name__ == '__main__':
    main()
