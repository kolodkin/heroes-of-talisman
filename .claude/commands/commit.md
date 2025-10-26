---
description: Create a git commit with staged changes, handling pre-commit hooks automatically
---

# Git Commit Command

You are helping the user create a git commit with their staged changes.

## Pre-commit Hook Context

This project uses pre-commit hooks that may modify files during commit (formatting, linting, etc.).

## Instructions

1. **Check staged changes**: Run `git status` and `git diff --staged --stat` to understand what's being committed

2. **Analyze changes**: If the user didn't provide a commit message, analyze the staged changes and suggest an appropriate commit message following conventional commit format:
   - `feature:` for new features
   - `bugfix:` for bug fixes
   - `refactor:` for code refactoring
   - `cleanup:` for code cleanup

   Note: Multiple types can be combined, e.g., `[feature, cleanup]: description`

3. **Present commit message for approval**: Show the proposed commit message to the user and ask for their approval before proceeding. Let them edit it if needed.

4. **Create the commit**: Once approved, use the Bash tool with a HEREDOC to create the commit:

   ```bash
   git commit -m "$(cat <<'EOF'
   <type>: <short description>

   <optional longer description>
   EOF
   )"
   ```

5. **Handle pre-commit hook modifications**: If the commit FAILED because files were modified by hooks:
   - The hooks run BEFORE the commit is created, so no commit exists yet
   - Simply stage the hook changes and retry the commit:
     ```bash
     git add -u && git commit -m "$(cat <<'EOF'
     <same commit message>
     EOF
     )"
     ```
   - Do NOT use `--amend` in this scenario since no commit was created yet

6. **Show result**: Display the final commit with `git log -1 --pretty=format:"%h %s%n%b"`

## Important Notes

- NEVER amend commits that were authored by someone else or already pushed
- If amend is unsafe, create a NEW commit with the hook changes
- Always use HEREDOC format for multi-line commit messages
- Keep commit messages concise but descriptive
- ALWAYS get user approval before creating the commit
- If command runs again: restart from step 1
