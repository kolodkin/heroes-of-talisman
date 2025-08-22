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

## 🌐 Core Automation Tools

### Navigation & Page Control
- **`browser_navigate`** - Navigate to a URL
  - *Parameters:* `url` (string)
  - *Usage:* Navigate to any website or web application

- **`browser_navigate_back`** - Go back to previous page
  - *No parameters*
  - *Usage:* Browser back button functionality

- **`browser_navigate_forward`** - Go forward to next page
  - *No parameters*
  - *Usage:* Browser forward button functionality

- **`browser_close`** - Close the browser page
  - *No parameters*
  - *Usage:* Clean up and close current browser session

### Element Interactions
- **`browser_click`** - Perform click on web elements
  - *Parameters:* `element` (description), `ref` (exact reference), `doubleClick` (optional boolean)
  - *Usage:* Click buttons, links, or any clickable elements

- **`browser_type`** - Type text into editable elements
  - *Parameters:* `element`, `ref`, `text`, `submit` (optional), `slowly` (optional)
  - *Usage:* Fill forms, input fields, text areas

- **`browser_hover`** - Hover mouse over elements
  - *Parameters:* `element`, `ref`
  - *Usage:* Trigger hover effects, reveal tooltips

- **`browser_drag`** - Drag and drop between elements
  - *Parameters:* `startElement`, `startRef`, `endElement`, `endRef`
  - *Usage:* Drag and drop operations, reordering items

- **`browser_select_option`** - Select dropdown options
  - *Parameters:* `element`, `ref`, `values` (array)
  - *Usage:* Select from dropdowns, multi-select lists

- **`browser_press_key`** - Press keyboard keys
  - *Parameters:* `key` (key name or character)
  - *Usage:* Keyboard shortcuts, navigation, special key presses

### Page Information & Monitoring
- **`browser_snapshot`** - Capture accessibility snapshot
  - *No parameters*
  - *Usage:* Get structured page content for element selection and analysis

- **`browser_take_screenshot`** - Take visual screenshots
  - *Parameters:* `raw` (optional), `filename` (optional), `element` (optional), `ref` (optional)
  - *Usage:* Visual documentation, debugging, element-specific captures

- **`browser_console_messages`** - Get browser console logs
  - *No parameters*
  - *Usage:* Debug JavaScript errors, monitor console output

- **`browser_network_requests`** - List network requests
  - *No parameters*
  - *Usage:* Monitor API calls, track network activity

### Advanced Interactions
- **`browser_evaluate`** - Execute JavaScript code
  - *Parameters:* `function` (JavaScript code), `element` (optional), `ref` (optional)
  - *Usage:* Custom JavaScript execution, data extraction

- **`browser_file_upload`** - Upload files
  - *Parameters:* `paths` (array of file paths)
  - *Usage:* Upload documents, images, or any files

- **`browser_handle_dialog`** - Handle browser dialogs
  - *Parameters:* `accept` (boolean), `promptText` (optional)
  - *Usage:* Handle alerts, confirms, prompts

- **`browser_wait_for`** - Wait for conditions
  - *Parameters:* `time` (optional), `text` (optional), `textGone` (optional)
  - *Usage:* Wait for page loads, content changes, specific text

- **`browser_resize`** - Resize browser window
  - *Parameters:* `width` (number), `height` (number)
  - *Usage:* Test responsive design, change viewport

## 📑 Tab Management (Capability Required)

- **`browser_tab_list`** - List all open tabs
  - *No parameters*
  - *Usage:* View all browser tabs and their status

- **`browser_tab_new`** - Open new tab
  - *Parameters:* `url` (optional)
  - *Usage:* Create new browser tabs

- **`browser_tab_select`** - Switch to specific tab
  - *Parameters:* `index` (tab number)
  - *Usage:* Navigate between multiple tabs

- **`browser_tab_close`** - Close specific tab
  - *Parameters:* `index` (optional, closes current if not specified)
  - *Usage:* Close unwanted tabs

## 🔧 System & Installation

- **`browser_install`** - Install browser
  - *No parameters*
  - *Usage:* Install required browser if missing

## 🎯 Coordinate-Based Tools (--caps=vision)

- **`browser_mouse_click_xy`** - Click at coordinates
  - *Parameters:* `element`, `x`, `y`
  - *Usage:* Precise coordinate-based clicking

- **`browser_mouse_move_xy`** - Move mouse to coordinates
  - *Parameters:* `element`, `x`, `y`
  - *Usage:* Hover at specific positions

- **`browser_mouse_drag_xy`** - Drag between coordinates
  - *Parameters:* `element`, `startX`, `startY`, `endX`, `endY`
  - *Usage:* Precise drag and drop operations

## 📄 PDF Generation (--caps=pdf)

- **`browser_pdf_save`** - Save page as PDF
  - *Parameters:* `filename` (optional)
  - *Usage:* Generate PDF documents from web pages

## 🚀 Usage Patterns

### Basic Web Automation
1. `browser_navigate` → Navigate to target site
2. `browser_snapshot` → Get page structure
3. `browser_click/type` → Interact with elements
4. `browser_take_screenshot` → Document results

### Form Filling
1. `browser_navigate` → Go to form page
2. `browser_type` → Fill input fields
3. `browser_select_option` → Select dropdown values
4. `browser_file_upload` → Upload files if needed
5. `browser_click` → Submit form

### Multi-Tab Workflow
1. `browser_tab_new` → Open additional tabs
2. `browser_tab_select` → Switch between tabs
3. Perform operations in each tab
4. `browser_tab_close` → Clean up when done

### Testing & Debugging
1. `browser_console_messages` → Check for errors
2. `browser_network_requests` → Monitor API calls
3. `browser_evaluate` → Run custom checks
4. `browser_take_screenshot` → Visual verification

## Frontend Code Evaluation Use Cases

### ✅ When to Use Playwright MCP

**Code Changes & Reviews:**

- Test new component functionality
- Validate form behavior and validation
- Check responsive design implementations
- Verify accessibility improvements
- Test navigation and routing changes

**UI/UX Validation:**

- Test user interaction flows
- Validate loading states and animations
- Check error handling and edge cases

### ❌ When NOT to Use

- Unit testing individual functions
- Testing backend APIs directly
- Static code analysis
- Build process validation
- Server-side rendering without browser context

## Essential Commands for Frontend Evaluation

### Basic Navigation & Setup

```
"Navigate to localhost:5173 and take a screenshot of the homepage"
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

- **Screenshot Everything**: For each visual state, instruct the AI to take a screenshot and save it with an enumerated filename indicating the flow, using the format "{i}-{name}.jpg" (e.g., 001-start.jpg, 002-after-click.jpg).
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
