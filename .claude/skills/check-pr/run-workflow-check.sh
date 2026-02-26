#!/bin/bash
#
# GitHub Actions Workflow Checker
# Installs gh CLI if needed, polls workflow status, and reports results
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# GitHub CLI version for installation
GH_VERSION="2.62.0"
GH_ARCHIVE="gh_${GH_VERSION}_linux_amd64"

echo -e "${BLUE}🔍 GitHub Actions Workflow Checker${NC}"
echo ""

# Step 1: Install gh CLI if not available
install_gh() {
    if command -v gh &> /dev/null; then
        echo -e "${GREEN}✓ GitHub CLI already installed${NC}"
        gh --version
        return 0
    fi

    echo -e "${YELLOW}⚠️  GitHub CLI not found. Installing...${NC}"

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Installing on Linux (local)..."
        wget -q "https://github.com/cli/cli/releases/download/v${GH_VERSION}/${GH_ARCHIVE}.tar.gz"
        tar -xzf "${GH_ARCHIVE}.tar.gz"
        mkdir -p ~/.local/bin
        mv "${GH_ARCHIVE}/bin/gh" ~/.local/bin/
        rm -rf "${GH_ARCHIVE}"*
        export PATH="$HOME/.local/bin:$PATH"
        echo -e "${GREEN}✓ GitHub CLI installed successfully (~/.local/bin)${NC}"
        gh --version

    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Installing on macOS..."
        if command -v brew &> /dev/null; then
            brew install gh
            echo -e "${GREEN}✓ GitHub CLI installed successfully${NC}"
        else
            echo -e "${RED}❌ Error: Homebrew not found${NC}"
            echo "Please install Homebrew first: https://brew.sh"
            exit 1
        fi
    else
        echo -e "${RED}❌ Error: Unsupported OS: $OSTYPE${NC}"
        exit 1
    fi
}

# Step 2: Check authentication
check_auth() {
    echo ""
    echo -e "${BLUE}Checking authentication...${NC}"

    if ! gh auth status &> /dev/null; then
        echo -e "${RED}❌ Not authenticated with GitHub CLI${NC}"
        echo ""
        echo "Please authenticate:"
        echo "  1. Run: gh auth login"
        echo "  2. Or set: export GH_TOKEN=<your-token>"
        exit 1
    fi

    echo -e "${GREEN}✓ Authenticated${NC}"
}

# Step 3: Detect GitHub repository
detect_repo() {
    echo ""
    echo -e "${BLUE}Detecting GitHub repository...${NC}"

    # Try to get repo from git remote
    REMOTE_URL=$(git remote get-url origin 2>/dev/null)

    if [ -z "$REMOTE_URL" ]; then
        echo -e "${RED}❌ Error: No git remote found${NC}"
        exit 1
    fi

    # Extract owner/repo from various remote URL formats
    # Handle: http://*/git/owner/repo, https://github.com/owner/repo, git@github.com:owner/repo
    if [[ "$REMOTE_URL" =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
        REPO="${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
    elif [[ "$REMOTE_URL" =~ /git/([^/]+)/([^/.]+) ]]; then
        # Handle local proxy format: http://local_proxy@127.0.0.1:*/git/owner/repo
        REPO="${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
    else
        echo -e "${RED}❌ Error: Could not parse repository from remote URL: $REMOTE_URL${NC}"
        echo "Please set manually: export GITHUB_REPOSITORY=owner/repo"
        exit 1
    fi

    # Parse owner and repo name
    REPO_OWNER=$(echo "$REPO" | cut -d'/' -f1)
    REPO_NAME=$(echo "$REPO" | cut -d'/' -f2)

    echo -e "${GREEN}✓ REPO: ${NC}$REPO"
    echo -e "${GREEN}✓ REPO_OWNER: ${NC}$REPO_OWNER"
    echo -e "${GREEN}✓ REPO_NAME: ${NC}$REPO_NAME"
}

# Step 4: Get current branch
get_branch() {
    BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [ -z "$BRANCH" ]; then
        echo -e "${RED}❌ Error: Not a git repository${NC}"
        exit 1
    fi
    echo -e "${BLUE}📝 Branch: ${NC}$BRANCH"
}

# Step 4.5: Check if PR exists for this branch
check_pr_exists() {
    echo ""
    echo -e "${BLUE}Checking for pull request...${NC}"

    # Check if PR exists for this branch
    PR_DATA=$(gh pr list --repo "$REPO" --head "$BRANCH" --json number,state,url 2>/dev/null)

    if [ -z "$PR_DATA" ] || [ "$PR_DATA" = "[]" ]; then
        echo -e "${YELLOW}⚠️  No pull request found for branch '$BRANCH'${NC}"
        echo ""
        echo -e "${YELLOW}ℹ️  Workflow runs only trigger for:${NC}"
        echo "  • Pushes to main/master branches"
        echo "  • Pull requests targeting main/master"
        echo ""
        echo -e "${YELLOW}💡 To trigger CI checks, create a pull request:${NC}"
        echo "  gh pr create --repo $REPO --head $BRANCH --base main --fill"
        echo ""
        echo -e "${YELLOW}Or push to main/master branch (if you have permissions)${NC}"
        echo ""
        return 1
    else
        PR_NUMBER=$(echo "$PR_DATA" | jq -r '.[0].number')
        PR_URL=$(echo "$PR_DATA" | jq -r '.[0].url')
        echo -e "${GREEN}✓ Pull request found: ${NC}#$PR_NUMBER"
        echo -e "${BLUE}  URL: ${NC}$PR_URL"
        return 0
    fi
}

# Step 5: Check for PR review comments
check_review_comments() {
    echo ""
    echo -e "${BLUE}🔍 Checking for unresolved PR review comments...${NC}"
    echo ""

    # Get PR review decision
    REVIEW_DATA=$(gh pr view "$PR_NUMBER" --repo "$REPO" --json reviewDecision 2>/dev/null)

    if [ -z "$REVIEW_DATA" ]; then
        echo -e "${YELLOW}⚠️  Could not fetch PR review data${NC}"
        return 0
    fi

    REVIEW_DECISION=$(echo "$REVIEW_DATA" | jq -r '.reviewDecision')
    echo -e "${BLUE}Review Status: ${NC}$REVIEW_DECISION"

    # Get unresolved review threads using GraphQL API (fetch ALL comments per thread)
    UNRESOLVED_THREADS=$(gh api graphql -f query='
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $number) {
          reviewThreads(first: 100) {
            nodes {
              isResolved
              comments(first: 100) {
                nodes {
                  databaseId
                  path
                  body
                  line
                  author {
                    login
                  }
                }
              }
            }
          }
        }
      }
    }' -f owner="${REPO%/*}" -f repo="${REPO#*/}" -F number="$PR_NUMBER" 2>/dev/null)

    # Count unresolved threads
    UNRESOLVED_COUNT=$(echo "$UNRESOLVED_THREADS" | jq -r '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)] | length' 2>/dev/null || echo "0")

    if [ "$UNRESOLVED_COUNT" -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}📝 PR HAS $UNRESOLVED_COUNT UNRESOLVED REVIEW THREAD(S)${NC}"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""

        # Display each unresolved thread that needs a response.
        # Shows ALL reviewer comments after the last [Agent] reply (not just the last one).
        echo "$UNRESOLVED_THREADS" | jq -r '
            .data.repository.pullRequest.reviewThreads.nodes[] |
            select(.isResolved == false) |
            .comments.nodes as $comments |
            # Root comment info (for file/line context and reply ID)
            ($comments[0].databaseId // "N/A") as $root_id |
            ($comments[0].path // "N/A") as $path |
            ($comments[0].line // "N/A") as $line |
            # Only show threads where the last comment is NOT from agent (needs response)
            select(($comments | last).body | startswith("[Agent]") | not) |
            # Find index of last agent comment (-1 if none)
            ([ range($comments | length) | select($comments[.].body | startswith("[Agent]")) ] | if length > 0 then last else -1 end) as $last_agent_idx |
            # Collect all non-agent comments after the last agent comment
            [ range($last_agent_idx + 1; $comments | length) | $comments[.] | select(.body | startswith("[Agent]") | not) ] as $pending |
            # Format: header with file/line, then each pending comment
            "File: \($path)\nLine: \($line)\nReply-To-ID: \($root_id)",
            ($pending[] | "  > \(.body)"),
            "---"
        ' 2>/dev/null

        # Count threads that actually need response (last comment is not from agent)
        NEEDS_RESPONSE=$(echo "$UNRESOLVED_THREADS" | jq -r '
            [.data.repository.pullRequest.reviewThreads.nodes[] |
            select(.isResolved == false) |
            .comments.nodes | last |
            select(.body | startswith("[Agent]") | not)] | length
        ' 2>/dev/null || echo "0")

        if [ "$NEEDS_RESPONSE" = "0" ]; then
            echo -e "${GREEN}✅ All unresolved threads have been responded to (awaiting reviewer resolution)${NC}"
        fi

        echo ""
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "${YELLOW}💡 See SKILL.md 'Address PR Review Comments' section for reply guidelines${NC}"
        echo ""
    else
        echo -e "${GREEN}✅ No unresolved review comments${NC}"
        echo ""
    fi

    # Check review decision
    if [ "$REVIEW_DECISION" = "CHANGES_REQUESTED" ]; then
        echo -e "${YELLOW}⚠️  Changes requested by reviewers${NC}"
        echo -e "${YELLOW}Please address all feedback and push changes${NC}"
        echo ""
        return 0
    elif [ "$REVIEW_DECISION" = "APPROVED" ]; then
        echo -e "${GREEN}✅ PR is approved!${NC}"
        echo ""
        return 0
    elif [ "$REVIEW_DECISION" = "REVIEW_REQUIRED" ]; then
        echo -e "${YELLOW}⏳ PR is awaiting review${NC}"
        if [ "$UNRESOLVED_COUNT" -gt 0 ]; then
            echo -e "${YELLOW}But unresolved comments exist - consider addressing them${NC}"
        fi
        echo ""
        return 0
    else
        echo -e "${BLUE}ℹ️  Review status: $REVIEW_DECISION${NC}"
        echo ""
        return 0
    fi
}

# Helper: Print artifacts link
print_artifacts_link() {
    local run_id="$1"
    if [ -z "$run_id" ]; then
        return
    fi

    # Get run number from run ID
    local run_number=$(gh run view "$run_id" --repo "$REPO" --json number --jq '.number' 2>/dev/null)
    if [ -z "$run_number" ] || [ "$run_number" = "null" ]; then
        return
    fi

    local artifacts_url="https://${REPO_OWNER}.github.io/artifact-view/${REPO_NAME}/playwright-report/${run_number}"

    echo ""
    echo -e "${BLUE}📸 View artifacts: ${NC}$artifacts_url"
}

# Step 6: Poll PR checks using gh pr checks --watch
poll_checks() {
    echo ""
    echo -e "${BLUE}⏳ Waiting for GitHub to process push...${NC}"
    sleep 3

    # Show initial status
    echo -e "${BLUE}Current check status:${NC}"
    gh pr checks "$PR_NUMBER" --repo "$REPO" 2>/dev/null || true
    echo ""

    # Watch until all checks complete
    echo -e "${BLUE}⏳ Watching checks until completion...${NC}"
    if timeout 1200 gh pr checks "$PR_NUMBER" --repo "$REPO" --watch 2>/dev/null; then
        echo ""
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}STATUS: SUCCESS${NC}"
        echo -e "${GREEN}PR: #$PR_NUMBER${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

        # Print artifacts link
        RUN_ID=$(gh run list --repo "$REPO" --branch "$BRANCH" --limit 1 --json databaseId -q '.[0].databaseId' 2>/dev/null)
        print_artifacts_link "$RUN_ID"

        # Check for PR review comments after CI passes
        check_review_comments
        exit 0
    fi

    # Failed - show status and fetch error logs
    echo ""
    echo -e "${RED}❌ Some checks FAILED!${NC}"
    echo ""
    gh pr checks "$PR_NUMBER" --repo "$REPO" 2>/dev/null || true
    echo ""

    # Get failed logs
    RUN_ID=$(gh run list --repo "$REPO" --branch "$BRANCH" --limit 1 --json databaseId -q '.[0].databaseId' 2>/dev/null)
    echo -e "${YELLOW}📋 Fetching error logs (run $RUN_ID)...${NC}"
    echo ""

    LOGS=$(gh run view "$RUN_ID" --repo "$REPO" --log-failed 2>&1)

    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}STATUS: FAILURE${NC}"
    echo -e "${RED}PR: #$PR_NUMBER | RUN: $RUN_ID${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "$LOGS"
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    print_artifacts_link "$RUN_ID"
    echo -e "${YELLOW}💡 Agent should analyze and fix these errors${NC}"
    exit 1
}

# Main execution
main() {
    install_gh
    check_auth
    detect_repo
    get_branch
    check_pr_exists
    poll_checks
}

main
