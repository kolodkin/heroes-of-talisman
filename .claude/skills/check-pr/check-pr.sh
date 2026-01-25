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
        echo "Installing on Linux..."
        wget -q https://github.com/cli/cli/releases/download/v2.62.0/gh_2.62.0_linux_amd64.tar.gz
        tar -xzf gh_2.62.0_linux_amd64.tar.gz

        # Try to install to /usr/local/bin with sudo, fallback to local install
        if sudo -n true 2>/dev/null; then
            sudo mv gh_2.62.0_linux_amd64/bin/gh /usr/local/bin/
            rm -rf gh_2.62.0_linux_amd64*
        else
            # Install to user's local bin directory
            mkdir -p ~/.local/bin
            mv gh_2.62.0_linux_amd64/bin/gh ~/.local/bin/
            rm -rf gh_2.62.0_linux_amd64*
            export PATH="$HOME/.local/bin:$PATH"
            echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.bashrc 2>/dev/null || true
        fi

        echo -e "${GREEN}✓ GitHub CLI installed successfully${NC}"
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

    echo -e "${GREEN}✓ Repository: ${NC}$REPO"
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

# Step 5: Check if PR exists for this branch
check_pr_exists() {
    echo ""
    echo -e "${BLUE}Checking for pull request...${NC}"

    PR_DATA=$(gh pr list --repo "$REPO" --head "$BRANCH" --json number,state,url 2>/dev/null)

    if [ -z "$PR_DATA" ] || [ "$PR_DATA" = "[]" ]; then
        echo -e "${RED}❌ No pull request found for branch '$BRANCH'${NC}"
        echo ""
        echo -e "${YELLOW}💡 Create a pull request first:${NC}"
        echo "  gh pr create --repo $REPO --head $BRANCH --base main --fill"
        exit 1
    fi

    PR_NUMBER=$(echo "$PR_DATA" | jq -r '.[0].number')
    PR_URL=$(echo "$PR_DATA" | jq -r '.[0].url')
    echo -e "${GREEN}✓ Pull request found: ${NC}#$PR_NUMBER"
    echo -e "${BLUE}  URL: ${NC}$PR_URL"
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
