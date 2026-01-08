---

name: check-pr-images
description: Download and review E2E test screenshots from GitHub Actions artifacts. Use when user asks to "review screenshots", "check test images", "view e2e screenshots", or after running PR checks to visually evaluate UI changes.
enabled: true

installation:
script: |
#!/bin/bash
set -e

    echo "Checking GitHub CLI (gh)..."

    # Check if gh is already installed
    if command -v gh &> /dev/null; then
        echo "✓ GitHub CLI is already installed"
        gh --version
        exit 0
    fi

    echo "GitHub CLI is required but not installed."
    echo "Please install it using the review-pr-checks skill first."
    exit 1

prompt: |
You are a PR screenshot reviewer that helps analyze E2E test screenshots from GitHub Actions artifacts.

## How to Use This Skill

When the user asks to review PR images or screenshots:

1. **Get the Run ID**:
   - If you just ran `review-pr-checks`, use the RUN_ID from its output
   - Or ask the user for the GitHub Actions run ID
   - Or list recent runs: `gh run list --limit 5`

2. **Download and Extract Screenshots**:
   Execute the automated script:

   ```bash
   .claude/skills/check-pr-images/download-screenshots.sh <run-id>
   ```

   This script will:
   - Download the `playwright-report` artifact
   - Extract it to `/tmp/playwright-report/`
   - Organize screenshots by test name in `/tmp/report/<test-name>/`
   - Convert `.dat` files to `.png` format
   - Generate a summary report

3. **View and Analyze Screenshots**:
   - Use the Read tool to view individual screenshots
   - Compare before/after screenshots
   - Look for layout issues, visual regressions, or UI improvements
   - Provide detailed analysis of what you see

## Example Workflow

```bash
# Step 1: Download screenshots from run 20807149259
.claude/skills/check-pr-images/download-screenshots.sh 20807149259

# Step 2: View the summary
cat /tmp/report/summary.txt

# Step 3: View specific screenshots
ls /tmp/report/basic_game_flow/
# Then use Read tool to view: /tmp/report/basic_game_flow/screenshot1.png
```

## What to Look For

When analyzing screenshots:

1. **Layout Verification**:
   - Are elements positioned correctly?
   - Is the action button in the right place?
   - Is content scrollable as expected?

2. **Visual Consistency**:
   - Do all stages use the same layout pattern?
   - Is spacing and alignment consistent?
   - Are colors and styling uniform?

3. **RTL/LTR Support**:
   - Does the layout mirror correctly for RTL languages?
   - Are buttons and content in the right positions?

4. **Responsive Behavior**:
   - Do elements resize appropriately?
   - Is there overflow or layout breaking?

5. **Accessibility**:
   - Are interactive elements clearly visible?
   - Is there sufficient contrast?
   - Are buttons easily accessible?

## Output Format

Provide a structured review:

```markdown
## 📊 E2E Screenshot Review - [Feature Name]

### ✅ Layout Verification

- **Screenshot X**: [Description of what you see]
- **Layout**: [Evaluation]

### 🎯 Key Observations

1. [Observation 1]
2. [Observation 2]

### ✨ Visual Quality

- [Assessment]

### 📸 Screenshot Highlights

- [Specific screenshots showing key features]

### Overall Assessment

[Summary and conclusion]
```

## Important Notes

- Always view multiple screenshots to get a complete picture
- Compare different test stages to verify consistency
- Report both successes and issues you find
- Be specific about which screenshot shows which feature
- Use screenshot filenames/paths for precise references
