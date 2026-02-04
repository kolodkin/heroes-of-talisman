---
name: svg-getter
description: Search and download SVG icons and illustrations from free online sources (Heroicons, Lucide, Feather, Bootstrap Icons, Tabler). Use when working with SVG icons, need UI graphics, or want to add icons to a project. Requires httpx package.
---

# SVG Search and Fetch

Search and download SVG icons and illustrations from free online sources.

## When to Use

Use this skill when the user needs to:

- Find SVG icons for their project
- Download specific icons from free libraries
- Search for illustrations or graphics
- Get SVG code for UI elements
- Browse available icons from popular icon libraries

## Supported Sources

- **Heroicons** - Clean, MIT-licensed icons by Tailwind Labs
- **Lucide** - Open source icon library with consistent design
- **Feather Icons** - Minimalist open source icons
- **Bootstrap Icons** - 2,000+ free icons from Bootstrap
- **Tabler Icons** - 5,000+ free MIT-licensed icons

## How to Search

To search for SVG icons, use the Python script with these parameters:

```bash
python .claude/skills/svg_getter/scripts/svg_search.py --query "SEARCH_TERM" [--source SOURCE] [--output OUTPUT_DIR] [--limit N]
```

**Parameters:**

- `--query` (required): What to search for (e.g., "user", "calendar", "arrow")
- `--source` (optional): Specific source (heroicons, lucide, feather, bootstrap, tabler). If omitted, searches all sources.
- `--output` (optional): Directory to save SVGs (default: src/assets/icons)
- `--limit` (optional): Max results to return (default: 5)

## Examples

Search all sources for user icons:

```bash
python .claude/skills/svg_getter/scripts/svg_search.py --query "user"
```

Search only Heroicons for calendar icon:

```bash
python .claude/skills/svg_getter/scripts/svg_search.py --query "calendar" --source heroicons
```

Get arrow icons and save to custom directory:

```bash
python .claude/skills/svg_getter/scripts/svg_search.py --query "arrow" --output public/icons --limit 10
```

## Output

The script will:

1. Search the specified sources for matching icons
2. Display found icons with their names and sources
3. Download SVG files to the output directory
4. Return a summary with file paths and usage information

## Requirements

- Python 3.7+
- httpx package: `uv add httpx` or `pip install httpx`
