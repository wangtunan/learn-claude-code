#!/usr/bin/env python3
"""
Utility functions for MyPackage.

This module contains various utility functions for mathematical operations,
string manipulation, and other common tasks.
"""

from typing import List, Union


def add_numbers(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b

    Examples:
        >>> add_numbers(2, 3)
        5
        >>> add_numbers(2.5, 3.5)
        6.0
    """
    return a + b


def multiply_numbers(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Multiply two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Product of a and b

    Examples:
        >>> multiply_numbers(2, 3)
        6
        >>> multiply_numbers(2.5, 4)
        10.0
    """
    return a * b


def greet(name: str = "World") -> str:
    """
    Generate a greeting message.

    Args:
        name: Name to greet. Defaults to "World".

    Returns:
        Greeting message

    Examples:
        >>> greet("Alice")
        'Hello, Alice!'
        >>> greet()
        'Hello, World!'
    """
    return f"Hello, {name}!"


def calculate_average(numbers: List[Union[int, float]]) -> float:
    """
    Calculate the average of a list of numbers.

    Args:
        numbers: List of numbers

    Returns:
        Average of the numbers

    Raises:
        ValueError: If the list is empty

    Examples:
        >>> calculate_average([1, 2, 3, 4, 5])
        3.0
        >>> calculate_average([1.5, 2.5, 3.5])
        2.5
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")

    return sum(numbers) / len(numbers)


def is_palindrome(text: str, case_sensitive: bool = False) -> bool:
    """
    Check if a string is a palindrome.

    Args:
        text: String to check
        case_sensitive: Whether to consider case. Defaults to False.

    Returns:
        True if the string is a palindrome, False otherwise

    Examples:
        >>> is_palindrome("racecar")
        True
        >>> is_palindrome("Racecar")
        True
        >>> is_palindrome("Racecar", case_sensitive=True)
        False
        >>> is_palindrome("hello")
        False
    """
    if not case_sensitive:
        text = text.lower()

    # Remove non-alphanumeric characters for a more robust check
    cleaned_text = "".join(c for c in text if c.isalnum())
    return cleaned_text == cleaned_text[::-1]


def fibonacci(n: int) -> List[int]:
    """
    Generate Fibonacci sequence up to n terms.

    Args:
        n: Number of terms to generate

    Returns:
        List of Fibonacci numbers

    Raises:
        ValueError: If n is less than 1

    Examples:
        >>> fibonacci(5)
        [0, 1, 1, 2, 3]
        >>> fibonacci(1)
        [0]
    """
    if n < 1:
        raise ValueError("n must be at least 1")

    if n == 1:
        return [0]

    sequence = [0, 1]
    for i in range(2, n):
        sequence.append(sequence[i-1] + sequence[i-2])

    return sequence


def factorial(n: int) -> int:
    """
    Calculate factorial of a number.

    Args:
        n: Non-negative integer

    Returns:
        Factorial of n

    Raises:
        ValueError: If n is negative

    Examples:
        >>> factorial(5)
        120
        >>> factorial(0)
        1
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")

    result = 1
    for i in range(1, n + 1):
        result *= i
    return result