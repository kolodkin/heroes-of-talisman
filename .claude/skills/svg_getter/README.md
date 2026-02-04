# SVG Getter Skill

A Claude Code skill for searching and downloading SVG icons from free online sources.

## Features

- Search multiple free SVG icon libraries simultaneously
- Download SVG files directly to your project
- Support for 6 major icon libraries:

  **UI Icon Libraries (MIT/ISC License):**
  - **Heroicons** - Clean, MIT-licensed icons by Tailwind Labs
  - **Lucide** - Open source icon library with consistent design (ISC)
  - **Feather Icons** - Minimalist open source icons (MIT)
  - **Bootstrap Icons** - 2,000+ free icons from Bootstrap (MIT)
  - **Tabler Icons** - 5,000+ free MIT-licensed icons (MIT)

  **Game Icon Libraries (CC BY 3.0 License):**
  - **Game Icons** - 4,000+ RPG/game icons from [game-icons.net](https://game-icons.net)
    - Includes: weapons, armor, creatures, items, skills, magic, etc.
    - Attribution required when using these icons

- License verification tool to ensure all sources use permissive licenses
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

# Search Game Icons for sword/weapon icons (great for games!)
uv run python .claude/skills/svg_getter/scripts/svg_search.py --query "sword" --source gameicons

# Search Game Icons for armor/shield icons
uv run python .claude/skills/svg_getter/scripts/svg_search.py --query "armor" --source gameicons
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

- `--query, -q` (required): Search term (e.g., "user", "calendar", "sword", "armor")
- `--source, -s` (optional): Specific source (heroicons, lucide, feather, bootstrap, tabler, gameicons)
- `--output, -o` (optional): Output directory (default: src/assets/icons)
- `--limit, -l` (optional): Maximum results per source (default: 5)
- `--verbose, -v` (optional): Verbose output

## License Verification

All icon sources have been verified to use permissive licenses suitable for commercial use. You can verify licenses anytime by running:

```bash
uv run python .claude/skills/svg_getter/scripts/sources_license_checker.py
```

This will check all sources and confirm they use MIT or ISC licenses.

## Files

```
.claude/skills/svg_getter/
├── SKILL.md                        # Skill configuration for Claude Code
├── README.md                       # This file
└── scripts/
    ├── svg_search.py              # Main search and download script
    ├── svg_search_bist.py         # Built-in self-test demo
    └── sources_license_checker.py # License verification tool
```

## How It Works

1. The script uses GitHub API to list available icons in each source's repository
2. Matches icons against your search query
3. Downloads matching SVGs from jsDelivr CDN
4. Saves them to your specified output directory

## Limitations

- GitHub API has rate limits (60 requests/hour for unauthenticated requests)
- Some icons may not be available on the CDN even if listed in the repository
- Search is case-insensitive substring matching on icon filenames

## License

This skill is provided as-is. All icon libraries use permissive licenses verified by our license checker:

**MIT/ISC Licensed (no attribution required):**

- **Heroicons**: MIT License
- **Lucide**: ISC License
- **Feather Icons**: MIT License
- **Bootstrap Icons**: MIT License
- **Tabler Icons**: MIT License

**CC BY 3.0 Licensed (attribution required):**

- **Game Icons**: CC BY 3.0 License
  - Website: https://game-icons.net
  - Attribution: Credit the icon author (shown in download output)
  - Example: "Icon by Lorc, https://game-icons.net"

All these licenses allow free commercial use. Run the license checker to view full license details and GitHub links.
