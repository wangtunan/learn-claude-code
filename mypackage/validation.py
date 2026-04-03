#!/usr/bin/env python3
"""
Data validation utilities for MyPackage.

This module provides comprehensive data validation functions for common data types,
input validation, and schema validation. It includes type checking, range validation,
and custom validation rules.
"""

from typing import Any, Union, List, Dict, Optional, Callable, Type, TypeVar, Tuple
from datetime import datetime, date
import re
import json

T = TypeVar('T')


def validate_type(value: Any, expected_type: Union[Type, Tuple[Type, ...]], 
                 allow_none: bool = False) -> bool:
    """
    Validate that a value is of the expected type.
    
    Args:
        value: The value to validate
        expected_type: The expected type or tuple of types
        allow_none: Whether None is an acceptable value
        
    Returns:
        True if the value is of the expected type, False otherwise
        
    Examples:
        >>> validate_type(42, int)
        True
        >>> validate_type("hello", (int, str))
        True
        >>> validate_type(None, int, allow_none=True)
        True
        >>> validate_type(3.14, int)
        False
    """
    if allow_none and value is None:
        return True
    
    return isinstance(value, expected_type)


def validate_range(value: Union[int, float], min_val: Optional[Union[int, float]] = None,
                  max_val: Optional[Union[int, float]] = None, inclusive: bool = True) -> bool:
    """
    Validate that a numeric value is within a specified range.
    
    Args:
        value: The numeric value to validate
        min_val: Minimum allowed value (inclusive if inclusive=True)
        max_val: Maximum allowed value (inclusive if inclusive=True)
        inclusive: Whether the range boundaries are inclusive
        
    Returns:
        True if the value is within the specified range, False otherwise
        
    Examples:
        >>> validate_range(5, min_val=0, max_val=10)
        True
        >>> validate_range(10, min_val=0, max_val=10)
        True
        >>> validate_range(10, min_val=0, max_val=10, inclusive=False)
        False
        >>> validate_range(15, max_val=10)
        False
    """
    if min_val is not None:
        if inclusive:
            if value < min_val:
                return False
        else:
            if value <= min_val:
                return False
    
    if max_val is not None:
        if inclusive:
            if value > max_val:
                return False
        else:
            if value >= max_val:
                return False
    
    return True


def validate_string(value: str, min_length: Optional[int] = None,
                   max_length: Optional[int] = None, pattern: Optional[str] = None,
                   allowed_values: Optional[List[str]] = None) -> bool:
    """
    Validate a string against various constraints.
    
    Args:
        value: The string to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        pattern: Regular expression pattern to match
        allowed_values: List of allowed string values
        
    Returns:
        True if the string meets all constraints, False otherwise
        
    Examples:
        >>> validate_string("hello", min_length=3, max_length=10)
        True
        >>> validate_string("hi", min_length=3)
        False
        >>> validate_string("test@example.com", pattern=r'^[^@]+@[^@]+\.[^@]+$')
        True
        >>> validate_string("apple", allowed_values=["apple", "banana", "orange"])
        True
    """
    if not isinstance(value, str):
        return False
    
    if min_length is not None and len(value) < min_length:
        return False
    
    if max_length is not None and len(value) > max_length:
        return False
    
    if pattern is not None:
        if not re.match(pattern, value):
            return False
    
    if allowed_values is not None:
        if value not in allowed_values:
            return False
    
    return True


def validate_email(email: str) -> bool:
    """
    Validate an email address format.
    
    Args:
        email: The email address to validate
        
    Returns:
        True if the email address is valid, False otherwise
        
    Examples:
        >>> validate_email("test@example.com")
        True
        >>> validate_email("invalid-email")
        False
        >>> validate_email("user@domain.co.uk")
        True
    """
    # Basic email validation pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str, require_https: bool = False) -> bool:
    """
    Validate a URL format.
    
    Args:
        url: The URL to validate
        require_https: Whether to require HTTPS protocol
        
    Returns:
        True if the URL is valid, False otherwise
        
    Examples:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("http://example.com")
        True
        >>> validate_url("https://example.com", require_https=True)
        True
        >>> validate_url("http://example.com", require_https=True)
        False
        >>> validate_url("not-a-url")
        False
    """
    # URL validation pattern
    pattern = r'^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(:[0-9]+)?(/[^\s]*)?$'
    
    if not re.match(pattern, url):
        return False
    
    if require_https and not url.startswith('https://'):
        return False
    
    return True


def validate_date_string(date_str: str, format: str = "%Y-%m-%d") -> bool:
    """
    Validate a date string against a specified format.
    
    Args:
        date_str: The date string to validate
        format: The expected date format (default: YYYY-MM-DD)
        
    Returns:
        True if the date string is valid, False otherwise
        
    Examples:
        >>> validate_date_string("2023-12-25")
        True
        >>> validate_date_string("2023-12-25", "%Y-%m-%d")
        True
        >>> validate_date_string("25/12/2023", "%d/%m/%Y")
        True
        >>> validate_date_string("invalid-date")
        False
    """
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def validate_dict_structure(data: Dict[str, Any], 
                           schema: Dict[str, Union[Type, Tuple[Type, ...]]],
                           strict: bool = False) -> Tuple[bool, List[str]]:
    """
    Validate a dictionary against a schema definition.
    
    Args:
        data: The dictionary to validate
        schema: Schema definition mapping keys to expected types
        strict: If True, data cannot contain keys not in schema
        
    Returns:
        Tuple of (is_valid, list_of_errors)
        
    Examples:
        >>> schema = {"name": str, "age": int, "email": str}
        >>> data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
        >>> validate_dict_structure(data, schema)
        (True, [])
        >>> data2 = {"name": "Bob", "age": "thirty"}
        >>> validate_dict_structure(data2, schema)
        (False, ["Key 'age' has incorrect type. Expected <class 'int'>, got <class 'str'>"])
    """
    errors = []
    
    # Check for missing required keys
    for key, expected_type in schema.items():
        if key not in data:
            errors.append(f"Missing required key: '{key}'")
        elif not isinstance(data[key], expected_type):
            errors.append(f"Key '{key}' has incorrect type. Expected {expected_type}, got {type(data[key])}")
    
    # Check for extra keys if strict mode
    if strict:
        for key in data.keys():
            if key not in schema:
                errors.append(f"Unexpected key: '{key}'")
    
    return len(errors) == 0, errors


def validate_json_string(json_str: str, schema: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate a JSON string and optionally validate against a schema.
    
    Args:
        json_str: The JSON string to validate
        schema: Optional schema to validate the parsed JSON against
        
    Returns:
        Tuple of (is_valid, error_message_or_parsed_data)
        
    Examples:
        >>> json_str = '{"name": "Alice", "age": 30}'
        >>> validate_json_string(json_str)
        (True, {'name': 'Alice', 'age': 30})
        >>> validate_json_string('invalid json')
        (False, 'Invalid JSON: Expecting value: line 1 column 1 (char 0)')
        >>> schema = {"name": str, "age": int}
        >>> validate_json_string(json_str, schema)
        (True, {'name': 'Alice', 'age': 30})
    """
    try:
        parsed_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"
    
    if schema is not None:
        if not isinstance(parsed_data, dict):
            return False, "JSON must be an object for schema validation"
        
        is_valid, errors = validate_dict_structure(parsed_data, schema)
        if not is_valid:
            return False, f"Schema validation failed: {', '.join(errors)}"
    
    return True, parsed_data


def validate_with_custom_rules(value: Any, rules: List[Callable[[Any], Tuple[bool, str]]]) -> Tuple[bool, List[str]]:
    """
    Validate a value against a list of custom validation rules.
    
    Args:
        value: The value to validate
        rules: List of validation functions that return (is_valid, error_message)
        
    Returns:
        Tuple of (is_valid, list_of_error_messages)
        
    Examples:
        >>> def is_positive(x):
        ...     return x > 0, "Value must be positive"
        >>> def is_even(x):
        ...     return x % 2 == 0, "Value must be even"
        >>> rules = [is_positive, is_even]
        >>> validate_with_custom_rules(4, rules)
        (True, [])
        >>> validate_with_custom_rules(-2, rules)
        (False, ['Value must be positive', 'Value must be even'])
    """
    errors = []
    
    for rule in rules:
        is_valid, error_message = rule(value)
        if not is_valid:
            errors.append(error_message)
    
    return len(errors) == 0, errors


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.field:
            return f"Validation error for field '{self.field}': {self.message}"
        return f"Validation error: {self.message}"


def validate_and_raise(value: Any, validator: Callable[[Any], bool], 
                      error_message: str, field: Optional[str] = None) -> None:
    """
    Validate a value and raise ValidationError if validation fails.
    
    Args:
        value: The value to validate
        validator: Validation function that returns True/False
        error_message: Error message to use if validation fails
        field: Optional field name for the error
        
    Raises:
        ValidationError: If validation fails
        
    Examples:
        >>> validate_and_raise(5, lambda x: x > 0, "Value must be positive")
        >>> validate_and_raise(-1, lambda x: x > 0, "Value must be positive")
        Traceback (most recent call last):
            ...
        ValidationError: Validation error: Value must be positive
    """
    if not validator(value):
        raise ValidationError(error_message, field)


# Convenience function for common validation patterns
def create_validator(min_val: Optional[Union[int, float]] = None,
                    max_val: Optional[Union[int, float]] = None,
                    min_length: Optional[int] = None,
                    max_length: Optional[int] = None,
                    pattern: Optional[str] = None,
                    allowed_values: Optional[List[Any]] = None) -> Callable[[Any], Tuple[bool, str]]:
    """
    Create a validator function with multiple constraints.
    
    Args:
        min_val: Minimum numeric value
        max_val: Maximum numeric value
        min_length: Minimum string length
        max_length: Maximum string length
        pattern: Regular expression pattern for strings
        allowed_values: List of allowed values
        
    Returns:
        A validator function that returns (is_valid, error_message)
        
    Examples:
        >>> validator = create_validator(min_val=0, max_val=100)
        >>> validator(50)
        (True, '')
        >>> validator(150)
        (False, 'Value must be between 0 and 100')
    """
    def validator(value: Any) -> Tuple[bool, str]:
        if min_val is not None or max_val is not None:
            if isinstance(value, (int, float)):
                if not validate_range(value, min_val, max_val):
                    min_str = str(min_val) if min_val is not None else "negative infinity"
                    max_str = str(max_val) if max_val is not None else "infinity"
                    return False, f"Value must be between {min_str} and {max_str}"
            else:
                return False, "Value must be numeric for range validation"
        
        if min_length is not None or max_length is not None:
            if isinstance(value, str):
                if not validate_string(value, min_length, max_length):
                    min_len_str = str(min_length) if min_length is not None else "0"
                    max_len_str = str(max_length) if max_length is not None else "infinity"
                    return False, f"String length must be between {min_len_str} and {max_len_str}"
            else:
                return False, "Value must be a string for length validation"
        
        if pattern is not None:
            if isinstance(value, str):
                if not validate_string(value, pattern=pattern):
                    return False, f"String must match pattern: {pattern}"
            else:
                return False, "Value must be a string for pattern validation"
        
        if allowed_values is not None:
            if value not in allowed_values:
                return False, f"Value must be one of: {allowed_values}"
        
        return True, ""
    
    return validator