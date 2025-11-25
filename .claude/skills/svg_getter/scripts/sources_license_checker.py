#!/usr/bin/env python3
"""
Sources License Checker

Validates the license of each SVG icon source by fetching and analyzing
LICENSE files from their GitHub repositories.
"""

import re
import sys
from typing import Optional

try:
    import httpx
except ImportError:
    print("Error: httpx package is required. Install with: uv add httpx", file=sys.stderr)
    sys.exit(1)


# Source configurations with GitHub repository info
SOURCES = {
    "heroicons": {
        "name": "Heroicons",
        "github_repo": "tailwindlabs/heroicons",
        "website": "https://heroicons.com",
    },
    "lucide": {
        "name": "Lucide",
        "github_repo": "lucide-icons/lucide",
        "website": "https://lucide.dev",
    },
    "feather": {
        "name": "Feather Icons",
        "github_repo": "feathericons/feather",
        "website": "https://feathericons.com",
    },
    "bootstrap": {
        "name": "Bootstrap Icons",
        "github_repo": "twbs/icons",
        "website": "https://icons.getbootstrap.com",
    },
    "tabler": {
        "name": "Tabler Icons",
        "github_repo": "tabler/tabler-icons",
        "website": "https://tabler.io/icons",
    },
}


class LicenseChecker:
    """Check licenses for SVG icon sources."""

    def __init__(self, timeout: int = 30):
        self.client = httpx.Client(timeout=timeout)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def fetch_github_license(self, repo: str) -> Optional[dict]:
        """Fetch license information from GitHub repository."""
        # Try GitHub's license API endpoint first
        license_api_url = f"https://api.github.com/repos/{repo}/license"
        html_url = None

        try:
            response = self.client.get(license_api_url)
            if response.status_code == 200:
                data = response.json()
                spdx_id = data.get("license", {}).get("spdx_id", "Unknown")
                html_url = data.get("html_url", "")

                # If GitHub successfully identified the license, use it
                # But fall through to content analysis if NOASSERTION or Unknown
                if spdx_id not in ["NOASSERTION", "Unknown", "NONE", None]:
                    return {
                        "type": spdx_id,
                        "name": data.get("license", {}).get("name", spdx_id),
                        "url": html_url,
                    }
        except httpx.HTTPError as e:
            print(f"Warning: Failed to fetch license via API for {repo}: {e}", file=sys.stderr)

        # Fallback: Try to fetch LICENSE file directly and analyze content
        license_file_urls = [
            f"https://api.github.com/repos/{repo}/contents/LICENSE",
            f"https://api.github.com/repos/{repo}/contents/LICENSE.md",
            f"https://api.github.com/repos/{repo}/contents/LICENSE.txt",
            f"https://api.github.com/repos/{repo}/contents/LICENCE",
        ]

        for url in license_file_urls:
            try:
                response = self.client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    # Decode content from base64
                    import base64

                    content = base64.b64decode(data.get("content", "")).decode("utf-8")
                    license_type = self.identify_license(content)
                    return {
                        "type": license_type,
                        "name": license_type,
                        "url": html_url or data.get("html_url", ""),
                        "content_preview": content[:200] + "...",
                    }
            except Exception:
                continue

        return None

    def identify_license(self, content: str) -> str:
        """Identify license type from content."""
        content_lower = content.lower()

        # Common license patterns
        # Check ISC first (has unique permission text)
        if "isc license" in content_lower or (
            "permission to use, copy, modify, and" in content_lower
            and "distribute this software" in content_lower
        ):
            return "ISC"
        elif "mit license" in content_lower or "permission is hereby granted, free of charge" in content_lower:
            return "MIT"
        elif "apache license" in content_lower and "version 2.0" in content_lower:
            return "Apache-2.0"
        elif "bsd" in content_lower:
            if "3-clause" in content_lower:
                return "BSD-3-Clause"
            elif "2-clause" in content_lower:
                return "BSD-2-Clause"
            return "BSD"
        elif "gnu general public license" in content_lower:
            if "version 3" in content_lower:
                return "GPL-3.0"
            elif "version 2" in content_lower:
                return "GPL-2.0"
            return "GPL"
        elif "mozilla public license" in content_lower:
            return "MPL-2.0"
        elif "unlicense" in content_lower:
            return "Unlicense"
        elif "creative commons" in content_lower or "cc0" in content_lower:
            return "CC0-1.0"
        else:
            return "Unknown"

    def is_permissive_license(self, license_type: str) -> bool:
        """Check if license is permissive (allows commercial use)."""
        permissive_licenses = {
            "MIT",
            "ISC",
            "BSD",
            "BSD-2-Clause",
            "BSD-3-Clause",
            "Apache-2.0",
            "Unlicense",
            "CC0-1.0",
        }
        return license_type in permissive_licenses


def main():
    """Check licenses for all configured sources."""
    print("SVG Sources License Checker")
    print("=" * 80)
    print("Checking licenses for all icon sources...\n")

    results = []

    with LicenseChecker() as checker:
        for source_key, source_info in SOURCES.items():
            print(f"Checking {source_info['name']}...")

            license_info = checker.fetch_github_license(source_info["github_repo"])

            if license_info:
                is_permissive = checker.is_permissive_license(license_info["type"])
                status = "✓ PERMISSIVE" if is_permissive else "⚠ RESTRICTIVE"

                results.append(
                    {
                        "source": source_info["name"],
                        "license_type": license_info["type"],
                        "license_name": license_info.get("name", license_info["type"]),
                        "url": license_info.get("url", ""),
                        "website": source_info["website"],
                        "github": f"https://github.com/{source_info['github_repo']}",
                        "status": status,
                        "is_permissive": is_permissive,
                    }
                )

                print(f"  {status}: {license_info['type']}\n")
            else:
                results.append(
                    {
                        "source": source_info["name"],
                        "license_type": "UNKNOWN",
                        "license_name": "Could not determine",
                        "url": "",
                        "website": source_info["website"],
                        "github": f"https://github.com/{source_info['github_repo']}",
                        "status": "✗ FAILED TO CHECK",
                        "is_permissive": False,
                    }
                )
                print(f"  ✗ FAILED TO CHECK: Could not fetch license\n")

    # Print summary
    print("\n" + "=" * 80)
    print("LICENSE SUMMARY")
    print("=" * 80)
    print()

    for result in results:
        print(f"{result['source']}")
        print(f"  License:  {result['license_type']}")
        print(f"  Status:   {result['status']}")
        print(f"  Website:  {result['website']}")
        print(f"  GitHub:   {result['github']}")
        if result["url"]:
            print(f"  License:  {result['url']}")
        print()

    # Check if all are permissive
    all_permissive = all(r["is_permissive"] for r in results)

    if all_permissive:
        print("=" * 80)
        print("✓ All sources use permissive licenses suitable for commercial use")
        print("=" * 80)
        return 0
    else:
        print("=" * 80)
        print("⚠ WARNING: Some sources may have restrictive licenses")
        print("Please review the licenses before using in commercial projects")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
