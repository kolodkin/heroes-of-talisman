# GitMCP

## Overview

GitMCP is a free, remote MCP server that connects AI agents to any GitHub repository documentation. It eliminates code hallucinations by providing access to current, accurate documentation.

## URL Formats

- **Specific repo**: `gitmcp.io/{owner}/{repo}`
- **Dynamic access**: `gitmcp.io/docs` (AI picks repo on demand)
- **GitHub Pages**: `{owner}.gitmcp.io/{repo}`

## When to Use GitMCP

✅ **Use When:**

- Working with unfamiliar libraries
- Need current documentation/examples
- Implementing features from specific projects
- Want to avoid code hallucinations
- Quick access to README, API docs, code samples

❌ **Don't Use When:**

- Basic programming concepts (no specific repo needed)
- General coding questions
- You already have sufficient context

## Available Tools

- Documentation fetching
- Smart semantic search
- Code search and analysis
- Repository structure exploration

## Best Practices

1. Use specific URLs for focused work: `gitmcp.io/microsoft/playwright`
2. Use generic endpoint for exploration: `gitmcp.io/docs`
3. No installation required - just add URL to config
4. Privacy-focused - no data collection or storage

## Examples

- Playwright: `https://gitmcp.io/microsoft/playwright`
- LangGraph: `https://langchain-ai.gitmcp.io/langgraph`
- TypeScript: `https://gitmcp.io/microsoft/typescript`
