#!/usr/bin/env python3
"""
Example usage of the validation module.
"""

import sys
import os

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


def demonstrate_basic_validation():
    """Demonstrate basic validation functions."""
    print("=== Basic Validation Examples ===")
    
    # Type validation
    print("\n1. Type Validation:")
    print(f"   validate_type(42, int): {validate_type(42, int)}")
    print(f"   validate_type('hello', int): {validate_type('hello', int)}")
    print(f"   validate_type(3.14, (int, float)): {validate_type(3.14, (int, float))}")
    
    # Range validation
    print("\n2. Range Validation:")
    print(f"   validate_range(5, min_val=0, max_val=10): {validate_range(5, min_val=0, max_val=10)}")
    print(f"   validate_range(15, min_val=0, max_val=10): {validate_range(15, min_val=0, max_val=10)}")
    
    # String validation
    print("\n3. String Validation:")
    print(f"   validate_string('hello', min_length=3, max_length=10): "
          f"{validate_string('hello', min_length=3, max_length=10)}")
    print(f"   validate_string('hi', min_length=3): {validate_string('hi', min_length=3)}")
    
    # Email validation
    print("\n4. Email Validation:")
    print(f"   validate_email('test@example.com'): {validate_email('test@example.com')}")
    print(f"   validate_email('invalid-email'): {validate_email('invalid-email')}")
    
    # URL validation
    print("\n5. URL Validation:")
    print(f"   validate_url('https://example.com'): {validate_url('https://example.com')}")
    print(f"   validate_url('not-a-url'): {validate_url('not-a-url')}")
    
    # Date validation
    print("\n6. Date Validation:")
    print(f"   validate_date_string('2023-12-25'): {validate_date_string('2023-12-25')}")
    print(f"   validate_date_string('invalid-date'): {validate_date_string('invalid-date')}")


def demonstrate_advanced_validation():
    """Demonstrate advanced validation functions."""
    print("\n=== Advanced Validation Examples ===")
    
    # Dictionary structure validation
    print("\n1. Dictionary Structure Validation:")
    schema = {"name": str, "age": int, "email": str}
    valid_data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
    invalid_data = {"name": "Bob", "age": "thirty", "email": "bob@example.com"}
    
    is_valid, errors = validate_dict_structure(valid_data, schema)
    print(f"   Valid data: {is_valid}, errors: {errors}")
    
    is_valid, errors = validate_dict_structure(invalid_data, schema)
    print(f"   Invalid data: {is_valid}, errors: {errors}")
    
    # JSON validation
    print("\n2. JSON Validation:")
    valid_json = '{"name": "Charlie", "age": 25, "active": true}'
    invalid_json = '{"name": "Charlie", age: 25}'
    
    is_valid, result = validate_json_string(valid_json)
    print(f"   Valid JSON: {is_valid}, parsed: {result}")
    
    is_valid, result = validate_json_string(invalid_json)
    print(f"   Invalid JSON: {is_valid}, error: {result}")
    
    # Custom rules validation
    print("\n3. Custom Rules Validation:")
    def is_positive(x):
        return x > 0, "Value must be positive"
    
    def is_even(x):
        return x % 2 == 0, "Value must be even"
    
    rules = [is_positive, is_even]
    
    is_valid, errors = validate_with_custom_rules(4, rules)
    print(f"   Value 4: {is_valid}, errors: {errors}")
    
    is_valid, errors = validate_with_custom_rules(3, rules)
    print(f"   Value 3: {is_valid}, errors: {errors}")
    
    # Validator creation
    print("\n4. Validator Creation:")
    age_validator = create_validator(min_val=0, max_val=150)
    
    is_valid, error = age_validator(30)
    print(f"   Age 30: {is_valid}, error: '{error}'")
    
    is_valid, error = age_validator(200)
    print(f"   Age 200: {is_valid}, error: '{error}'")
    
    # Exception-based validation
    print("\n5. Exception-based Validation:")
    try:
        validate_and_raise(5, lambda x: x > 0, "Value must be positive")
        print("   Value 5 is valid (no exception raised)")
    except ValidationError as e:
        print(f"   Error: {e}")
    
    try:
        validate_and_raise(-1, lambda x: x > 0, "Value must be positive", field="age")
        print("   Value -1 is valid (no exception raised)")
    except ValidationError as e:
        print(f"   Error: {e}")


def validate_user_data():
    """Example: Validate user registration data."""
    print("\n=== User Registration Validation Example ===")
    
    user_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "age": 25,
        "password": "secure123",
        "website": "https://johnsblog.com"
    }
    
    errors = []
    
    # Validate username
    if not validate_string(user_data["username"], min_length=3, max_length=20, 
                          pattern=r'^[a-zA-Z0-9_]+$'):
        errors.append("Username must be 3-20 characters, alphanumeric with underscores only")
    
    # Validate email
    if not validate_email(user_data["email"]):
        errors.append("Invalid email address")
    
    # Validate age
    if not validate_range(user_data["age"], min_val=13, max_val=120):
        errors.append("Age must be between 13 and 120")
    
    # Validate password
    if not validate_string(user_data["password"], min_length=8):
        errors.append("Password must be at least 8 characters")
    
    # Validate website (optional)
    if user_data["website"] and not validate_url(user_data["website"]):
        errors.append("Invalid website URL")
    
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("All user data is valid!")


def main():
    """Main function to run all examples."""
    print("Data Validation Module Examples")
    print("=" * 50)
    
    demonstrate_basic_validation()
    demonstrate_advanced_validation()
    validate_user_data()
    
    print("\n" + "=" * 50)
    print("All examples completed successfully!")


if __name__ == "__main__":
    main()