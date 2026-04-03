# Validation Module

A comprehensive data validation module for Python with type hints and extensive documentation.

## Overview

The validation module provides a set of functions for validating various data types, including:
- Type validation
- Range validation for numeric values
- String validation with length constraints and regex patterns
- Email and URL validation
- Date string validation
- Dictionary structure validation
- JSON validation
- Custom validation rules

## Installation

The module is part of the `mypackage` package. Import it as:

```python
from mypackage.validation import validate_email, validate_type, validate_range, ValidationError
```

## Key Features

### 1. Basic Validation Functions

#### `validate_type(value, expected_type, allow_none=False)`
Validate that a value is of the expected type.

```python
validate_type(42, int)  # True
validate_type("hello", int)  # False
validate_type(None, int, allow_none=True)  # True
```

#### `validate_range(value, min_val=None, max_val=None, inclusive=True)`
Validate that a numeric value is within a specified range.

```python
validate_range(5, min_val=0, max_val=10)  # True
validate_range(15, min_val=0, max_val=10)  # False
```

#### `validate_string(value, min_length=None, max_length=None, pattern=None, allowed_values=None)`
Validate a string against various constraints.

```python
validate_string("hello", min_length=3, max_length=10)  # True
validate_string("test@example.com", pattern=r'^[^@]+@[^@]+\.[^@]+$')  # True
```

### 2. Specialized Validators

#### `validate_email(email)`
Validate email address format.

```python
validate_email("test@example.com")  # True
validate_email("invalid-email")  # False
```

#### `validate_url(url, require_https=False)`
Validate URL format.

```python
validate_url("https://example.com")  # True
validate_url("http://example.com", require_https=True)  # False
```

#### `validate_date_string(date_str, format="%Y-%m-%d")`
Validate date string against a specified format.

```python
validate_date_string("2023-12-25")  # True
validate_date_string("25/12/2023", "%d/%m/%Y")  # True
```

### 3. Complex Data Validation

#### `validate_dict_structure(data, schema, strict=False)`
Validate a dictionary against a schema definition.

```python
schema = {"name": str, "age": int, "email": str}
data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
is_valid, errors = validate_dict_structure(data, schema)  # (True, [])
```

#### `validate_json_string(json_str, schema=None)`
Validate a JSON string and optionally validate against a schema.

```python
json_str = '{"name": "Alice", "age": 30}'
is_valid, result = validate_json_string(json_str)  # (True, {'name': 'Alice', 'age': 30})
```

### 4. Custom Validation

#### `validate_with_custom_rules(value, rules)`
Validate a value against a list of custom validation rules.

```python
def is_positive(x):
    return x > 0, "Value must be positive"

def is_even(x):
    return x % 2 == 0, "Value must be even"

rules = [is_positive, is_even]
is_valid, errors = validate_with_custom_rules(4, rules)  # (True, [])
```

#### `create_validator(**constraints)`
Create a validator function with multiple constraints.

```python
age_validator = create_validator(min_val=0, max_val=150)
is_valid, error = age_validator(30)  # (True, '')
is_valid, error = age_validator(200)  # (False, 'Value must be between 0 and 150')
```

### 5. Exception-based Validation

#### `ValidationError`
Custom exception for validation errors.

```python
raise ValidationError("Value must be positive", field="age")
```

#### `validate_and_raise(value, validator, error_message, field=None)`
Validate a value and raise ValidationError if validation fails.

```python
validate_and_raise(5, lambda x: x > 0, "Value must be positive")  # No exception
validate_and_raise(-1, lambda x: x > 0, "Value must be positive")  # Raises ValidationError
```

## Usage Examples

### Example 1: User Registration Validation

```python
from mypackage.validation import validate_string, validate_email, validate_range

def validate_user_registration(user_data):
    errors = []
    
    # Validate username
    if not validate_string(user_data["username"], min_length=3, max_length=20):
        errors.append("Username must be 3-20 characters")
    
    # Validate email
    if not validate_email(user_data["email"]):
        errors.append("Invalid email address")
    
    # Validate age
    if not validate_range(user_data["age"], min_val=13, max_val=120):
        errors.append("Age must be between 13 and 120")
    
    return errors
```

### Example 2: Configuration Validation

```python
from mypackage.validation import validate_dict_structure, validate_url, validate_range

def validate_config(config):
    schema = {
        "api_url": str,
        "timeout": int,
        "retry_count": int,
        "debug": bool
    }
    
    is_valid, errors = validate_dict_structure(config, schema)
    if not is_valid:
        return False, errors
    
    # Additional validation
    if not validate_url(config["api_url"]):
        errors.append("Invalid API URL")
    
    if not validate_range(config["timeout"], min_val=1, max_val=60):
        errors.append("Timeout must be between 1 and 60 seconds")
    
    return len(errors) == 0, errors
```

### Example 3: Custom Validator for Product Data

```python
from mypackage.validation import create_validator

# Create a validator for product price
price_validator = create_validator(min_val=0.01, max_val=10000.0)

# Create a validator for product category
category_validator = create_validator(
    allowed_values=["electronics", "clothing", "books", "home", "sports"]
)

# Use the validators
price = 29.99
is_valid, error = price_validator(price)  # (True, '')

category = "electronics"
is_valid, error = category_validator(category)  # (True, '')
```

## Testing

The module includes comprehensive tests. Run them with:

```bash
python -m unittest mypackage.tests.test_validation
```

## Type Hints

All functions include complete type hints for better IDE support and static type checking.

## Error Handling

The module provides two approaches to error handling:
1. **Boolean return values**: Functions return `True`/`False` for simple validation
2. **Exception-based**: Use `ValidationError` and `validate_and_raise` for more complex scenarios
3. **Error messages**: Functions that validate complex data return detailed error messages

## Dependencies

- Python 3.6+
- Standard library only (no external dependencies)

## License

Part of the MyPackage project.