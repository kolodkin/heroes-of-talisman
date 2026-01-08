#!/bin/bash
set -e

# Script to download and organize E2E test screenshots from GitHub Actions artifacts
# Usage: ./download-screenshots.sh <run-id>

if [ -z "$1" ]; then
    echo "Error: Run ID is required"
    echo "Usage: $0 <run-id>"
    echo ""
    echo "To find run IDs, use: gh run list --limit 5"
    exit 1
fi

RUN_ID="$1"
TMP_DIR="/tmp/playwright-report"
REPORT_DIR="/tmp/report"

echo "🔍 Downloading screenshots from GitHub Actions run: $RUN_ID"
echo ""

# Clean up previous downloads
echo "🧹 Cleaning up previous downloads..."
rm -rf "$TMP_DIR"
rm -rf "$REPORT_DIR"
mkdir -p "$TMP_DIR"
mkdir -p "$REPORT_DIR"

# Download the playwright-report artifact
echo "📥 Downloading playwright-report artifact..."
cd "$TMP_DIR"
if ! gh run download "$RUN_ID" -n playwright-report; then
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
echo "🔄 Organizing screenshots by test name..."

# Function to sanitize test names for directory names
sanitize_name() {
    echo "$1" | sed 's/[^a-zA-Z0-9_-]/_/g' | sed 's/__*/_/g'
}

# If we have results.json, use it to organize screenshots
if [ -n "$RESULTS_JSON" ]; then
    # Extract test names and their screenshot paths using jq
    # The structure is: suites[].specs[].tests[].results[].attachments[]

    # Get all test titles and their screenshots
    jq -r '.suites[].specs[] | .title as $spec_title | .tests[] | .results[] | .attachments[] | select(.name == "screenshot") | "\($spec_title)|\(.path)"' "$RESULTS_JSON" | while IFS='|' read -r test_name screenshot_path; do
        if [ -n "$test_name" ] && [ -n "$screenshot_path" ]; then
            # Sanitize test name for directory
            safe_name=$(sanitize_name "$test_name")
            test_dir="$REPORT_DIR/$safe_name"
            mkdir -p "$test_dir"

            # Get the full path to the screenshot
            full_path="$(dirname "$RESULTS_JSON")/$screenshot_path"

            if [ -f "$full_path" ]; then
                # Extract the base name and convert .dat to .png
                base_name=$(basename "$screenshot_path" .dat)

                # Copy and rename to .png (these are actually PNG files)
                cp "$full_path" "$test_dir/${base_name}.png"
                echo "  ✓ $safe_name/${base_name}.png"
            fi
        fi
    done
else
    # Fallback: organize by directory structure
    find "$TMP_DIR" -name "*.dat" -type f | while read -r screenshot; do
        # Get the test name from the directory structure
        rel_path=$(realpath --relative-to="$TMP_DIR" "$screenshot")
        test_name=$(dirname "$rel_path" | sed 's/\//-/g')

        if [ -z "$test_name" ] || [ "$test_name" = "." ]; then
            test_name="uncategorized"
        fi

        safe_name=$(sanitize_name "$test_name")
        test_dir="$REPORT_DIR/$safe_name"
        mkdir -p "$test_dir"

        # Get base name and convert to .png
        base_name=$(basename "$screenshot" .dat)
        cp "$screenshot" "$test_dir/${base_name}.png"
        echo "  ✓ $safe_name/${base_name}.png"
    done
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
    echo "Test Results:"
    echo ""

    for test_dir in "$REPORT_DIR"/*/; do
        if [ -d "$test_dir" ]; then
            test_name=$(basename "$test_dir")
            screenshot_count=$(find "$test_dir" -name "*.png" -type f | wc -l)

            echo "📁 $test_name ($screenshot_count screenshots)"
            find "$test_dir" -name "*.png" -type f -exec basename {} \; | sort | sed 's/^/   - /'
            echo ""
        fi
    done

    echo "============================"
    total_screenshots=$(find "$REPORT_DIR" -name "*.png" -type f | wc -l)
    total_tests=$(find "$REPORT_DIR" -mindepth 1 -maxdepth 1 -type d | wc -l)
    echo "Total: $total_screenshots screenshots across $total_tests tests"
} > "$SUMMARY_FILE"

cat "$SUMMARY_FILE"

echo ""
echo "✅ Screenshots organized successfully!"
echo ""
echo "📂 Location: $REPORT_DIR"
echo "📄 Summary: $SUMMARY_FILE"
echo ""
echo "💡 To view screenshots, use the Read tool with paths like:"
echo "   /tmp/report/<test-name>/<screenshot-name>.png"
