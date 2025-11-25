#!/usr/bin/env python3
"""
SVG Search Built-In Self Test (BIST)

Demonstrates usage of the SVG search functionality and outputs results to ./tmp/svg_search/
"""

import subprocess
import sys
from pathlib import Path


def run_search(query: str, source: str = None, limit: int = 3):
    """Run an SVG search and display results."""
    output_dir = Path("./tmp/svg_search")

    print(f"\n{'='*60}")
    print(f"Test: Searching for '{query}'" + (f" in {source}" if source else " (all sources)"))
    print(f"{'='*60}\n")

    cmd = [
        "python",
        ".claude/skills/svg_getter/scripts/svg_search.py",
        "--query",
        query,
        "--output",
        str(output_dir),
        "--limit",
        str(limit),
        "--verbose",
    ]

    if source:
        cmd.extend(["--source", source])

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr, file=sys.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running search: {e}", file=sys.stderr)
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr, file=sys.stderr)
        return False


def list_downloaded_files():
    """List all downloaded SVG files."""
    output_dir = Path("./tmp/svg_search")

    if not output_dir.exists():
        print("\nNo output directory found.")
        return

    svg_files = list(output_dir.glob("*.svg"))

    if not svg_files:
        print("\nNo SVG files found in output directory.")
        return

    print(f"\n{'='*60}")
    print(f"Downloaded Files ({len(svg_files)} total)")
    print(f"{'='*60}\n")

    for svg_file in sorted(svg_files):
        size = svg_file.stat().st_size
        print(f"  {svg_file.name:40} ({size:,} bytes)")

    print(f"\nAll files saved to: {output_dir.absolute()}")


def main():
    """Run a series of demo searches."""
    print("SVG Search Built-In Self Test (BIST)")
    print("=" * 60)
    print("This script demonstrates the SVG search functionality")
    print("and saves results to ./tmp/svg_search/")
    print("=" * 60)

    # Clean up previous test results
    output_dir = Path("./tmp/svg_search")
    if output_dir.exists():
        for file in output_dir.glob("*.svg"):
            file.unlink()
        print(f"\nCleaned up previous test files from {output_dir}")

    # Test 1: Search all sources for "user" icon
    run_search("user", limit=2)

    # Test 2: Search Heroicons for "calendar" icon
    run_search("calendar", source="heroicons", limit=2)

    # Test 3: Search Lucide for "arrow" icon
    run_search("arrow", source="lucide", limit=2)

    # Test 4: Search Bootstrap Icons for "home" icon
    run_search("home", source="bootstrap", limit=2)

    # Test 5: Search Feather Icons for "check" icon
    run_search("check", source="feather", limit=2)

    # List all downloaded files
    list_downloaded_files()

    print("\n" + "=" * 60)
    print("BIST Complete!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
