# Front End Styling

## Styling System

### Use CSS Modules

# CSS Modules with Vite

CSS Modules in Vite work automatically for any CSS file ending with `.module.css`. Here are practical examples:

## Basic CSS Module Usage

### 1. Create a CSS Module File

**`styles.module.css`**

```css
.red {
  color: red;
}

.container {
  padding: 20px;
  border: 1px solid #ccc;
}

.button {
  background-color: blue;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
}
```

### 2. Import and Use in JavaScript

**`main.js`**

```javascript
import classes from "./styles.module.css";

// Use the classes
document.getElementById("foo").className = classes.red;
document.getElementById("container").className = classes.container;
document.getElementById("btn").className = classes.button;
```

## Named Imports (with camelCase conversion)

### CSS Module with kebab-case classes

**`example.module.css`**

```css
.apply-color {
  color: green;
}

.nav-item {
  display: inline-block;
  margin-right: 10px;
}

.header-title {
  font-size: 24px;
  font-weight: bold;
}
```

## React Component Example

**`Button.module.css`**

```css
.button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.button:hover {
  background-color: #0056b3;
}

.button--large {
  padding: 16px 32px;
  font-size: 18px;
}

.button--disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}
```

**`Button.jsx`**

```jsx
import styles from "./Button.module.css";

function Button({ children, large, disabled, onClick }) {
  const buttonClass = [styles.button, large && styles["button--large"], disabled && styles["button--disabled"]]
    .filter(Boolean)
    .join(" ");

  return (
    <button className={buttonClass} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}

export default Button;
```

## CSS Modules with Preprocessors

You can also use CSS Modules with preprocessors by prepending `.module` to the file extension:

**`styles.module.scss`**

```scss
$primary-color: #007bff;
$border-radius: 4px;

.card {
  border: 1px solid #ddd;
  border-radius: $border-radius;
  padding: 20px;

  &__header {
    color: $primary-color;
    font-size: 18px;
    margin-bottom: 10px;
  }

  &__body {
    color: #333;
    line-height: 1.5;
  }
}
```

**`Card.jsx`**

```jsx
import styles from "./styles.module.scss";

function Card({ title, children }) {
  return (
    <div className={styles.card}>
      <h3 className={styles.card__header}>{title}</h3>
      <div className={styles.card__body}>{children}</div>
    </div>
  );
}
```

### CSS Architecture

- **BEM Methodology**: Block-Element-Modifier naming
- **CSS Custom Properties**: Theme variables for easy customization
- **Responsive Breakpoints**: Mobile-first responsive design
- **Animation Classes**: Reusable transition effects
