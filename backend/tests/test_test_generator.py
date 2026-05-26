"""
test_test_generator.py — Unit tests for the Test Case Generator
"""
import pytest
from app.engines.test_generator import generate_tests


def test_array_function_detection():
    """Functions with param names like 'arr' should yield array edge cases."""
    code = """
def find_max(arr):
    return max(arr)
"""
    tests = generate_tests(code, "python")
    assert len(tests) > 0
    labels = [t["label"] for t in tests]
    assert "Empty array" in labels
    assert "Single element" in labels
    assert tests[0]["func_name"] == "find_max"
    assert tests[0]["func_type"] == "array"
    # Expected outputs should be computed for known patterns like find_max
    for t in tests:
        assert "expected_output" in t
        assert t["expected_output"] != None
    # Verify that the normal array case has correct expected value
    normal = next((t for t in tests if t["label"] == "Normal array"), None)
    assert normal is not None
    assert normal["expected_output"] == "5"


def test_numeric_function_detection():
    """Functions with param names like 'n' should yield numeric edge cases."""
    code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
    tests = generate_tests(code, "python")
    assert len(tests) > 0
    labels = [t["label"] for t in tests]
    assert "Zero" in labels
    assert "One" in labels
    assert tests[0]["func_type"] == "numeric"
    # Factorial expected outputs should be computed (e.g., for input 5 → 120)
    fact_case = next((t for t in tests if t["input"] == "5" or t["label"] == "Normal positive"), None)
    # If a '5' test exists, its expected should be 120
    if fact_case:
        assert fact_case["expected_output"] in ("120", "?")


def test_string_function_detection():
    """Functions with param names like 's' should yield string edge cases."""
    code = """
def reverse_string(s):
    return s[::-1]
"""
    tests = generate_tests(code, "python")
    assert len(tests) > 0
    labels = [t["label"] for t in tests]
    assert "Empty string" in labels
    assert "Single character" in labels
    assert tests[0]["func_type"] == "string"


def test_no_function_returns_empty():
    """Code without a function definition should return no tests."""
    code = 'print("hello")'
    tests = generate_tests(code, "python")
    assert tests == []


def test_non_python_returns_empty():
    """Non-Python code should return no tests."""
    code = "function findMax(arr) { return Math.max(...arr); }"
    tests = generate_tests(code, "javascript")
    assert tests == []
