#!/usr/bin/env python3
"""A simple hello world program with type hints and documentation."""


def greet(name: str = "World") -> str:
    """
    Generate a greeting message.

    Args:
        name: The name to greet. Defaults to "World".

    Returns:
        A greeting string in the format "Hello, {name}!".
    """
    return f"Hello, {name}!"


def main() -> None:
    """Main function that runs the greeting program."""
    greeting = greet()
    print(greeting)


if __name__ == "__main__":
    main()