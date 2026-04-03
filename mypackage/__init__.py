"""
MyPackage - A collection of utility functions.

This package provides various utility functions for common tasks.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import key functions to make them available at package level
from .utils import (
    add_numbers,
    multiply_numbers,
    greet,
    calculate_average,
    is_palindrome
)

from .validation import (
    validate_type,
    validate_range,
    validate_string,
    validate_email,
    validate_url,
    validate_date_string,
    validate_dict_structure,
    validate_json_string,
    validate_with_custom_rules,
    ValidationError,
    validate_and_raise,
    create_validator
)

__all__ = [
    "add_numbers",
    "multiply_numbers",
    "greet",
    "calculate_average",
    "is_palindrome",
    "validate_type",
    "validate_range",
    "validate_string",
    "validate_email",
    "validate_url",
    "validate_date_string",
    "validate_dict_structure",
    "validate_json_string",
    "validate_with_custom_rules",
    "ValidationError",
    "validate_and_raise",
    "create_validator",
]