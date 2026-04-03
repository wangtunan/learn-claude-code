#!/usr/bin/env python3
"""
Unit tests for the utils module.
"""

import pytest
from mypackage.utils import (
    add_numbers,
    multiply_numbers,
    greet,
    calculate_average,
    is_palindrome,
    fibonacci,
    factorial,
)


class TestAddNumbers:
    """Test cases for add_numbers function."""

    def test_add_integers(self):
        """Test adding two integers."""
        assert add_numbers(2, 3) == 5
        assert add_numbers(-2, 3) == 1
        assert add_numbers(0, 0) == 0

    def test_add_floats(self):
        """Test adding two floats."""
        assert add_numbers(2.5, 3.5) == 6.0
        assert add_numbers(-2.5, 3.5) == 1.0

    def test_add_mixed(self):
        """Test adding integer and float."""
        assert add_numbers(2, 3.5) == 5.5
        assert add_numbers(2.5, 3) == 5.5


class TestMultiplyNumbers:
    """Test cases for multiply_numbers function."""

    def test_multiply_integers(self):
        """Test multiplying two integers."""
        assert multiply_numbers(2, 3) == 6
        assert multiply_numbers(-2, 3) == -6
        assert multiply_numbers(0, 5) == 0

    def test_multiply_floats(self):
        """Test multiplying two floats."""
        assert multiply_numbers(2.5, 4.0) == 10.0
        assert multiply_numbers(-2.5, 4.0) == -10.0

    def test_multiply_mixed(self):
        """Test multiplying integer and float."""
        assert multiply_numbers(2, 3.5) == 7.0
        assert multiply_numbers(2.5, 4) == 10.0


class TestGreet:
    """Test cases for greet function."""

    def test_greet_with_name(self):
        """Test greeting with a specific name."""
        assert greet("Alice") == "Hello, Alice!"
        assert greet("Bob") == "Hello, Bob!"

    def test_greet_default(self):
        """Test greeting with default name."""
        assert greet() == "Hello, World!"
        assert greet("World") == "Hello, World!"


class TestCalculateAverage:
    """Test cases for calculate_average function."""

    def test_average_integers(self):
        """Test average of integers."""
        assert calculate_average([1, 2, 3, 4, 5]) == 3.0
        assert calculate_average([10, 20, 30]) == 20.0

    def test_average_floats(self):
        """Test average of floats."""
        assert calculate_average([1.5, 2.5, 3.5]) == 2.5
        assert calculate_average([0.1, 0.2, 0.3]) == pytest.approx(0.2)

    def test_average_single_number(self):
        """Test average of single number."""
        assert calculate_average([5]) == 5.0
        assert calculate_average([3.14]) == 3.14

    def test_average_empty_list(self):
        """Test that empty list raises ValueError."""
        with pytest.raises(ValueError, match="Cannot calculate average of empty list"):
            calculate_average([])


class TestIsPalindrome:
    """Test cases for is_palindrome function."""

    def test_palindrome_case_insensitive(self):
        """Test palindrome check (case insensitive by default)."""
        assert is_palindrome("racecar")
        assert is_palindrome("Racecar")
        assert is_palindrome("A man a plan a canal Panama")
        assert not is_palindrome("hello")

    def test_palindrome_case_sensitive(self):
        """Test palindrome check with case sensitivity."""
        assert is_palindrome("racecar", case_sensitive=True)
        assert not is_palindrome("Racecar", case_sensitive=True)

    def test_palindrome_with_special_chars(self):
        """Test palindrome check with special characters."""
        assert is_palindrome("A man, a plan, a canal: Panama")
        assert is_palindrome("Was it a car or a cat I saw?")


class TestFibonacci:
    """Test cases for fibonacci function."""

    def test_fibonacci_sequence(self):
        """Test Fibonacci sequence generation."""
        assert fibonacci(1) == [0]
        assert fibonacci(2) == [0, 1]
        assert fibonacci(5) == [0, 1, 1, 2, 3]
        assert fibonacci(8) == [0, 1, 1, 2, 3, 5, 8, 13]

    def test_fibonacci_invalid_input(self):
        """Test Fibonacci with invalid input."""
        with pytest.raises(ValueError, match="n must be at least 1"):
            fibonacci(0)
        with pytest.raises(ValueError, match="n must be at least 1"):
            fibonacci(-5)


class TestFactorial:
    """Test cases for factorial function."""

    def test_factorial_positive(self):
        """Test factorial of positive numbers."""
        assert factorial(0) == 1
        assert factorial(1) == 1
        assert factorial(5) == 120
        assert factorial(7) == 5040

    def test_factorial_negative(self):
        """Test factorial of negative number raises error."""
        with pytest.raises(ValueError, match="Factorial is not defined for negative numbers"):
            factorial(-1)
        with pytest.raises(ValueError, match="Factorial is not defined for negative numbers"):
            factorial(-5)


def test_import_from_package():
    """Test that functions can be imported from the package directly."""
    from mypackage import add_numbers, greet
    assert add_numbers(2, 3) == 5
    assert greet("Test") == "Hello, Test!"


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])