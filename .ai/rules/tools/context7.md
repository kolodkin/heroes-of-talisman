
# Context7 MCP Tool

## Overview

This instruction set provides comprehensive guidelines for effectively utilize Context7 MCP (Model Context Protocol) for retrieving up-to-date, version-specific documentation and code examples. Context7 eliminates outdated information and hallucinated APIs by pulling documentation directly from source repositories.

## Core Principles

### 1. Always Use Current Documentation
- **Problem**: LLMs rely on training data that may be months or years old
- **Solution**: Leverage Context7 to fetch real-time documentation
- **Implementation**: When discussing libraries, frameworks, or APIs, always retrieve current docs

### 2. Prefer Accuracy Over Speed
- Better to take extra time retrieving current docs than provide outdated information
- Verify library compatibility and version-specific features
- Use Context7 for any library-related queries, especially for:
  - New or rapidly evolving frameworks (Next.js, React, Vue, etc.)
  - Lesser-known packages not well-represented in training data
  - Version-specific features or breaking changes

### 3. Provide Working Code Examples
- All code examples should be based on current documentation
- Include proper imports, syntax, and patterns from official sources
- Test suggestions against latest API specifications

## Tool Usage Guidelines

### Available Tools

#### 1. `resolve-library-id`
**Purpose**: Convert library names to Context7-compatible IDs

**When to Use**:
- User mentions a library by common name
- Need to identify the correct package from multiple options
- Unclear which specific library/version user wants

**Parameters**:
- `libraryName` (required): The name of the library to search for

**Example Usage**:
```
User: "How do I use React hooks?"
Agent: First resolve "react" to get the correct library ID
```

#### 2. `get-library-docs`
**Purpose**: Fetch up-to-date documentation for a specific library

**When to Use**:
- After resolving library ID
- User provides explicit Context7 ID (format: `/org/project` or `/org/project/version`)
- Need specific topic documentation

**Parameters**:
- `context7CompatibleLibraryID` (required): Exact Context7 ID
- `topic` (optional): Focus on specific area (e.g., "routing", "hooks", "authentication")
- `tokens` (optional): Max tokens to return (minimum 10000)

**Example Usage**:
```
get-library-docs with ID "/vercel/next.js" and topic "middleware"
```

## Workflow Patterns

### Pattern 1: User Mentions Library by Name
```
1. User asks about "Express.js authentication"
2. Call resolve-library-id with libraryName="express"
3. Select appropriate library from results
4. Call get-library-docs with resolved ID and topic="authentication"
5. Provide answer based on current documentation
```

### Pattern 2: User Provides Specific Context7 ID
```
1. User says "use library /mongodb/docs for authentication"
2. Skip resolve step
3. Call get-library-docs directly with ID="/mongodb/docs" and topic="authentication"
4. Provide current documentation-based response
```

### Pattern 3: General Library Question
```
1. User asks "What's new in React 18?"
2. Call resolve-library-id with libraryName="react"
3. Call get-library-docs with resolved ID
4. Analyze documentation for version-specific features
5. Highlight new features with examples
```

## Decision Tree for Context7 Usage

```
Is user asking about a library/framework/API?
├── YES
│   ├── Is it a well-established, slowly-changing technology? (HTML, CSS basics)
│   │   ├── NO → Use Context7
│   │   └── YES → Consider Context7 for completeness
│   ├── Is it mentioned in user's recent messages?
│   │   ├── YES → Use Context7 for consistency
│   │   └── NO → Evaluate necessity
│   └── Is accuracy critical for the task?
│       ├── YES → Always use Context7
│       └── NO → Use Context7 for better results
└── NO → Proceed without Context7
```

## Best Practices

### Do's
- **Always resolve library ID first** unless user provides explicit Context7 format
- **Use topic parameter** to focus documentation retrieval
- **Combine multiple calls** when user asks about different aspects
- **Reference documentation sources** in responses
- **Validate suggestions** against retrieved documentation
- **Handle version differences** when multiple versions exist

### Don'ts
- **Don't skip Context7** for popular libraries (they change frequently)
- **Don't assume library names** - always resolve first
- **Don't provide generic examples** when specific docs are available
- **Don't ignore version compatibility** issues
- **Don't mix old training data** with new documentation

## Response Formatting

### Code Examples
```javascript
// ✅ Based on current Next.js 14 documentation via Context7
import { NextRequest, NextResponse } from 'next/server'

export function middleware(request: NextRequest) {
  // Current implementation pattern
}
```

### Documentation References
Always indicate when information comes from Context7:
- "According to the current Next.js documentation..."
- "Based on the latest MongoDB docs..."
- "The current React documentation shows..."

### Version Awareness
```
// For React 18+ (current documentation)
const [state, setState] = useState(initialState)

// Note: This replaces the older class-based approach
```

## Error Handling

### Library Not Found
```
If resolve-library-id returns no results:
1. Suggest similar libraries
2. Ask user to clarify the exact library name
3. Provide general guidance if appropriate
```

### Documentation Unavailable
```
If get-library-docs fails:
1. Inform user of the limitation
2. Offer to help with general knowledge
3. Suggest checking official documentation directly
```

### Ambiguous Libraries
```
If multiple libraries match:
1. Present options to user
2. Ask for clarification
3. Choose most popular/relevant if context is clear
```

## Advanced Usage

### Multi-Library Queries
```
User: "How do I connect Next.js with Prisma?"
1. Resolve both "next.js" and "prisma"
2. Get docs for Next.js with topic "database"
3. Get docs for Prisma with topic "integration"
4. Combine information for comprehensive answer
```

### Version-Specific Queries
```
User: "What changed in Next.js 14?"
1. Resolve "next.js"
2. Get docs for current version
3. Look for migration guides or changelog sections
4. Highlight breaking changes and new features
```

### Comparative Analysis
```
User: "Should I use Axios or Fetch?"
1. Resolve and get docs for both
2. Compare current capabilities
3. Provide recommendation based on latest features
```

## Quality Assurance

### Verification Checklist
- [ ] Used Context7 for all library-related information
- [ ] Resolved library IDs properly
- [ ] Focused on relevant topics
- [ ] Provided working, current code examples
- [ ] Referenced documentation sources
- [ ] Handled version compatibility
- [ ] Offered additional resources when needed

### Response Validation
Before providing final answer:
1. Ensure all code examples use current syntax
2. Verify imports and dependencies are correct
3. Check for deprecated methods or patterns
4. Confirm version compatibility notes

## Integration with Other Tools

### When to Combine Context7 with Other MCP Servers
- **File operations**: Use Context7 for library docs, file MCP for project structure
- **Web search**: Use Context7 for official docs, web search for community examples
- **Database queries**: Use Context7 for ORM docs, database MCP for schema operations

### Complementary Information Sources
- Context7: Official documentation and examples
- Web search: Community tutorials and troubleshooting
- Code analysis: Project-specific implementation patterns

## Continuous Improvement

### Feedback Integration
- Monitor which libraries are frequently requested
- Note common documentation gaps
- Track user satisfaction with Context7-enhanced responses
- Suggest new libraries for Context7 inclusion

### Staying Current
- Context7 automatically updates documentation
- No need to manually track library changes
- Trust Context7 for latest information over training data
- Regular validation ensures accuracy

## Troubleshooting Common Issues

### Module Resolution Errors
```
If Context7 returns module errors:
1. Try alternative library names
2. Check for typos in library names
3. Suggest official package names
4. Provide manual documentation links as fallback
```

### Rate Limiting
```
If hitting rate limits:
1. Inform user of temporary limitation
2. Provide cached knowledge where appropriate
3. Suggest trying again shortly
4. Offer alternative information sources
```

### Outdated Context7 Data
```
If Context7 data seems outdated:
1. Note the potential issue
2. Suggest checking official sources
3. Provide best available information
4. Document for improvement
```

## Success Metrics

### Quality Indicators
- Code examples work without modification
- No deprecated API usage in suggestions
- Version-appropriate recommendations
- Reduced user follow-up questions about outdated information

### User Experience Goals
- Faster development with accurate information
- Reduced debugging time from outdated examples
- Increased confidence in AI-provided code
- Better integration with modern development workflows

---

*This instruction set should be regularly updated to reflect improvements in Context7 MCP capabilities and emerging best practices in AI-assisted development.*