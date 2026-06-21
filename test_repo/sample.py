import fire

class Calculator:
    """A simple class to perform basic arithmetic operations."""

    def add(self, num1: float, num2: float) -> float:
        """Return the sum of two numbers."""
        return num1 + num2

    def subtract(self, num1: float, num2: float) -> float:
        """Return the difference between two numbers."""
        return num1 - num2


# Example usage:
if __name__ == "__main__":
    # Instantiate the class
    calc = Calculator()