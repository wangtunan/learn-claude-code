#!/usr/bin/env python3
"""
Tests for the validation module.
"""

import unittest
import json
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import mypackage
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mypackage.validation import (
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


class TestValidationFunctions(unittest.TestCase):
    """Test cases for validation functions."""
    
    def test_validate_type(self):
        """Test type validation."""
        self.assertTrue(validate_type(42, int))
        self.assertTrue(validate_type(3.14, float))
        self.assertTrue(validate_type("hello", str))
        self.assertTrue(validate_type([1, 2, 3], list))
        self.assertTrue(validate_type({"a": 1}, dict))
        
        self.assertFalse(validate_type(42, str))
        self.assertFalse(validate_type("hello", int))
        
        # Test with multiple types
        self.assertTrue(validate_type(42, (int, float)))
        self.assertTrue(validate_type(3.14, (int, float)))
        self.assertFalse(validate_type("hello", (int, float)))
        
        # Test with None allowed
        self.assertTrue(validate_type(None, int, allow_none=True))
        self.assertFalse(validate_type(None, int, allow_none=False))
    
    def test_validate_range(self):
        """Test range validation."""
        self.assertTrue(validate_range(5, min_val=0, max_val=10))
        self.assertTrue(validate_range(0, min_val=0, max_val=10))
        self.assertTrue(validate_range(10, min_val=0, max_val=10))
        self.assertTrue(validate_range(5, min_val=0))
        self.assertTrue(validate_range(5, max_val=10))
        self.assertTrue(validate_range(5))
        
        self.assertFalse(validate_range(-1, min_val=0, max_val=10))
        self.assertFalse(validate_range(11, min_val=0, max_val=10))
        
        # Test exclusive boundaries
        self.assertTrue(validate_range(5, min_val=0, max_val=10, inclusive=False))
        self.assertFalse(validate_range(0, min_val=0, max_val=10, inclusive=False))
        self.assertFalse(validate_range(10, min_val=0, max_val=10, inclusive=False))
        
        # Test with floats
        self.assertTrue(validate_range(3.14, min_val=0.0, max_val=5.0))
        self.assertFalse(validate_range(6.28, min_val=0.0, max_val=5.0))
    
    def test_validate_string(self):
        """Test string validation."""
        self.assertTrue(validate_string("hello", min_length=3, max_length=10))
        self.assertTrue(validate_string("hi", min_length=2, max_length=2))
        self.assertFalse(validate_string("hi", min_length=3))
        self.assertFalse(validate_string("verylongstring", max_length=10))
        
        # Test with pattern
        pattern = r'^[A-Z][a-z]+$'
        self.assertTrue(validate_string("Hello", pattern=pattern))
        self.assertFalse(validate_string("hello", pattern=pattern))
        self.assertFalse(validate_string("HELLO", pattern=pattern))
        
        # Test with allowed values
        allowed = ["apple", "banana", "orange"]
        self.assertTrue(validate_string("apple", allowed_values=allowed))
        self.assertFalse(validate_string("grape", allowed_values=allowed))
        
        # Test non-string input
        self.assertFalse(validate_string(123, min_length=1))
    
    def test_validate_email(self):
        """Test email validation."""
        self.assertTrue(validate_email("test@example.com"))
        self.assertTrue(validate_email("user.name@domain.co.uk"))
        self.assertTrue(validate_email("user+tag@example.org"))
        
        self.assertFalse(validate_email("invalid-email"))
        self.assertFalse(validate_email("@example.com"))
        self.assertFalse(validate_email("user@"))
        self.assertFalse(validate_email("user@.com"))
    
    def test_validate_url(self):
        """Test URL validation."""
        self.assertTrue(validate_url("https://example.com"))
        self.assertTrue(validate_url("http://example.com"))
        self.assertTrue(validate_url("https://sub.domain.co.uk/path/to/page"))
        self.assertTrue(validate_url("example.com"))  # Protocol optional
        
        self.assertFalse(validate_url("not-a-url"))
        self.assertFalse(validate_url("http://"))
        
        # Test HTTPS requirement
        self.assertTrue(validate_url("https://example.com", require_https=True))
        self.assertFalse(validate_url("http://example.com", require_https=True))
    
    def test_validate_date_string(self):
        """Test date string validation."""
        self.assertTrue(validate_date_string("2023-12-25"))
        self.assertTrue(validate_date_string("2023-12-25", "%Y-%m-%d"))
        self.assertTrue(validate_date_string("25/12/2023", "%d/%m/%Y"))
        self.assertTrue(validate_date_string("12-25-2023", "%m-%d-%Y"))
        
        self.assertFalse(validate_date_string("invalid-date"))
        self.assertFalse(validate_date_string("2023-13-01"))  # Invalid month
        self.assertFalse(validate_date_string("2023-12-32"))  # Invalid day
    
    def test_validate_dict_structure(self):
        """Test dictionary structure validation."""
        schema = {"name": str, "age": int, "email": str}
        
        # Valid data
        valid_data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
        is_valid, errors = validate_dict_structure(valid_data, schema)
        self.assertTrue(is_valid)
        self.assertEqual(errors, [])
        
        # Missing key
        missing_key_data = {"name": "Bob", "age": 25}
        is_valid, errors = validate_dict_structure(missing_key_data, schema)
        self.assertFalse(is_valid)
        self.assertIn("Missing required key: 'email'", errors)
        
        # Wrong type
        wrong_type_data = {"name": "Charlie", "age": "thirty", "email": "charlie@example.com"}
        is_valid, errors = validate_dict_structure(wrong_type_data, schema)
        self.assertFalse(is_valid)
        self.assertIn("Key 'age' has incorrect type", errors)
        
        # Strict mode
        extra_key_data = {"name": "David", "age": 35, "email": "david@example.com", "extra": "field"}
        is_valid, errors = validate_dict_structure(extra_key_data, schema, strict=True)
        self.assertFalse(is_valid)
        self.assertIn("Unexpected key: 'extra'", errors)
        
        # Non-strict mode with extra key
        is_valid, errors = validate_dict_structure(extra_key_data, schema, strict=False)
        self.assertTrue(is_valid)
        self.assertEqual(errors, [])
    
    def test_validate_json_string(self):
        """Test JSON string validation."""
        # Valid JSON
        json_str = '{"name": "Alice", "age": 30, "active": true}'
        is_valid, result = validate_json_string(json_str)
        self.assertTrue(is_valid)
        self.assertEqual(result, {"name": "Alice", "age": 30, "active": True})
        
        # Invalid JSON
        invalid_json = '{"name": "Alice", age: 30}'
        is_valid, result = validate_json_string(invalid_json)
        self.assertFalse(is_valid)
        self.assertIn("Invalid JSON", result)
        
        # Valid JSON with schema
        schema = {"name": str, "age": int}
        is_valid, result = validate_json_string(json_str, schema)
        self.assertTrue(is_valid)
        
        # Invalid JSON with schema (wrong type)
        wrong_type_json = '{"name": "Bob", "age": "thirty"}'
        is_valid, result = validate_json_string(wrong_type_json, schema)
        self.assertFalse(is_valid)
        self.assertIn("Schema validation failed", result)
        
        # Non-object JSON with schema
        array_json = '[1, 2, 3]'
        is_valid, result = validate_json_string(array_json, schema)
        self.assertFalse(is_valid)
        self.assertIn("JSON must be an object", result)
    
    def test_validate_with_custom_rules(self):
        """Test validation with custom rules."""
        def is_positive(x):
            return x > 0, "Value must be positive"
        
        def is_even(x):
            return x % 2 == 0, "Value must be even"
        
        def is_multiple_of_three(x):
            return x % 3 == 0, "Value must be a multiple of 3"
        
        rules = [is_positive, is_even, is_multiple_of_three]
        
        # Valid value
        is_valid, errors = validate_with_custom_rules(6, rules)
        self.assertTrue(is_valid)
        self.assertEqual(errors, [])
        
        # Invalid value (fails all rules)
        is_valid, errors = validate_with_custom_rules(-1, rules)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 3)
        self.assertIn("Value must be positive", errors)
        self.assertIn("Value must be even", errors)
        self.assertIn("Value must be a multiple of 3", errors)
        
        # Invalid value (fails some rules)
        is_valid, errors = validate_with_custom_rules(5, rules)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 2)
        self.assertIn("Value must be even", errors)
        self.assertIn("Value must be a multiple of 3", errors)
    
    def test_validation_error(self):
        """Test ValidationError exception."""
        error = ValidationError("Invalid value")
        self.assertEqual(str(error), "Validation error: Invalid value")
        
        error_with_field = ValidationError("Value must be positive", field="age")
        self.assertEqual(str(error_with_field), "Validation error for field 'age': Value must be positive")
    
    def test_validate_and_raise(self):
        """Test validate_and_raise function."""
        # Valid case - should not raise
        validate_and_raise(5, lambda x: x > 0, "Value must be positive")
        
        # Invalid case - should raise
        with self.assertRaises(ValidationError) as context:
            validate_and_raise(-1, lambda x: x > 0, "Value must be positive")
        self.assertEqual(str(context.exception), "Validation error: Value must be positive")
        
        # With field name
        with self.assertRaises(ValidationError) as context:
            validate_and_raise(-1, lambda x: x > 0, "Value must be positive", field="age")
        self.assertIn("field 'age'", str(context.exception))
    
    def test_create_validator(self):
        """Test create_validator function."""
        # Numeric range validator
        range_validator = create_validator(min_val=0, max_val=100)
        is_valid, error = range_validator(50)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
        
        is_valid, error = range_validator(150)
        self.assertFalse(is_valid)
        self.assertIn("Value must be between 0 and 100", error)
        
        # String length validator
        length_validator = create_validator(min_length=3, max_length=10)
        is_valid, error = length_validator("hello")
        self.assertTrue(is_valid)
        
        is_valid, error = length_validator("hi")
        self.assertFalse(is_valid)
        self.assertIn("String length must be between 3 and 10", error)
        
        # Pattern validator
        pattern_validator = create_validator(pattern=r'^[A-Z][a-z]+$')
        is_valid, error = pattern_validator("Hello")
        self.assertTrue(is_valid)
        
        is_valid, error = pattern_validator("hello")
        self.assertFalse(is_valid)
        self.assertIn("String must match pattern", error)
        
        # Allowed values validator
        allowed_validator = create_validator(allowed_values=["red", "green", "blue"])
        is_valid, error = allowed_validator("red")
        self.assertTrue(is_valid)
        
        is_valid, error = allowed_validator("yellow")
        self.assertFalse(is_valid)
        self.assertIn("Value must be one of:", error)
        
        # Combined validator
        combined_validator = create_validator(
            min_val=18,
            max_val=120,
            allowed_values=[18, 21, 30, 40, 50, 60, 70, 80, 90, 100]
        )
        is_valid, error = combined_validator(21)
        self.assertTrue(is_valid)
        
        is_valid, error = combined_validator(25)
        self.assertFalse(is_valid)
        self.assertIn("Value must be one of:", error)


if __name__ == "__main__":
    unittest.main()