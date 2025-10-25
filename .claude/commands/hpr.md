---
description: Create a Heroes PR
---

# Heroes PR Command

You are helping the user create a pull request using the Heroes PR flow, which generates a comprehensive PR description.

## Instructions

1. **Check if pull from main is needed**:
   - Run `git fetch origin main` to update remote tracking
   - Run `git rev-list HEAD..origin/main --count` to check if main has new commits
   - If there are new commits on main:
     - Ask user: "Main branch has X new commits. Pull from main before creating PR?"
     - If user approves, run `git pull origin main`
     - Check for conflicts after pull:
       - Run `git status` - look for "Unmerged paths" or "both modified" messages
       - If `git status` shows conflicts:
         - Inform user: "Merge conflicts detected. Please resolve conflicts manually and run /hpr again."
         - Stop the flow
       - If no conflicts (clean working tree or only "Your branch is ahead" message):
         - Continue to next step
   - If user declines pull, warn: "Proceeding without pulling from main. PR may have conflicts."

2. **Analyze changes vs main**: Run the following commands to understand all changes:
   - `git diff main...HEAD --stat` - Get statistics of changed files
   - `git diff main...HEAD` - Get full diff of changes
   - `git log main..HEAD --pretty=format:"%h %s"` - Get list of commits

3. **Generate PR description**: Based on the changes, create a comprehensive PR description with:
   - **Summary section**: 1-3 bullet points summarizing the changes
   - **Relevant Tests section**: List relevant test files that cover the changes
     - Look for test files matching changed files:
       - Python: `test_<module>.py` for `<module>.py`
       - Frontend: `<component>.spec.js` or `<feature>.spec.cjs` for component/feature changes
     - Group tests by area/module (Backend/Frontend)
     - **Note**: Only list the tests in the PR description - do NOT actually run them
   - **Required Manual Tests section**: List functionality without automated test coverage
     - Identify changes that don't have corresponding test files
     - Note what manual testing is needed
     - Suggest areas that should have tests added
   - Follow this format:

     ```
     ## Summary
     <1-3 bullet points>

     ## Relevant Tests
     **Backend - <Module/Area Name>**
     - `server/tests/test_<module>.py` - Description of what it tests

     **Frontend - <Component/Feature Name>**
     - `e2e/<feature>.spec.js` - Description of what it tests

     ## Required Manual Tests
     - <Functionality without tests> - Needs manual testing of <specific behavior>
     - <Another area> - Should add tests for <specific cases>
     ```

4. **Get PR title**:
   - Use the current branch name as the default title: `git branch --show-current`

5. **Present PR details for approval**: Show the user:
   - The PR title (branch name)
   - The generated PR description
   - Ask for approval before proceeding

6. **Create the PR**: Once approved, call the create_pr.py script:

   ```bash
   python management/devenv-setup-scripts/create_pr.py \
     --pr_title "$(git branch --show-current)" \
     --pr_body "$(cat <<'EOF'
     <generated PR description>
     EOF
     )"
   ```

7. **Show result**: Display the PR URL from the script output

## Important Notes

- The script will push the current branch to remote if not already pushed
- Make sure all commits are created before running this command
- The PR description should be informative enough for reviewers to understand the changes
