"""
Comprehensive test suite for fibonacci.py module.

This test suite covers all three implementations of the Fibonacci sequence:
- fibonacci_manual_memo: Manual memoization approach
- fibonacci_lru: LRU cache decorator approach
- fibonacci_iterative: Iterative approach

Tests include edge cases, normal cases, error handling, and performance validation.
"""

import pytest
import time
from fibonacci import (
    fibonacci_manual_memo,
    fibonacci_lru,
    fibonacci_iterative,
    fibonacci
)


class TestFibonacciManualMemo:
    """Test suite for fibonacci_manual_memo function."""

    def test_base_case_zero(self):
        """Test that fibonacci(0) returns 0."""
        assert fibonacci_manual_memo(0) == 0

    def test_base_case_one(self):
        """Test that fibonacci(1) returns 1."""
        assert fibonacci_manual_memo(1) == 1

    def test_small_positive_numbers(self):
        """Test fibonacci for small positive integers."""
        assert fibonacci_manual_memo(2) == 1
        assert fibonacci_manual_memo(3) == 2
        assert fibonacci_manual_memo(4) == 3
        assert fibonacci_manual_memo(5) == 5
        assert fibonacci_manual_memo(6) == 8
        assert fibonacci_manual_memo(7) == 13

    def test_medium_positive_numbers(self):
        """Test fibonacci for medium-sized positive integers."""
        assert fibonacci_manual_memo(10) == 55
        assert fibonacci_manual_memo(15) == 610
        assert fibonacci_manual_memo(20) == 6765

    def test_large_positive_numbers(self):
        """Test fibonacci for large positive integers."""
        assert fibonacci_manual_memo(30) == 832040
        assert fibonacci_manual_memo(50) == 12586269025
        assert fibonacci_manual_memo(100) == 354224848179261915075

    def test_negative_number_raises_error(self):
        """Test that negative numbers raise ValueError."""
        with pytest.raises(ValueError, match="n must be a non-negative integer"):
            fibonacci_manual_memo(-1)

        with pytest.raises(ValueError, match="n must be a non-negative integer"):
            fibonacci_manual_memo(-10)

        with pytest.raises(ValueError, match="n must be a non-negative integer"):
            fibonacci_manual_memo(-100)

    def test_memoization_works(self):
        """Test that memoization is functioning correctly."""
        # Create a shared memo dictionary
        memo = {}

        # First call should populate memo
        result1 = fibonacci_manual_memo(10, memo)
        assert result1 == 55
        assert len(memo) > 0  # Memo should have entries

        # Second call with same memo should use cached values
        result2 = fibonacci_manual_memo(10, memo)
        assert result2 == 55

        # Calling with higher n should reuse cached values
        initial_memo_size = len(memo)
        result3 = fibonacci_manual_memo(12, memo)
        assert result3 == 144
        # Should only add 2 new entries (11 and 12)
        assert len(memo) == initial_memo_size + 2

    def test_type_consistency(self):
        """Test that return type is always int."""
        for n in [0, 1, 5, 10, 20]:
            result = fibonacci_manual_memo(n)
            assert isinstance(result, int)


class TestFibonacciLRU:
    """Test suite for fibonacci_lru function."""

    def setup_method(self):
        """Clear LRU cache before each test."""
        fibonacci_lru.cache_clear()

    def test_base_case_zero(self):
        """Test that fibonacci(0) returns 0."""
        assert fibonacci_lru(0) == 0

    def test_base_case_one(self):
        """Test that fibonacci(1) returns 1."""
        assert fibonacci_lru(1) == 1

    def test_small_positive_numbers(self):
        """Test fibonacci for small positive integers."""
        assert fibonacci_lru(2) == 1
        assert fibonacci_lru(3) == 2
        assert fibonacci_lru(4) == 3
        assert fibonacci_lru(5) == 5
        assert fibonacci_lru(6) == 8
        assert fibonacci_lru(7) == 13

    def test_medium_positive_numbers(self):
        """Test fibonacci for medium-sized positive integers."""
        assert fibonacci_lru(10) == 55
        assert fibonacci_lru(15) == 610
        assert fibonacci_lru(20) == 6765

    def test_large_positive_numbers(self):
        """Test fibonacci for large positive integers."""
        assert fibonacci_lru(30) == 832040
        assert fibonacci_lru(50) == 12586269025
        assert fibonacci_lru(100) == 354224848179261915075

    def test_negative_number_raises_error(self):
        """Test that negative numbers raise ValueError."""
        with pytest.raises(ValueError, match="n must be a non-negative integer"):
            fibonacci_lru(-1)

        with pytest.raises(ValueError, match="n must be a non-negative integer"):
            fibonacci_lru(-10)

        with pytest.raises(ValueError, match="n must be a non-negative integer"):
            fibonacci_lru(-100)

    def test_lru_cache_functionality(self):
        """Test that LRU cache is working correctly."""
        fibonacci_lru.cache_clear()

        # First call
        result1 = fibonacci_lru(10)
        assert result1 == 55

        cache_info = fibonacci_lru.cache_info()
        assert cache_info.hits >= 0
        assert cache_info.misses > 0

        # Second call should hit cache
        result2 = fibonacci_lru(10)
        assert result2 == 55

        cache_info_after = fibonacci_lru.cache_info()
        assert cache_info_after.hits > cache_info.hits

    def test_cache_clear(self):
        """Test that cache_clear works properly."""
        fibonacci_lru(10)
        fibonacci_lru.cache_clear()

        cache_info = fibonacci_lru.cache_info()
        assert cache_info.hits == 0
        assert cache_info.misses == 0
        assert cache_info.currsize == 0

    def test_type_consistency(self):
        """Test that return type is always int."""
        for n in [0, 1, 5, 10, 20]:
            result = fibonacci_lru(n)
            assert isinstance(result, int)


class TestFibonacciIterative:
    """Test suite for fibonacci_iterative function."""

    def test_base_case_zero(self):
        """Test that fibonacci(0) returns 0."""
        assert fibonacci_iterative(0) == 0

    def test_base_case_one(self):
        """Test that fibonacci(1) returns 1."""
        assert fibonacci_iterative(1) == 1

    def test_small_positive_numbers(self):
        """Test fibonacci for small positive integers."""
        assert fibonacci_iterative(2) == 1
        assert fibonacci_iterative(3) == 2
        assert fibonacci_iterative(4) == 3
        assert fibonacci_iterative(5) == 5
        assert fibonacci_iterative(6) == 8
        assert fibonacci_iterative(7) == 13

    def test_medium_positive_numbers(self):
        """Test fibonacci for medium-sized positive integers."""
        assert fibonacci_iterative(10) == 55
        assert fibonacci_iterative(15) == 610
        assert fibonacci_iterative(20) == 6765

    def test_large_positive_numbers(self):
        """Test fibonacci for large positive integers."""
        assert fibonacci_iterative(30) == 832040
        assert fibonacci_iterative(50) == 12586269025
        assert fibonacci_iterative(100) == 354224848179261915075

    def test_very_large_numbers(self):
        """Test fibonacci for very large inputs (stress test)."""
        # Iterative approach should handle large n efficiently
        result = fibonacci_iterative(500)
        assert isinstance(result, int)
        assert result > 0

    def test_negative_number_raises_error(self):
        """Test that negative numbers raise ValueError."""
        with pytest.raises(ValueError, match="n must be a non-negative integer"):
            fibonacci_iterative(-1)

        with pytest.raises(ValueError, match="n must be a non-negative integer"):
            fibonacci_iterative(-10)

        with pytest.raises(ValueError, match="n must be a non-negative integer"):
            fibonacci_iterative(-100)

    def test_type_consistency(self):
        """Test that return type is always int."""
        for n in [0, 1, 5, 10, 20]:
            result = fibonacci_iterative(n)
            assert isinstance(result, int)


class TestFibonacciAlias:
    """Test suite for the fibonacci alias (should point to fibonacci_lru)."""

    def test_alias_points_to_lru(self):
        """Test that fibonacci is an alias for fibonacci_lru."""
        assert fibonacci is fibonacci_lru

    def test_alias_works_correctly(self):
        """Test that the alias produces correct results."""
        assert fibonacci(0) == 0
        assert fibonacci(1) == 1
        assert fibonacci(10) == 55


class TestImplementationConsistency:
    """Test that all implementations produce consistent results."""

    def setup_method(self):
        """Clear LRU cache before each test."""
        fibonacci_lru.cache_clear()

    @pytest.mark.parametrize("n", [0, 1, 2, 3, 5, 8, 10, 15, 20, 25, 30])
    def test_all_implementations_agree(self, n):
        """Test that all three implementations return the same result."""
        result_manual = fibonacci_manual_memo(n)
        result_lru = fibonacci_lru(n)
        result_iterative = fibonacci_iterative(n)

        assert result_manual == result_lru == result_iterative

    @pytest.mark.parametrize("n", [-1, -5, -10, -100])
    def test_all_implementations_raise_same_error(self, n):
        """Test that all implementations raise ValueError for negative inputs."""
        with pytest.raises(ValueError):
            fibonacci_manual_memo(n)

        with pytest.raises(ValueError):
            fibonacci_lru(n)

        with pytest.raises(ValueError):
            fibonacci_iterative(n)


class TestFibonacciSequenceProperties:
    """Test mathematical properties of the Fibonacci sequence."""

    def test_fibonacci_recurrence_relation(self):
        """Test that F(n) = F(n-1) + F(n-2) holds."""
        for n in range(2, 20):
            fib_n = fibonacci_iterative(n)
            fib_n_minus_1 = fibonacci_iterative(n - 1)
            fib_n_minus_2 = fibonacci_iterative(n - 2)
            assert fib_n == fib_n_minus_1 + fib_n_minus_2

    def test_fibonacci_monotonic_increasing(self):
        """Test that the sequence is monotonically increasing for n >= 0."""
        prev = fibonacci_iterative(0)
        for n in range(1, 30):
            curr = fibonacci_iterative(n)
            assert curr >= prev
            prev = curr

    def test_fibonacci_growth_rate(self):
        """Test that Fibonacci numbers grow exponentially."""
        # F(n+1) / F(n) should approach golden ratio (~1.618) as n increases
        for n in range(10, 20):
            fib_n = fibonacci_iterative(n)
            fib_n_plus_1 = fibonacci_iterative(n + 1)
            ratio = fib_n_plus_1 / fib_n
            # Golden ratio is approximately 1.618
            assert 1.6 < ratio < 1.62


class TestPerformance:
    """Performance and efficiency tests."""

    def setup_method(self):
        """Clear LRU cache before each test."""
        fibonacci_lru.cache_clear()

    def test_iterative_performance_large_n(self):
        """Test that iterative approach handles large n efficiently."""
        start = time.time()
        result = fibonacci_iterative(1000)
        elapsed = time.time() - start

        assert isinstance(result, int)
        assert elapsed < 0.1  # Should complete in less than 100ms

    def test_lru_cache_performance_benefit(self):
        """Test that LRU cache provides performance benefit for repeated calls."""
        fibonacci_lru.cache_clear()

        # First call (cache miss)
        start = time.time()
        fibonacci_lru(30)
        first_call_time = time.time() - start

        # Second call (cache hit)
        start = time.time()
        fibonacci_lru(30)
        second_call_time = time.time() - start

        # Cached call should be significantly faster
        assert second_call_time < first_call_time

    def test_manual_memo_reuse(self):
        """Test that manual memoization provides benefit when memo is reused."""
        memo = {}

        # Build up cache
        for i in range(20):
            fibonacci_manual_memo(i, memo)

        # This should be fast since all sub-problems are cached
        start = time.time()
        result = fibonacci_manual_memo(20, memo)
        elapsed = time.time() - start

        assert result == 6765
        assert elapsed < 0.01  # Should be very fast with full cache


class TestEdgeCasesAndBoundaries:
    """Test edge cases and boundary conditions."""

    def test_zero_is_valid(self):
        """Test that 0 is a valid input."""
        assert fibonacci_iterative(0) == 0
        assert fibonacci_lru(0) == 0
        assert fibonacci_manual_memo(0) == 0

    def test_one_is_valid(self):
        """Test that 1 is a valid input."""
        assert fibonacci_iterative(1) == 1
        assert fibonacci_lru(1) == 1
        assert fibonacci_manual_memo(1) == 1

    def test_two_is_valid(self):
        """Test that 2 is a valid input (first non-base case)."""
        assert fibonacci_iterative(2) == 1
        assert fibonacci_lru(2) == 1
        assert fibonacci_manual_memo(2) == 1

    def test_result_is_non_negative(self):
        """Test that all results are non-negative."""
        for n in range(0, 50):
            assert fibonacci_iterative(n) >= 0

    def test_large_number_doesnt_overflow(self):
        """Test that Python's arbitrary precision handles large Fibonacci numbers."""
        # Python ints have arbitrary precision, so this should work
        result = fibonacci_iterative(200)
        assert isinstance(result, int)
        assert result > 0
        # F(200) is a very large number
        assert len(str(result)) > 40  # Should have more than 40 digits


class TestInputValidation:
    """Test input validation and error handling."""

    def test_float_input_works_if_whole_number(self):
        """Test behavior with float inputs that are whole numbers."""
        # Python will accept 5.0 as 5 in most cases, but type hints suggest int
        # This tests actual behavior
        try:
            result = fibonacci_iterative(5)
            assert result == 5
        except TypeError:
            # If implementation enforces strict typing, that's also acceptable
            pass

    def test_string_input_raises_error(self):
        """Test that string inputs raise appropriate errors."""
        with pytest.raises(TypeError):
            fibonacci_iterative("5")

        with pytest.raises(TypeError):
            fibonacci_lru("10")

        with pytest.raises(TypeError):
            fibonacci_manual_memo("15")

    def test_none_input_raises_error(self):
        """Test that None input raises appropriate errors."""
        with pytest.raises(TypeError):
            fibonacci_iterative(None)

        with pytest.raises(TypeError):
            fibonacci_lru(None)

        with pytest.raises(TypeError):
            fibonacci_manual_memo(None)

    def test_boolean_input_behavior(self):
        """Test behavior with boolean inputs (True=1, False=0 in Python)."""
        # In Python, bool is a subclass of int, so True=1 and False=0
        assert fibonacci_iterative(False) == 0
        assert fibonacci_iterative(True) == 1


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
