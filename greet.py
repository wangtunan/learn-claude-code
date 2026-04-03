#!/usr/bin/env python3
"""A greeting module with docstring examples."""


def greet(name: str) -> str:
    """
    Greet a person by name.

    Args:
        name: The name of the person to greet.

    Returns:
        A greeting message.

    Examples:
        >>> greet("Alice")
        'Hello, Alice!'
    """
    return f"Hello, {name}!"


def main() -> None:
    """Demonstrate the greet function."""
    print(greet("World"))


if __name__ == "__main__":
    main()