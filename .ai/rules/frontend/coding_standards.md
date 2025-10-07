# Frontend Coding Standards

## React Imports

### Prefer Destructured Imports

Always use destructured imports for React hooks and features instead of accessing them from the React object.

**Good:**

```javascript
import React, { useState, useEffect, useCallback } from "react";

function MyComponent() {
  const [count, setCount] = useState(0);
  // ...
}
```

**Avoid:**

```javascript
import React from "react";

function MyComponent() {
  const [count, setCount] = React.useState(0); // Don't do this
  // ...
}
```
