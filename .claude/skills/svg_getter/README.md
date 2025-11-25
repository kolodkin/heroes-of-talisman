# SVG Getter Skill

A Claude Code skill for searching and downloading SVG icons from free online sources.

## Features

- Search multiple free SVG icon libraries simultaneously
- Download SVG files directly to your project
- Support for 5 major icon libraries:
  - **Heroicons** - Clean, MIT-licensed icons by Tailwind Labs
  - **Lucide** - Open source icon library with consistent design
  - **Feather Icons** - Minimalist open source icons
  - **Bootstrap Icons** - 2,000+ free icons from Bootstrap
  - **Tabler Icons** - 5,000+ free MIT-licensed icons
- Automatic file naming with source prefix
- Usage examples in JSX/TSX

## Installation

This skill requires the `httpx` Python package, which is already included in the project dependencies.

## Usage

### With Claude Code

Simply ask Claude to find SVG icons for you:

```
"Find me a user icon"
"Search for a calendar icon from Heroicons"
"Get me an arrow-right SVG"
```

### Manual Usage

You can also run the script directly:

```bash
# Search all sources for user icons
uv run python .claude/skills/svg_getter/scripts/svg_search.py --query "user"

# Search only Heroicons for calendar icon
uv run python .claude/skills/svg_getter/scripts/svg_search.py --query "calendar" --source heroicons

# Get arrow icons and save to custom directory
uv run python .claude/skills/svg_getter/scripts/svg_search.py --query "arrow" --output public/icons --limit 10
```

### Testing

Run the built-in self-test to see the skill in action:

```bash
uv run python .claude/skills/svg_getter/scripts/svg_search_bist.py
```

This will search for various icons and save them to `./tmp/svg_search/`.

## Output

Downloaded SVG files are named with the format: `{icon-name}.svg`

Example output:

```
src/assets/icons/
  user-circle.svg
  arrow-right.svg
  check.svg
```

**Note:** If you search multiple sources and there are naming conflicts, files will be overwritten. Use the `--source` flag to search a specific library.

## Script Parameters

- `--query, -q` (required): Search term (e.g., "user", "calendar", "arrow")
- `--source, -s` (optional): Specific source (heroicons, lucide, feather, bootstrap, tabler)
- `--output, -o` (optional): Output directory (default: src/assets/icons)
- `--limit, -l` (optional): Maximum results per source (default: 5)
- `--verbose, -v` (optional): Verbose output

## Files

```
.claude/skills/svg_getter/
├── SKILL.md                    # Skill configuration for Claude Code
├── README.md                   # This file
└── scripts/
    ├── svg_search.py          # Main search and download script
    └── svg_search_bist.py     # Built-in self-test demo
```

## How It Works

1. The script uses GitHub API to list available icons in each source's repository
2. Matches icons against your search query
3. Downloads matching SVGs from jsDelivr CDN
4. Saves them to your specified output directory with source-prefixed names

## Limitations

- GitHub API has rate limits (60 requests/hour for unauthenticated requests)
- Some icons may not be available on the CDN even if listed in the repository
- Search is case-insensitive substring matching on icon filenames

## License

This skill is provided as-is. All icon libraries have their own licenses:

- Heroicons: MIT License
- Lucide: ISC License
- Feather Icons: MIT License
- Bootstrap Icons: MIT License
- Tabler Icons: MIT License

Always check the individual library licenses before using icons in commercial projects.
