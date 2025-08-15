#!/usr/bin/env python3
"""
AI Documentation Converter Script

Converts all .ai/**.md files to .cursor/rules/*.mdc files and concatenates them
to CLAUDE.md and AGENTS.md files in the project root.
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple


def find_ai_markdown_files(root_dir: Path) -> List[Path]:
    """Find all .md files in .ai directory and subdirectories."""
    ai_dir = root_dir / ".ai"
    if not ai_dir.exists():
        return []

    return list(ai_dir.rglob("*.md"))


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
        output_path = cursor_rules_dir / output_name

        # Copy content and convert extension
        shutil.copy2(ai_file, output_path)
        conversions.append((ai_file, output_path))
        print(f"Converted: {ai_file} -> {output_path}")

    return conversions


def concatenate_to_claude_md(ai_files: List[Path], root_dir: Path) -> None:
    """Concatenate all .ai/**.md files to CLAUDE.md."""
    claude_md = root_dir / "CLAUDE.md"

    with open(claude_md, "w", encoding="utf-8") as outfile:
        outfile.write("# Claude AI Documentation\n\n")
        outfile.write("This file contains concatenated documentation from .ai/ directory.\n\n")

        for ai_file in ai_files:
            relative_path = ai_file.relative_to(root_dir)
            outfile.write(f"## {relative_path}\n\n")

            with open(ai_file, "r", encoding="utf-8") as infile:
                content = infile.read()
                outfile.write(content)
                outfile.write("\n\n---\n\n")

    print(f"Created: {claude_md}")


def concatenate_to_agents_md(ai_files: List[Path], root_dir: Path) -> None:
    """Concatenate all .ai/**.md files to AGENTS.md."""
    agents_md = root_dir / "AGENTS.md"

    with open(agents_md, "w", encoding="utf-8") as outfile:
        outfile.write("# AI Agents Documentation\n\n")
        outfile.write("This file contains agent-specific documentation from .ai/ directory.\n\n")

        for ai_file in ai_files:
            relative_path = ai_file.relative_to(root_dir)
            outfile.write(f"## {relative_path}\n\n")

            with open(ai_file, "r", encoding="utf-8") as infile:
                content = infile.read()
                outfile.write(content)
                outfile.write("\n\n---\n\n")

    print(f"Created: {agents_md}")


def main():
    """Main function to execute the conversion process."""
    root_dir = Path(__file__).parent.parent.resolve()
    print(f"Working directory: {root_dir}")

    # Find all .ai markdown files
    ai_files = find_ai_markdown_files(root_dir)
    if not ai_files:
        print("No .ai/**.md files found.")
        return

    print(f"Found {len(ai_files)} .ai markdown files:")
    for ai_file in ai_files:
        print(f"  - {ai_file.relative_to(root_dir)}")

    # Convert .md to .mdc files
    print("\nConverting to .cursor/rules/*.mdc files...")
    conversions = convert_md_to_mdc(ai_files, root_dir)

    # Concatenate to CLAUDE.md
    print("\nCreating CLAUDE.md...")
    concatenate_to_claude_md(ai_files, root_dir)

    # Concatenate to AGENTS.md
    print("\nCreating AGENTS.md...")
    concatenate_to_agents_md(ai_files, root_dir)

    print(f"\nConversion complete! Processed {len(ai_files)} files.")


if __name__ == "__main__":
    main()
