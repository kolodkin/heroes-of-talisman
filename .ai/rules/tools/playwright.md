# Playwright MCP for Frontend Code Evaluation

## Overview

Playwright MCP is a Model Context Protocol server that enables AI agents to evaluate frontend code and changes through real browser automation. It provides structured accessibility snapshots for testing UI behavior, visual regression detection, and functional validation without requiring vision models.

## Key Benefits for Frontend Evaluation

- **Real Browser Testing**: Test actual user interactions in Chrome, Firefox, Safari
- **Accessibility Analysis**: Evaluate semantic structure and ARIA compliance
- **Performance Monitoring**: Measure load times, interactions, and Core Web Vitals
- **Cross-browser Validation**: Ensure consistent behavior across browsers
- **Visual Regression**: Detect unintended UI changes through screenshots
- **Responsive Testing**: Validate mobile and desktop layouts

## Frontend Code Evaluation Use Cases

### ✅ When to Use Playwright MCP

**Code Changes & Reviews:**

- Test new component functionality
- Validate form behavior and validation
- Check responsive design implementations
- Verify accessibility improvements
- Test navigation and routing changes

**UI/UX Validation:**

- Confirm visual design matches mockups
- Test user interaction flows
- Validate loading states and animations
- Check error handling and edge cases
- Verify cross-browser compatibility

**Performance & Optimization:**

- Measure page load performance
- Test lazy loading implementations
- Validate bundle size impact on load times
- Check for layout shifts (CLS)
- Monitor JavaScript execution performance

**Regression Testing:**

- Compare before/after screenshots
- Test existing functionality after changes
- Validate that bug fixes work correctly
- Ensure no unintended side effects

### ❌ When NOT to Use

- Unit testing individual functions
- Testing backend APIs directly
- Static code analysis
- Build process validation
- Server-side rendering without browser context

## Essential Commands for Frontend Evaluation

### Basic Navigation & Setup

```
"Navigate to localhost:3000 and take a screenshot of the homepage"
"Open the development server at http://localhost:5173"
"Test the mobile view of the current page using iPhone 15"
```

### Component Testing

```
"Click the 'Add to Cart' button and verify the cart count updates"
"Fill out the signup form with test data and submit"
"Test the dropdown menu functionality"
"Verify the modal opens when clicking the trigger button"
```

### Visual & Layout Validation

```
"Take screenshots of the page at desktop, tablet, and mobile breakpoints"
"Compare the current page layout with the previous version"
"Check if the navigation header is properly positioned"
"Verify the footer stays at the bottom of the page"
```

### Form & Interaction Testing

```
"Test form validation by submitting empty required fields"
"Fill out the contact form and verify success message appears"
"Test keyboard navigation through the form elements"
"Check if the search functionality returns expected results"
```

### Performance & Accessibility

```
"Measure the page load time and report Core Web Vitals"
"Check if all images have proper alt text"
"Verify the page is keyboard navigable"
"Test color contrast ratios for accessibility compliance"
```

## Frontend Evaluation Workflows

### 1. Code Change Validation

```
1. "Navigate to the updated page/component"
2. "Take a baseline screenshot"
3. "Test the new functionality step by step"
4. "Verify no existing features are broken"
5. "Test responsive behavior"
6. "Check accessibility compliance"
```

### 2. Visual Regression Testing

```
1. "Navigate to the page before changes"
2. "Take reference screenshots at multiple breakpoints"
3. "Apply code changes"
4. "Take new screenshots with same dimensions"
5. "Compare and report visual differences"
```

### 3. User Journey Testing

```
1. "Start at the entry point (homepage/landing)"
2. "Follow the complete user flow step by step"
3. "Test each interaction and transition"
4. "Verify the expected end state is reached"
5. "Check for any broken links or errors"
```

## Best Practices for Frontend Evaluation

### Effective Testing Strategies

- **Start with Critical Paths**: Test main user journeys first
- **Use Real Data**: Test with realistic content and data volumes
- **Test Edge Cases**: Empty states, error conditions, long content
- **Progressive Enhancement**: Test with JavaScript disabled
- **Network Conditions**: Test on slow connections

### Debugging & Troubleshooting

- **Save Traces**: Always enable trace saving for debugging
- **Use Specific Selectors**: Target elements by data attributes
- **Wait for Stability**: Ensure dynamic content is fully loaded
- **Check Console**: Monitor for JavaScript errors
- **Network Tab**: Watch for failed requests

### Reporting & Documentation

- **Screenshot Everything**: Document visual states
- **Record Interactions**: Save traces for complex user flows
- **Compare Versions**: Use before/after comparisons
- **Document Bugs**: Capture steps to reproduce issues
- **Performance Metrics**: Include load times and Core Web Vitals

## Example Frontend Evaluation Prompts

### Component Review

```
"I've updated the navigation component. Please test:
1. Navigation links work correctly
2. Mobile hamburger menu functions
3. Active state highlighting works
4. Dropdown menus are accessible
5. Take screenshots of all states"
```

### Form Validation Testing

```
"Test the new contact form validation:
1. Try submitting with empty fields
2. Test invalid email formats
3. Verify success message after valid submission
4. Check that error messages are accessible
5. Test keyboard navigation through the form"
```

### Responsive Design Validation

```
"Validate the responsive design changes:
1. Test on desktop (1920x1080)
2. Test on tablet (768x1024)
3. Test on mobile (375x667)
4. Check that no horizontal scrolling occurs
5. Verify touch targets are appropriately sized"
```

## Troubleshooting Frontend Testing

**Common Issues:**

- **Flaky Tests**: Use proper waits and stable selectors
- **Dynamic Content**: Wait for AJAX requests to complete
- **Authentication**: Use visible browser for manual login
- **Local Development**: Ensure dev server is running
- **CORS Issues**: Configure allowed origins properly
