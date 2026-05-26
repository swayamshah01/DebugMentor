"""
test_failure_detector.py — Unit tests for the Failure Detection Engine

Tests all 5 states: Runtime Error, Timeout, Empty Output, Wrong Output
(reserved), and All Passed.
"""
import pytest
from app.engines.failure_detector import detect_failures


def test_runtime_error():
    """Non-zero exit code → RUNTIME_ERROR status."""
    test_results = [
        {
            "input": "[]",
            "label": "Empty array",
            "expected_output": "?",
            "actual_output": "",
            "error_message": "IndexError: list index out of range",
            "exit_code": 1,
            "timed_out": False,
            "execution_time_ms": 12,
        }
    ]
    report = detect_failures(test_results)

    assert report["total"] == 1
    assert report["passed"] == 0
    assert report["failed"] == 1
    assert report["has_failures"] is True
    assert report["dominant_failure_type"] == "RUNTIME_ERROR"
    assert report["test_results"][0]["status"] == "RUNTIME_ERROR"
    assert report["test_results"][0]["error_type"] == "IndexError"


def test_timeout():
    """Timed-out execution → TIMEOUT status."""
    test_results = [
        {
            "input": "5",
            "label": "Normal input",
            "expected_output": "?",
            "actual_output": "",
            "error_message": "Execution timed out after 5 seconds.",
            "exit_code": 124,
            "timed_out": True,
            "execution_time_ms": 5000,
        }
    ]
    report = detect_failures(test_results)

    assert report["total"] == 1
    assert report["failed"] == 1
    assert report["dominant_failure_type"] == "TIMEOUT"
    assert report["test_results"][0]["status"] == "TIMEOUT"


def test_empty_output():
    """Successful exit but empty stdout → EMPTY_OUTPUT status."""
    test_results = [
        {
            "input": "[1, 2, 3]",
            "label": "Normal array",
            "expected_output": "?",
            "actual_output": "",
            "error_message": "",
            "exit_code": 0,
            "timed_out": False,
            "execution_time_ms": 8,
        }
    ]
    report = detect_failures(test_results)

    assert report["total"] == 1
    assert report["failed"] == 1
    assert report["dominant_failure_type"] == "EMPTY_OUTPUT"
    assert report["test_results"][0]["status"] == "EMPTY_OUTPUT"


def test_all_passed():
    """Clean execution with output → PASSED status."""
    test_results = [
        {
            "input": "[3, 1, 4, 1, 5]",
            "label": "Normal array",
            "expected_output": "?",
            "actual_output": "5",
            "error_message": "",
            "exit_code": 0,
            "timed_out": False,
            "execution_time_ms": 7,
        },
        {
            "input": "[-1, -5, -2]",
            "label": "All negatives",
            "expected_output": "?",
            "actual_output": "-1",
            "error_message": "",
            "exit_code": 0,
            "timed_out": False,
            "execution_time_ms": 6,
        },
    ]
    report = detect_failures(test_results)

    assert report["total"] == 2
    assert report["passed"] == 2
    assert report["failed"] == 0
    assert report["has_failures"] is False
    assert report["dominant_failure_type"] is None
    assert "passed successfully" in report["failure_summary"]


def test_mixed_results():
    """Mix of passing and failing test cases — report counts correctly."""
    test_results = [
        {
            "input": "[3, 1, 4]",
            "label": "Normal",
            "expected_output": "?",
            "actual_output": "4",
            "error_message": "",
            "exit_code": 0,
            "timed_out": False,
            "execution_time_ms": 5,
        },
        {
            "input": "[]",
            "label": "Empty",
            "expected_output": "?",
            "actual_output": "",
            "error_message": "IndexError: list index out of range",
            "exit_code": 1,
            "timed_out": False,
            "execution_time_ms": 10,
        },
    ]
    report = detect_failures(test_results)

    assert report["total"] == 2
    assert report["passed"] == 1
    assert report["failed"] == 1
    assert report["has_failures"] is True


def test_wrong_output_detection():
    """When expected_output is provided and differs from actual_output → WRONG_OUTPUT."""
    test_results = [
        {
            "input": "[3, 1, 4]",
            "label": "Normal",
            "expected_output": "4",
            "actual_output": "3",
            "error_message": "",
            "exit_code": 0,
            "timed_out": False,
            "execution_time_ms": 5,
        }
    ]
    report = detect_failures(test_results)

    assert report["total"] == 1
    assert report["passed"] == 0
    assert report["failed"] == 1
    assert report["dominant_failure_type"] == "WRONG_OUTPUT"
    assert report["test_results"][0]["status"] == "WRONG_OUTPUT"
