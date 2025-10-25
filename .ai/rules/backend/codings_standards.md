## String Literals and Type Safety

When working with string constants in Python code:

- **Use Literal types** from `typing.Literal` to define valid string values for variables and function parameters
- **Combine multiple Literal types** when a variable can accept values from different string sets

**Implementation pattern:**

```python
from typing import Literal

# Define literals
APPLES = 'apples'
BANANAS = 'bananas'
FRUITE_TYPES = [APPLES, BANANAS]
FruitType = Literal[*FRUITE_TYPES]  # Combined type for mixed usage

def eat_fruit(fruit: FruitType) -> None:
    """Accept only validated string values with compile-time checking."""
    pass
```
