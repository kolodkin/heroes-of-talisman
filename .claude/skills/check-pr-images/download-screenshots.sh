#!/bin/bash
set -e

# Script to download and organize E2E test screenshots from GitHub Actions artifacts
# Usage: ./download-screenshots.sh [run-id]
# If run-id is not provided, it will auto-detect the latest run from the current branch

# Auto-detect repository from git remote
REPO=$(git config --get remote.origin.url | sed -E 's|^.*github\.com[:/]||; s|^.*\.com/git/||; s|^.*/git/||; s|\.git$||')

if [ -z "$REPO" ]; then
    echo "❌ Error: Could not determine repository from git remote"
    echo "💡 Make sure you're in a git repository with a GitHub remote"
    exit 1
fi

echo "📦 Repository: $REPO"

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
    RUN_ID=$(gh run list --branch "$CURRENT_BRANCH" --limit 1 --json databaseId --jq '.[0].databaseId' -R "$REPO")

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

# Get the run number (different from run ID) for gh-pages URL
RUN_NUMBER=$(gh run view "$RUN_ID" -R "$REPO" --json number --jq '.number' 2>/dev/null)

if [ -z "$RUN_NUMBER" ] || [ "$RUN_NUMBER" = "null" ]; then
    echo "❌ Error: Could not get run number for workflow run $RUN_ID"
    exit 1
fi

# Extract owner from REPO (format: owner/repo)
REPO_OWNER=$(echo "$REPO" | cut -d'/' -f1)
REPO_NAME=$(echo "$REPO" | cut -d'/' -f2)
GH_PAGES_URL="https://${REPO_OWNER}.github.io/artifact-view/${REPO_NAME}/playwright-report/${RUN_NUMBER}"

echo "📥 Downloading playwright report from GitHub Pages..."
echo "   URL: $GH_PAGES_URL"

# Poll for GitHub Pages availability with 10-minute timeout
MAX_WAIT_SECONDS=600
POLL_INTERVAL=10
elapsed=0

echo "⏳ Waiting for GitHub Pages to become available (max ${MAX_WAIT_SECONDS}s)..."

while true; do
    if wget -q --spider "$GH_PAGES_URL/index.html" 2>/dev/null; then
        echo "✅ GitHub Pages is now accessible!"
        break
    fi

    if [ $elapsed -ge $MAX_WAIT_SECONDS ]; then
        echo "❌ Error: Report not accessible after ${MAX_WAIT_SECONDS}s timeout"
        echo "   URL: $GH_PAGES_URL"
        echo "💡 The GitHub Pages deployment may have failed."
        echo "💡 Check the workflow run status at:"
        echo "   https://github.com/$REPO/actions/runs/$RUN_ID"
        exit 1
    fi

    printf "\r   Waiting... %ds / %ds" "$elapsed" "$MAX_WAIT_SECONDS"
    sleep $POLL_INTERVAL
    elapsed=$((elapsed + POLL_INTERVAL))
done
echo ""

echo "  Downloading report files..."
# Download main files
wget -q -P "$TMP_DIR" "$GH_PAGES_URL/index.html" 2>/dev/null || true
wget -q -P "$TMP_DIR" "$GH_PAGES_URL/results.json" 2>/dev/null || true

DOWNLOAD_SUCCESS=false

# Download data directory (screenshots)
mkdir -p "$TMP_DIR/data"

# Method 1: Try to list data files from GitHub API (works for gh-pages)
echo "  Fetching list of screenshot files from data directory..."
DATA_FILES=$(gh api "repos/${REPO_OWNER}/artifact-view/contents/heroes-of-talisman/playwright-report/${RUN_NUMBER}/data?ref=gh-pages" 2>/dev/null | \
    grep -oE '"name":"[^"]+\.dat"' | sed 's/"name":"//;s/\.dat"//' || true)

if [ -n "$DATA_FILES" ]; then
    file_count=$(echo "$DATA_FILES" | wc -l)
    echo "  Found $file_count screenshot files, downloading..."
    downloaded=0
    for file in $DATA_FILES; do
        if wget -q -P "$TMP_DIR/data" "$GH_PAGES_URL/data/${file}.dat" 2>/dev/null; then
            downloaded=$((downloaded + 1))
        fi
    done
    echo "  Downloaded $downloaded/$file_count files"
    if [ "$downloaded" -gt 0 ]; then
        DOWNLOAD_SUCCESS=true
        echo "✅ Downloaded from GitHub Pages successfully"
    fi
else
    # Method 2: Fallback - try to parse path references from results.json
    if [ -f "$TMP_DIR/results.json" ]; then
        echo "  Parsing results.json for screenshot references..."
        DATA_FILES=$(grep -oE '"path"[[:space:]]*:[[:space:]]*"data/[^"]+\.dat"' "$TMP_DIR/results.json" 2>/dev/null | \
            sed 's/"path"[[:space:]]*:[[:space:]]*"data\///;s/\.dat"$//' | sort -u || true)

        if [ -n "$DATA_FILES" ]; then
            file_count=$(echo "$DATA_FILES" | wc -l)
            echo "  Found $file_count screenshot files, downloading..."
            downloaded=0
            for file in $DATA_FILES; do
                if wget -q -P "$TMP_DIR/data" "$GH_PAGES_URL/data/${file}.dat" 2>/dev/null; then
                    downloaded=$((downloaded + 1))
                fi
            done
            echo "  Downloaded $downloaded/$file_count files"
            if [ "$downloaded" -gt 0 ]; then
                DOWNLOAD_SUCCESS=true
                echo "✅ Downloaded from GitHub Pages successfully"
            fi
        else
            echo "⚠️  No screenshot references found in results.json"
        fi
    else
        echo "⚠️  Could not list data directory and results.json not available"
    fi
fi

if [ "$DOWNLOAD_SUCCESS" = false ]; then
    echo "❌ Failed to download screenshots from GitHub Pages."
    echo "💡 The report may not contain any screenshots."
    exit 1
fi
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
echo "🔄 Extracting and organizing screenshots..."

SCREENSHOTS_DIR="$REPORT_DIR/screenshots"
ORGANIZE_SCRIPT="$ORIGINAL_DIR/.claude/skills/check-pr-images/organize-screenshots-direct.js"

# Try to organize screenshots by test name using results.json
if [ -n "$RESULTS_JSON" ] && [ -f "$ORGANIZE_SCRIPT" ] && [ -d "$TMP_DIR/data" ]; then
    echo "📊 Organizing screenshots into test_filename/test_name/ directories..."
    if node "$ORGANIZE_SCRIPT" "$RESULTS_JSON" "$TMP_DIR/data" "$SCREENSHOTS_DIR" 2>/dev/null; then
        echo "✅ Screenshots organized by test name"
    else
        echo "⚠️  Organization failed, falling back to hash-based extraction"
        # Fallback to simple extraction
        mkdir -p "$SCREENSHOTS_DIR"
        screenshot_count=0
        for dat_file in "$TMP_DIR/data"/*.dat; do
            if [ -f "$dat_file" ]; then
                filename=$(basename "$dat_file" .dat)
                cp "$dat_file" "$SCREENSHOTS_DIR/${filename}.png"
                screenshot_count=$((screenshot_count + 1))
            fi
        done
        echo "  ✓ Extracted $screenshot_count screenshots"
    fi
else
    # Fallback: simple extraction with hash names
    echo "  Using hash-based extraction..."
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
fi

echo ""
echo "📝 Generating summary report..."

# Generate summary
SUMMARY_FILE="$REPORT_DIR/summary.txt"
PARSE_SCRIPT="$ORIGINAL_DIR/.claude/skills/check-pr-images/parse-test-results.js"

# Try to generate enhanced summary with test context
if [ -n "$RESULTS_JSON" ] && [ -f "$PARSE_SCRIPT" ]; then
    echo "📊 Extracting test context from results.json..."
    if node "$PARSE_SCRIPT" "$RESULTS_JSON" "$SCREENSHOTS_DIR" > "$SUMMARY_FILE" 2>&1; then
        echo "✅ Enhanced summary generated with test context"
    else
        echo "⚠️  Failed to parse results.json, generating basic summary"
        # Fallback to basic summary
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
    fi
else
    # Generate basic summary when results.json not available
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
fi

cat "$SUMMARY_FILE"

echo ""
echo "✅ Screenshots extracted successfully!"
echo ""
echo "📂 Location: $SCREENSHOTS_DIR"
echo "📄 Summary: $SUMMARY_FILE"

# Check for duplicate screenshots if the detection script exists
echo ""
echo "🔍 Checking for consecutive duplicate screenshots..."
DUPLICATE_CHECK_SCRIPT="$ORIGINAL_DIR/scripts/check-consecutive-duplicate-screenshots.js"

if [ -f "$DUPLICATE_CHECK_SCRIPT" ]; then
    # Ensure dependencies are installed (sharp is required)
    echo "  Installing dependencies..."
    (cd "$ORIGINAL_DIR" && npm install --silent)
    # Run duplicate detection on the downloaded report
    if node "$DUPLICATE_CHECK_SCRIPT" "$TMP_DIR"; then
        echo "✅ No consecutive duplicate screenshots found"
    else
        echo "⚠️  Consecutive duplicate screenshots detected (see output above)"
        echo "💡 This means some tests may have redundant screenshots"
    fi
else
    echo "⚠️  Duplicate detection script not found at:"
    echo "   $DUPLICATE_CHECK_SCRIPT"
    echo "💡 Skipping duplicate detection"
fi

echo ""
echo "💡 To view screenshots, use the Read tool with paths like:"
echo "   $SCREENSHOTS_DIR/<screenshot-name>.png"
echo ""
echo "💡 To run without arguments (auto-detect latest run):"
echo "   $0"
