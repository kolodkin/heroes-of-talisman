---
name: playwright
description: Browser automation and frontend testing and evaluation with Playwright MCP
---

# Playwright Frontend Testing Skill

Use this skill for browser automation, frontend testing, and UI validation using Playwright MCP tools.

## When to Use This Skill

**✅ Use for:**

- Testing new component functionality
- Validating form behavior and validation
- Checking responsive design implementations
- Verifying accessibility improvements
- Testing navigation and routing changes
- Testing user interaction flows
- Validating loading states and animations
- Visual regression detection
- Performance monitoring and Core Web Vitals

**❌ Do NOT use for:**

- Unit testing individual functions (use pytest/jest instead)
- Testing backend APIs directly (use API testing tools)
- Static code analysis
- Build process validation

## Available Tools

You have access to all `mcp__playwright__*` tools:

- `browser_navigate` - Navigate to URLs
- `browser_snapshot` - Get accessibility snapshot (better than screenshot for interactions)
- `browser_take_screenshot` - Capture visual state
- `browser_click` - Click elements
- `browser_type` - Type into fields
- `browser_select_option` - Select dropdown options
- `browser_fill_form` - Fill multiple form fields at once
- `browser_console_messages` - Check for console errors
- `browser_network_requests` - Monitor network activity
- `browser_evaluate` - Run JavaScript in page context
- `browser_tabs` - Manage browser tabs
- `browser_wait_for` - Wait for text or time

## Testing Workflows

### 1. Code Change Validation

```
1. Navigate to the updated page/component
2. Take a baseline screenshot
3. Test the new functionality step by step
4. Verify no existing features are broken
5. Test responsive behavior
6. Check accessibility compliance
```

### 2. Visual Regression Testing

```
1. Navigate to the page before changes
2. Take reference screenshots at multiple breakpoints
3. Apply code changes
4. Take new screenshots with same dimensions
5. Compare and report visual differences
```

### 3. User Journey Testing

```
1. Start at the entry point (homepage/landing)
2. Follow the complete user flow step by step
3. Test each interaction and transition
4. Verify the expected end state is reached
5. Check for any broken links or errors
```

## Best Practices

### DOM Selection

- **Use data attributes** or CSS class selectors (e.g., `[data-battle-participant="player"]`, `[class*="diceContainer"]`)
- **Avoid** selecting by DOM type (`h2`, `div`, `span`) or text content
- **Never** use text-based selectors that break with translations

### Screenshot Guidelines

- **Take a screenshot after every UI update** with descriptive filenames (e.g., `start.jpg`, `after-click.jpg`)
- Use `browser_snapshot` for getting page structure for interactions
- Use `browser_take_screenshot` for visual documentation

### Waiting & Stability

- **Avoid** `waitForTimeout()` - use `expect(element).toBeVisible()` instead
- Wait for dynamic content to fully load before assertions
- Ensure AJAX requests complete before proceeding

### Testing Strategy

- Start with critical paths first
- Test with realistic data volumes
- Test edge cases: empty states, errors, long content
- Test on multiple breakpoints (desktop, tablet, mobile)
- Check console for JavaScript errors
- Monitor network requests for failures

## Common Testing Patterns

### Component Testing

```
1. Navigate to page with component
2. Take baseline screenshot
3. Interact with component (click, type, etc.)
4. Verify expected state changes
5. Screenshot final state
6. Check console for errors
```

### Form Testing

```
1. Navigate to form page
2. Test validation with empty/invalid data
3. Fill form with valid data
4. Submit and verify success state
5. Test keyboard navigation
6. Verify error messages are accessible
```

### Responsive Design Testing

```
1. Resize browser to desktop (1920x1080)
2. Screenshot and test functionality
3. Resize to tablet (768x1024)
4. Screenshot and test functionality
5. Resize to mobile (375x667)
6. Screenshot and test functionality
7. Verify no horizontal scrolling
8. Check touch target sizes
```

## Development Server

For this project, the development server runs on:

- **Frontend (www)**: http://localhost:5173
- **Backend (server)**: http://localhost:8000

Always ensure the dev server is running before testing.

## Troubleshooting

**Common Issues:**

- **Flaky Tests**: Use proper waits and stable selectors
- **Dynamic Content**: Wait for AJAX requests to complete
- **Authentication**: Use visible browser for manual login
- **Local Development**: Ensure dev server is running
- **CORS Issues**: Configure allowed origins properly

## Instructions

When activated, you should:

1. **Understand the testing goal** - Clarify what needs to be tested
2. **Plan the test flow** - Create a TodoList with test steps
3. **Navigate to the target** - Use `browser_navigate` to reach the page
4. **Capture initial state** - Use `browser_snapshot` and `browser_take_screenshot`
5. **Execute test steps** - Interact with the UI using appropriate tools
6. **Verify expected behavior** - Check console, network, and UI state
7. **Document results** - Take screenshots of each state change
8. **Report findings** - Summarize what worked and what failed

Remember to use descriptive filenames for screenshots and always check the console for errors after interactions.
