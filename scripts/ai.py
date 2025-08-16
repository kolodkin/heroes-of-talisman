#!/usr/bin/env python3
"""
AI Documentation Converter Script

Converts all .ai/**.md files to .cursor/rules/*.mdc files and concatenates them
to CLAUDE.md and AGENTS.md files in the project root.
"""

import os
from pathlib import Path
from typing import List, Tuple
import sys
import re

VERBOSE = "-v" in sys.argv or "--verbose" in sys.argv


def vlog(*args, **kwargs):
    """Print only if verbose flag is set."""
    if VERBOSE:
        print(*args, **kwargs)


def write_tidy(outfile, text: str) -> None:
    """Write text to file after trimming trailing whitespace at end of the whole text only."""
    content = re.sub(r"[ \t]+$", "", text)
    outfile.write(content)


def ensure_single_newline_at_eof(path: Path) -> None:
    """Ensure the file at 'path' ends with exactly one newline character."""
    try:
        with open(path, "r", encoding="utf-8") as infile:
            content = infile.read()
        # Remove all trailing whitespace/newlines, then add a single newline
        normalized = content.rstrip() + "\n"
        with open(path, "w", encoding="utf-8") as outfile:
            outfile.write(normalized)
    except FileNotFoundError:
        return


def find_ai_markdown_files(root_dir: Path) -> List[Path]:
    """Find all .md files in .ai directory and subdirectories."""
    ai_dir = root_dir / ".ai" / "rules"
    if not ai_dir.exists():
        return []

    return list(sorted(ai_dir.rglob("*.md")))


def convert_md_to_mdc(ai_files: List[Path], root_dir: Path) -> List[Tuple[Path, Path]]:
    """Convert .ai/**.md files to .cursor/rules/*.mdc files."""
    cursor_rules_dir = root_dir / ".cursor" / "rules"
    cursor_rules_dir.mkdir(parents=True, exist_ok=True)

    conversions = []

    for ai_file in ai_files:
        # Get relative path from .ai directory
        relative_path = ai_file.relative_to(root_dir / ".ai")

        # Create output filename: replace directory separators with hyphens
        output_name = str(relative_path).replace(os.sep, "-").replace(".md", ".mdc")
        # Add .mdc header to the top of each output .mdc file
        with (
            open(ai_file, "r", encoding="utf-8") as infile,
            open(cursor_rules_dir / output_name, "w", encoding="utf-8") as outfile,
        ):
            write_tidy(outfile, "---\n")
            write_tidy(outfile, f"description: {relative_path}\n")
            write_tidy(outfile, "globs:\n")
            write_tidy(outfile, "alwaysApply: true\n")
            write_tidy(outfile, "---\n\n")
            # Read the input file and write its contents to the output file, skipping the insertion marker lines.
            for line in infile:
                write_tidy(outfile, line)
        output_path = cursor_rules_dir / output_name

        # Ensure single trailing newline
        ensure_single_newline_at_eof(output_path)
        conversions.append((ai_file, output_path))
        vlog(f"Converted: {ai_file} -> {output_path}")

    return conversions


def concatenate_ai_markdown(ai_files: List[Path], root_dir: Path, output_filename: str) -> None:
    """Concatenate all .ai/**.md files into a single markdown file.

    The only difference between outputs should be the output filename.
    """
    out_path = root_dir / output_filename

    with open(out_path, "w", encoding="utf-8") as outfile:
        write_tidy(outfile, "# Agents Documentation\n")
        write_tidy(outfile, "This file contains agents guidlines.\n\n")

        for ai_file in ai_files:
            relative_path = ai_file.relative_to(root_dir)
            write_tidy(outfile, f"## {relative_path}\n\n")

            with open(ai_file, "r", encoding="utf-8") as infile:
                for line in infile:
                    write_tidy(outfile, line)
                write_tidy(outfile, "\n\n---\n\n")

    # Ensure single trailing newline
    ensure_single_newline_at_eof(out_path)
    vlog(f"Created: {out_path}")


def main():
    """Main function to execute the conversion process."""
    root_dir = Path(__file__).parent.parent.resolve()
    vlog(f"Working directory: {root_dir}")

    # Find all .ai markdown files
    ai_files = find_ai_markdown_files(root_dir)
    if not ai_files:
        vlog("No .ai/**.md files found.")
        return

    vlog(f"Found {len(ai_files)} .ai markdown files:")
    for ai_file in ai_files:
        vlog(f"  - {ai_file.relative_to(root_dir)}")

    # Convert .md to .mdc files
    vlog("\nConverting to .cursor/rules/*.mdc files...")
    conversions = convert_md_to_mdc(ai_files, root_dir)

    # Concatenate unified docs to both outputs (only filename differs)
    vlog("\nCreating CLAUDE.md...")
    concatenate_ai_markdown(ai_files, root_dir, "CLAUDE.md")

    vlog("\nCreating AGENTS.md...")
    concatenate_ai_markdown(ai_files, root_dir, "AGENTS.md")

    vlog(f"\nConversion complete! Processed {len(ai_files)} files.")


if __name__ == "__main__":
    main()
