#!/usr/bin/env python3
"""
SVG Search and Fetch Script

Searches and downloads SVG icons from free online sources.
Supports: Heroicons, Lucide, Feather Icons, Bootstrap Icons, Tabler Icons
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Literal

try:
    import httpx
except ImportError:
    print("Error: httpx package is required. Install with: uv add httpx", file=sys.stderr)
    sys.exit(1)


# Source configurations
SOURCES = {
    "heroicons": {
        "name": "Heroicons",
        "base_url": "https://cdn.jsdelivr.net/npm/heroicons@2.0.18/24/outline",
        "search_url": "https://api.github.com/repos/tailwindlabs/heroicons/contents/optimized/24/outline",
        "file_pattern": ".svg",
    },
    "lucide": {
        "name": "Lucide",
        "base_url": "https://cdn.jsdelivr.net/npm/lucide-static@latest/icons",
        "search_url": "https://api.github.com/repos/lucide-icons/lucide/contents/icons",
        "file_pattern": ".svg",
    },
    "feather": {
        "name": "Feather Icons",
        "base_url": "https://cdn.jsdelivr.net/npm/feather-icons/dist/icons",
        "search_url": "https://api.github.com/repos/feathericons/feather/contents/icons",
        "file_pattern": ".svg",
    },
    "bootstrap": {
        "name": "Bootstrap Icons",
        "base_url": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons",
        "search_url": "https://api.github.com/repos/twbs/icons/contents/icons",
        "file_pattern": ".svg",
    },
    "tabler": {
        "name": "Tabler Icons",
        "base_url": "https://cdn.jsdelivr.net/npm/@tabler/icons@latest/icons",
        "search_url": "https://api.github.com/repos/tabler/tabler-icons/contents/icons/outline",
        "file_pattern": ".svg",
    },
}

SourceType = Literal["heroicons", "lucide", "feather", "bootstrap", "tabler"]


class SVGSearcher:
    """Search and fetch SVG icons from free sources."""

    def __init__(self, timeout: int = 30):
        self.client = httpx.Client(timeout=timeout)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def search_source(self, source: str, query: str, limit: int = 5) -> list[dict]:
        """Search a specific source for matching icons."""
        if source not in SOURCES:
            raise ValueError(f"Unknown source: {source}")

        config = SOURCES[source]
        results = []

        try:
            # Fetch the directory listing from GitHub API
            response = self.client.get(config["search_url"])
            response.raise_for_status()
            files = response.json()

            # Filter and match icons
            query_lower = query.lower()
            for file in files:
                if not isinstance(file, dict):
                    continue

                name = file.get("name", "")
                if not name.endswith(config["file_pattern"]):
                    continue

                # Check if query matches the filename
                icon_name = name.replace(config["file_pattern"], "")
                if query_lower in icon_name.lower():
                    results.append(
                        {
                            "name": icon_name,
                            "source": source,
                            "source_name": config["name"],
                            "filename": name,
                            "url": f"{config['base_url']}/{name}",
                        }
                    )

                if len(results) >= limit:
                    break

        except httpx.HTTPError as e:
            print(f"Warning: Failed to search {config['name']}: {e}", file=sys.stderr)

        return results

    def fetch_svg(self, url: str) -> str:
        """Fetch SVG content from a URL."""
        response = self.client.get(url)
        response.raise_for_status()
        return response.text

    def save_svg(self, content: str, output_path: Path) -> None:
        """Save SVG content to a file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Search and download SVG icons from free sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --query user
  %(prog)s --query calendar --source heroicons
  %(prog)s --query arrow --output public/icons --limit 10
        """,
    )

    parser.add_argument(
        "--query", "-q", required=True, help="Search term (e.g., 'user', 'calendar', 'arrow')"
    )

    parser.add_argument(
        "--source",
        "-s",
        choices=list(SOURCES.keys()),
        help="Specific source to search (default: all sources)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("src/assets/icons"),
        help="Output directory for SVG files (default: src/assets/icons)",
    )

    parser.add_argument(
        "--limit", "-l", type=int, default=5, help="Maximum results per source (default: 5)"
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Determine which sources to search
    sources_to_search = [args.source] if args.source else list(SOURCES.keys())

    print(f"Searching for '{args.query}' in {len(sources_to_search)} source(s)...\n")

    all_results = []

    with SVGSearcher() as searcher:
        # Search each source
        for source in sources_to_search:
            if args.verbose:
                print(f"Searching {SOURCES[source]['name']}...")

            results = searcher.search_source(source, args.query, args.limit)
            all_results.extend(results)

            if results:
                print(f"Found {len(results)} icon(s) in {SOURCES[source]['name']}")

        if not all_results:
            print(f"\nNo icons found matching '{args.query}'")
            return 1

        print(f"\nTotal: {len(all_results)} icon(s) found\n")
        print("Downloading SVGs...\n")

        # Download and save SVGs
        downloaded = []
        for result in all_results:
            try:
                svg_content = searcher.fetch_svg(result["url"])
                output_file = args.output / f"{result['name']}.svg"
                searcher.save_svg(svg_content, output_file)

                downloaded.append(
                    {
                        "name": result["name"],
                        "source": result["source_name"],
                        "file": str(output_file),
                    }
                )

                if args.verbose:
                    print(f"✓ {result['source_name']}: {result['name']} → {output_file}")

            except Exception as e:
                print(f"✗ Failed to download {result['name']}: {e}", file=sys.stderr)

        # Print summary
        print(f"\nSuccessfully downloaded {len(downloaded)} SVG file(s) to {args.output}/\n")

        if downloaded:
            print("Downloaded files:")
            for item in downloaded:
                print(f"  • {item['name']} ({item['source']}) → {item['file']}")

            print("\nUsage in JSX/TSX:")
            example = downloaded[0]
            icon_name = example["name"].replace("-", " ").title().replace(" ", "")
            print(f'  import {icon_name}Icon from "./{args.output}/{Path(example["file"]).name}"')
            print(f"  <img src={{{icon_name}Icon}} alt=\"{example['name']} icon\" />")

    return 0


if __name__ == "__main__":
    sys.exit(main())
