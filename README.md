# MyPackage

A collection of utility functions for common tasks.

## Installation

```bash
pip install mypackage
```

Or from source:

```bash
git clone https://github.com/yourusername/mypackage.git
cd mypackage
pip install -e .
```

## Usage

```python
from mypackage import greet, add_numbers, calculate_average

# Greet someone
print(greet("Alice"))  # Hello, Alice!

# Add numbers
result = add_numbers(2, 3)  # 5

# Calculate average
avg = calculate_average([1, 2, 3, 4, 5])  # 3.0
```

## Available Functions

### Core Functions (available from package level)

- `add_numbers(a, b)`: Add two numbers
- `multiply_numbers(a, b)`: Multiply two numbers
- `greet(name="World")`: Generate a greeting message
- `calculate_average(numbers)`: Calculate average of a list
- `is_palindrome(text, case_sensitive=False)`: Check if text is a palindrome

### Additional Functions (available from utils module)

- `fibonacci(n)`: Generate Fibonacci sequence
- `factorial(n)`: Calculate factorial

## Testing

Run tests with pytest:

```bash
pytest mypackage/tests/
```

## License

MIT