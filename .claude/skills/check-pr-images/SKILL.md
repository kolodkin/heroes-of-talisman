---
name: check-pr-images
description: Download and review E2E test screenshots from GitHub Pages with duplicate detection and test context. Use when user asks to "review screenshots", "check test images", "view e2e screenshots", or after running PR checks to visually evaluate UI changes. Includes screenshot generation guidelines for QA developers.
---

You are a PR screenshot reviewer that helps analyze E2E test screenshots from GitHub Pages.

## Installation

```bash
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
echo "Please install it using the pr-checks skill first."
exit 1
```

## How to Use This Skill

When the user asks to review PR images or screenshots:

1. **Download and Extract Screenshots**:
   Execute the automated script (it will auto-detect the latest run from the current branch):

   ```bash
   .claude/skills/check-pr-images/download-screenshots.sh
   ```

   Or specify a run ID manually:

   ```bash
   .claude/skills/check-pr-images/download-screenshots.sh <run-id>
   ```

   This script will:
   - Auto-detect the repository from git remote (no hardcoded repo names)
   - Auto-detect the latest workflow run for the current branch (if no run ID provided)
   - Download the playwright report from GitHub Pages
   - Save files to `./tmp/playwright-report/`
   - Extract all screenshots to `./tmp/report/screenshots/`
   - Convert `.dat` files to `.png` format
   - Parse test context from `results.json` for enhanced reporting
   - Generate a detailed summary report with test information
   - Run duplicate detection to identify redundant screenshots

2. **View and Analyze Screenshots**:
   - Use the Read tool to view individual screenshots
   - Compare different screenshots
   - Look for layout issues, visual regressions, or UI improvements
   - Provide detailed analysis of what you see

## Example Workflow

```bash
# Step 1: Download screenshots (auto-detect latest run)
.claude/skills/check-pr-images/download-screenshots.sh

# Step 2: View the summary (includes test context and duplicate detection results)
cat ./tmp/report/summary.txt

# Step 3: View specific screenshots
ls ./tmp/report/screenshots/
# Then use Read tool to view: ./tmp/report/screenshots/<hash>.png
```

## Enhanced Features

### Repository Auto-Detection

The skill automatically detects your repository from `git remote`, so it works with any GitHub repository without hardcoded values.

### Test Context Extraction

When `results.json` is available, the summary report includes:

- Test titles and file paths
- Test status (passed/failed)
- Test duration
- Screenshots grouped by test
- Mapping between screenshot names and files

### Duplicate Detection

Automatically runs consecutive duplicate screenshot detection using perceptual hashing:

- Identifies back-to-back identical screenshots within the same test
- Uses visual comparison (tolerates minor pixel differences)
- Reports which screenshots are redundant and should be removed
- Helps maintain clean, efficient test suites

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

---

## Guidelines for QA Developers: Generating Screenshots in Tests

You are a front-end QA developer responsible for screenshots taken in tests. Make sure image content and name correlate with the screenshot's location and purpose in the test.

### Core Guidelines

**1. Place screenshot capture AFTER relevant wait for UI change**

- Don't capture mid-transition or during animations
- Wait for the UI state to stabilize before capturing
- Example: After clicking a button, wait for the page to fully render

**2. Unless specifically tested, wait for loading UI indication to end**

- Avoid capturing spinners, skeleton screens, or "Loading..." text unless that's what you're testing
- Wait for content to fully load
- Ensure all async data has been fetched and rendered

**3. For toasts, wait for the toast to appear**

- Toasts often have animation delays
- Wait for the toast to be fully visible and stable
- Consider the toast's display duration when timing screenshots

### Playwright Examples

```typescript
// ✅ Good: Wait for UI to stabilize
await page.click("#submit-button");
await page.waitForSelector(".success-message", { state: "visible" });
await page.screenshot({ path: "form-submitted-success.png" });

// ✅ Good: Wait for loading to complete
await page.goto("/dashboard");
await page.waitForSelector(".loading-spinner", { state: "hidden" });
await page.waitForSelector(".dashboard-content", { state: "visible" });
await page.screenshot({ path: "dashboard-loaded.png" });

// ✅ Good: Wait for toast animation
await page.click("#delete-item");
await page.waitForSelector(".toast", { state: "visible" });
await page.waitForTimeout(300); // Wait for animation
await page.screenshot({ path: "delete-success-toast.png" });
```

### Screenshot Naming Best Practices

- **Names must accurately describe ALL items tested before the screenshot**
- Use kebab-case for consistency
- Use descriptive names by default; only use shorthand if name exceeds 100 characters
- Examples:
  - `login-success-with-welcome-message.png` - captures login + welcome message
  - `card-hover-and-sizes.png` - captures both hover effect and size validation
  - `battle-participants-visible.png` - captures multiple participant elements
  - `form-validation-errors.png` - captures multiple validation states
  - `card-view.png` - shorthand acceptable if full name would exceed 100 chars

### Common Pitfalls to Avoid

1. **Racing Conditions**: Don't rely on fixed timeouts; use proper wait conditions
2. **Inconsistent States**: Ensure screenshots always capture the same UI state
3. **Animation Interference**: Account for CSS animations and transitions
4. **Generic Names**: Avoid names like `screenshot-1.png` or `test.png`
5. **Loading Artifacts**: Don't capture temporary loading states unless intentional
