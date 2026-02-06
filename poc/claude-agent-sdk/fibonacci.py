"""
Fibonacci sequence implementation with memoization.

This module provides an efficient implementation of the Fibonacci sequence
using memoization to avoid redundant calculations.
"""

from functools import lru_cache
from typing import Dict


def fibonacci_manual_memo(n: int, memo: Dict[int, int] = None) -> int:
    """
    Calculate the nth Fibonacci number using manual memoization.

    This implementation uses a dictionary to cache previously calculated
    Fibonacci numbers, avoiding redundant recursive calls.

    Args:
        n: The position in the Fibonacci sequence (0-indexed).
        memo: Optional dictionary for memoization (used internally).

    Returns:
        The nth Fibonacci number.

    Raises:
        ValueError: If n is negative.

    Examples:
        >>> fibonacci_manual_memo(0)
        0
        >>> fibonacci_manual_memo(1)
        1
        >>> fibonacci_manual_memo(10)
        55
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")

    if memo is None:
        memo = {}

    # Base cases
    if n in (0, 1):
        return n

    # Check if already computed
    if n in memo:
        return memo[n]

    # Compute and store in memo
    memo[n] = fibonacci_manual_memo(n - 1, memo) + fibonacci_manual_memo(n - 2, memo)
    return memo[n]


@lru_cache(maxsize=None)
def fibonacci_lru(n: int) -> int:
    """
    Calculate the nth Fibonacci number using functools.lru_cache.

    This implementation uses Python's built-in LRU cache decorator for
    automatic memoization. This is the most Pythonic approach.

    Args:
        n: The position in the Fibonacci sequence (0-indexed).

    Returns:
        The nth Fibonacci number.

    Raises:
        ValueError: If n is negative.

    Examples:
        >>> fibonacci_lru(0)
        0
        >>> fibonacci_lru(1)
        1
        >>> fibonacci_lru(10)
        55
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")

    # Base cases
    if n in (0, 1):
        return n

    # Recursive case with automatic memoization
    return fibonacci_lru(n - 1) + fibonacci_lru(n - 2)


def fibonacci_iterative(n: int) -> int:
    """
    Calculate the nth Fibonacci number using an iterative approach.

    This implementation uses constant space O(1) and linear time O(n).
    It's the most efficient for single calculations without caching.

    Args:
        n: The position in the Fibonacci sequence (0-indexed).

    Returns:
        The nth Fibonacci number.

    Raises:
        ValueError: If n is negative.

    Examples:
        >>> fibonacci_iterative(0)
        0
        >>> fibonacci_iterative(1)
        1
        >>> fibonacci_iterative(10)
        55
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")

    if n in (0, 1):
        return n

    # Initialize first two Fibonacci numbers
    prev, curr = 0, 1

    # Calculate iteratively
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr

    return curr


# Alias the recommended implementation
fibonacci = fibonacci_lru


if __name__ == "__main__":
    # Demonstration of the different implementations
    print("Fibonacci Sequence Demonstration\n")

    # Test values
    test_values = [0, 1, 5, 10, 15, 20]

    print("Using LRU Cache (Recommended):")
    for n in test_values:
        print(f"  fibonacci_lru({n}) = {fibonacci_lru(n)}")

    print("\nUsing Manual Memoization:")
    for n in test_values:
        print(f"  fibonacci_manual_memo({n}) = {fibonacci_manual_memo(n)}")

    print("\nUsing Iterative Approach:")
    for n in test_values:
        print(f"  fibonacci_iterative({n}) = {fibonacci_iterative(n)}")

    # Performance comparison for larger values
    print("\n\nLarge value test (n=100):")
    print(f"  Result: {fibonacci(100)}")

    # Show cache info for LRU implementation
    print("\nCache statistics for fibonacci_lru:")
    print(f"  {fibonacci_lru.cache_info()}")
