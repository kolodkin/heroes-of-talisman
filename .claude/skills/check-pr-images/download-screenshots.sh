#!/bin/bash
set -e

# Script to download and organize E2E test screenshots from GitHub Actions artifacts
# Usage: ./download-screenshots.sh [run-id]
# If run-id is not provided, it will auto-detect the latest run from the current branch

# Auto-detect run ID if not provided
if [ -z "$1" ]; then
    echo "🔍 Auto-detecting latest GitHub Actions run for current branch..."
    CURRENT_BRANCH=$(git branch --show-current)

    if [ -z "$CURRENT_BRANCH" ]; then
        echo "❌ Error: Could not determine current branch"
        exit 1
    fi

    echo "📝 Current branch: $CURRENT_BRANCH"

    # Get the latest workflow run for this branch
    RUN_ID=$(gh run list --branch "$CURRENT_BRANCH" --limit 1 --json databaseId --jq '.[0].databaseId' -R kolodkin/heroes-of-talisman)

    if [ -z "$RUN_ID" ] || [ "$RUN_ID" = "null" ]; then
        echo "❌ Error: No workflow runs found for branch $CURRENT_BRANCH"
        echo "💡 You can specify a run ID manually: $0 <run-id>"
        exit 1
    fi

    echo "✅ Auto-detected run ID: $RUN_ID"
else
    RUN_ID="$1"
fi

TMP_DIR="./tmp/playwright-report"
REPORT_DIR="./tmp/report"
ORIGINAL_DIR=$(pwd)

echo "🔍 Downloading screenshots from GitHub Actions run: $RUN_ID"
echo ""

# Clean up previous downloads
echo "🧹 Cleaning up previous downloads..."
rm -rf "$TMP_DIR"
rm -rf "$REPORT_DIR"
mkdir -p "$TMP_DIR"
mkdir -p "$REPORT_DIR"

# Download the playwright-report artifact (from original directory to preserve git context)
echo "📥 Downloading playwright-report artifact..."
if ! (cd "$TMP_DIR" && gh run download "$RUN_ID" -n playwright-report -R kolodkin/heroes-of-talisman); then
    echo "❌ Failed to download artifact. Check that the run ID is correct and the artifact exists."
    exit 1
fi

echo "✅ Artifact downloaded successfully"
echo ""

# Find the results.json file
RESULTS_JSON=$(find "$TMP_DIR" -name "results.json" -type f | head -n 1)

if [ -z "$RESULTS_JSON" ]; then
    echo "⚠️  Warning: results.json not found. Will organize screenshots by directory structure."
    RESULTS_JSON=""
else
    echo "📊 Found results.json: $RESULTS_JSON"
fi

echo ""
echo "🔄 Extracting screenshots..."

# The .dat files in the data/ directory are actually PNG files
# Just copy them and rename them to .png
SCREENSHOTS_DIR="$REPORT_DIR/screenshots"
mkdir -p "$SCREENSHOTS_DIR"

screenshot_count=0
if [ -d "$TMP_DIR/data" ]; then
    for dat_file in "$TMP_DIR/data"/*.dat; do
        if [ -f "$dat_file" ]; then
            filename=$(basename "$dat_file" .dat)
            cp "$dat_file" "$SCREENSHOTS_DIR/${filename}.png"
            screenshot_count=$((screenshot_count + 1))
        fi
    done
    echo "  ✓ Extracted $screenshot_count screenshots"
else
    echo "  ⚠️  Warning: No data directory found"
fi

echo ""
echo "📝 Generating summary report..."

# Generate summary
SUMMARY_FILE="$REPORT_DIR/summary.txt"
{
    echo "E2E Test Screenshots Summary"
    echo "============================"
    echo "Run ID: $RUN_ID"
    echo "Downloaded: $(date)"
    echo ""
    echo "Screenshots location: $SCREENSHOTS_DIR"
    echo ""
    echo "Available screenshots:"
    echo ""

    if [ -d "$SCREENSHOTS_DIR" ]; then
        find "$SCREENSHOTS_DIR" -name "*.png" -type f -exec basename {} \; | sort | sed 's/^/   - /'
    fi

    echo ""
    echo "============================"
    total_screenshots=$(find "$SCREENSHOTS_DIR" -name "*.png" -type f 2>/dev/null | wc -l)
    echo "Total: $total_screenshots screenshots"
} > "$SUMMARY_FILE"

cat "$SUMMARY_FILE"

echo ""
echo "✅ Screenshots extracted successfully!"
echo ""
echo "📂 Location: $SCREENSHOTS_DIR"
echo "📄 Summary: $SUMMARY_FILE"
echo ""
echo "💡 To view screenshots, use the Read tool with paths like:"
echo "   $SCREENSHOTS_DIR/<screenshot-name>.png"
echo ""
echo "💡 To run without arguments (auto-detect latest run):"
echo "   $0"
