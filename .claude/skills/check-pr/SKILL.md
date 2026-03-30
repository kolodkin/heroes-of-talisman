---
name: check-pr
description: Check PR status and verify GitHub Actions CI workflows. Use after git push or when user asks to check PR/CI status.
---

# PR Check Skill

You are a PROACTIVE GitHub Actions assistant. After EVERY git push, you MUST automatically verify all GitHub Actions workflows are successful. If any fail, read error logs and resolve issues.

## Run the Check Script

The script accepts optional args that can be passed via the skill invocation
(e.g. `/check-pr links`, `/check-pr comments`, `/check-pr links comments`).

Map skill args to script flags:

| Skill arg  | Script flag       | Effect                                                         |
| ---------- | ----------------- | -------------------------------------------------------------- |
| `links`    | `--links`         | Print direct `#?testId=` links per test (waits for Pages ~30s) |
| `comments` | `--comments-only` | Skip CI polling, only check PR review comments                 |

```bash
# Default — poll CI, report result
.claude/skills/check-pr/run-workflow-check.sh

# With per-test deep links
.claude/skills/check-pr/run-workflow-check.sh --links

# Comments only
.claude/skills/check-pr/run-workflow-check.sh --comments-only

# Comments + links (can combine)
.claude/skills/check-pr/run-workflow-check.sh --comments-only --links
```

**When user passes args**, translate them:

- `links` → append `--links`
- `comments` → append `--comments-only`

This script will automatically:

1. Install gh CLI if not available
2. Check authentication
3. Get current branch
4. Poll workflow status every 10 seconds until complete
5. Report SUCCESS or FAILURE with full logs

## Deciding When to Use `--links`

Pass `--links` automatically (without the user asking) when CI completes with **test failures** in the E2E workflow. Do NOT pass `--links` on pure success runs unless the user explicitly requests it.

## Filtering Which Links to Show

When `--links` output is available, **do not show all test links**. Show only the relevant subset:

1. **Failing tests** — always show links for any test with status `unexpected` or `failed`
2. **Tests related to changed files** — determine which spec files correspond to files modified in this PR/push (e.g., changes in `server/gameplay/knight.py` → show links from `e2e/basic.spec.js` tests that cover the knight), then show links for those tests regardless of pass/fail

Omit all other passing tests that are unrelated to the current change set. This keeps the output focused and actionable.

## Output Format for Test Links

Always present test links in a plain-text format suitable for copying to messaging apps (e.g. WhatsApp). Use this exact format:

```
✅ PR #<number> — All checks passed

🧪 <Feature name> E2E Tests:

1. <test title>
<full URL with #?testId=...>

2. <test title>
<full URL with #?testId=...>
```

- Use `✅` for success, `❌` for failure
- Number each test
- Put the full URL on its own line (no markdown link syntax)
- Group tests by spec file with a header if multiple spec files are shown

## On Failure

1. **Get logs from failed runs:**

   ```bash
   gh run view RUN_ID --repo OWNER/REPO --log-failed
   ```

2. **Analyze, fix, commit, push, and re-run the script until workflow passes.**

## Address PR Review Comments

The script displays unresolved comments with their IDs. Address ONLY unresolved comments.

**Option A: Fix the issue**

1. Fix and commit
2. Push changes
3. Reply within the comment thread: `[Agent] Fixed - <what was fixed>`

**Option B: Ask for clarification**

- Reply within the comment thread: `[Agent] Question: <your question>`

**Reply within comment thread (REQUIRED):**

Use the `/replies` endpoint to respond within the same comment thread (not as a separate comment):

```bash
gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments/COMMENT_ID/replies \
  -f body="[Agent] Fixed - <description of what was fixed>"
```

Example:

```bash
# Reply to comment ID COMMENT_ID on PR #PR_NUMBER
gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments/COMMENT_ID/replies \
  -f body="[Agent] Fixed - <description of what was fixed>"
```

**IMPORTANT:**

- Always prefix responses with `[Agent]` to identify agent-generated replies
- Use the `/replies` endpoint to keep responses in the comment thread
- Only respond to unresolved comments
- Be concise in responses

Be PROACTIVE: Check and poll workflows after every push!
