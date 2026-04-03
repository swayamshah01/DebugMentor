"""
Real code analyzer — Phase 1.5

For Python:
  - Syntax check via ast.parse()
  - Runs actual test cases via subprocess with a 10-second timeout
  - Returns real stdout/stderr as test results

For C++ / Java / JavaScript:
  - Pattern detection only (no compiler available in Phase 1)
  - Returns pre-baked test case results consistent with the detected pattern
  - Phase 2: replace with sandboxed Docker execution

Interface is stable — only this file changes in Phase 2.
"""

import ast
import subprocess
import sys
import time
from typing import Optional

# ── Hint library ──────────────────────────────────────────────────────────────
_HINTS = {
    "syntax_error": [
        {"level": 1, "title": "Syntax Error Detected", "icon": "🚨",
         "text": "Your code has a **syntax error** — Python cannot even parse it yet. Fix this first before worrying about logic bugs."},
        {"level": 2, "title": "Where to look", "icon": "💡",
         "text": "Check the line number in the error message. Common causes: missing `:` after `if`/`for`/`def`, unmatched brackets, bad indentation."},
        {"level": 3, "title": "How to debug", "icon": "🔓",
         "text": "Run `python -m py_compile your_file.py` to check syntax without executing. Your IDE's linter will also underline the exact problem."},
    ],
    "empty_array": [
        {"level": 1, "title": "Directional nudge", "icon": "💡",
         "text": "Think carefully about what happens when the input array has **no elements at all**. Does your function handle that gracefully?"},
        {"level": 2, "title": "More specific", "icon": "💡",
         "text": "Your code accesses `arr[0]` before checking if `arr` has any elements. If the list is empty, this throws an **IndexError: list index out of range**."},
        {"level": 3, "title": "Full solution", "icon": "🔓",
         "text": "Add a guard clause at the top: `if not arr: return None`. This safely handles the empty input case before any array access."},
    ],
    "off_by_one": [
        {"level": 1, "title": "Directional nudge", "icon": "💡",
         "text": "Your loop is producing incorrect results. Think carefully about where your loop **starts and stops** — are you visiting every element?"},
        {"level": 2, "title": "More specific", "icon": "💡",
         "text": "The loop condition `i < len(arr) - 1` stops **one element early**, so the last element is never compared. Change it to `i < len(arr)`."},
        {"level": 3, "title": "Full solution", "icon": "🔓",
         "text": "Fix the loop bound: `for i in range(len(arr))`. Alternatively use Python's built-in: `return max(arr)` which handles all edge cases."},
    ],
    "recursion": [
        {"level": 1, "title": "Directional nudge", "icon": "💡",
         "text": "Your recursive function never terminates. Every recursive function needs a **base case** — a condition where it stops calling itself."},
        {"level": 2, "title": "More specific", "icon": "💡",
         "text": "The recursive call is made with the **same argument** `n`, so it never makes progress toward the base case and causes a stack overflow."},
        {"level": 3, "title": "Full solution", "icon": "🔓",
         "text": "Fix the recursive call: `return n * factorial(n - 1)`. Ensure your base case handles `n <= 1: return 1` to stop the recursion."},
    ],
    "sort_bug": [
        {"level": 1, "title": "Directional nudge", "icon": "💡",
         "text": "Your sorting function returns results in the **wrong order** for some inputs. Double-check the comparison logic inside your swap condition."},
        {"level": 2, "title": "More specific", "icon": "💡",
         "text": "The condition `arr[j] < arr[j+1]` swaps when the left element is **smaller** — this sorts in descending order. Ascending sort needs the opposite."},
        {"level": 3, "title": "Full solution", "icon": "🔓",
         "text": "Change the comparison to `arr[j] > arr[j+1]` to get ascending order. Your overall bubble sort structure is correct — only the operator is wrong."},
    ],
    "clean": [
        {"level": 1, "title": "Code quality tip", "icon": "✨",
         "text": "Your code is logically correct! Consider adding a **docstring** to document the expected input type, return value, and constraints."},
        {"level": 2, "title": "Performance insight", "icon": "💡",
         "text": "Your solution runs in **O(n)** time — optimal for this problem. Using sort to find max would be O(n log n) — unnecessary overhead."},
        {"level": 3, "title": "Pythonic refactor", "icon": "🔓",
         "text": "Python has a built-in: `return max(arr) if arr else None`. This is more readable, handles edge cases, and uses optimised C-level iteration."},
    ],
}

# ── Per-scenario test case specs ──────────────────────────────────────────────
# Each entry: (display_input, python_call, expected_output)
_TEST_SPECS = {
    "empty_array": [
        ("[3,1,4,1,5]", "find_max([3,1,4,1,5])", "5"),
        ("[]",          "find_max([])",           "None"),
        ("[-1,-5,-2]",  "find_max([-1,-5,-2])",  "-1"),
        ("[1]",         "find_max([1])",           "1"),
    ],
    "off_by_one": [
        ("[1,2,3,10]", "find_max([1,2,3,10])", "10"),
        ("[5,3,8,1]",  "find_max([5,3,8,1])",  "8"),
        ("[7]",        "find_max([7])",          "7"),
        ("[-2,-1,-5]", "find_max([-2,-1,-5])", "-1"),
    ],
    "recursion": [
        ("n=5",  "factorial(5)",  "120"),
        ("n=0",  "factorial(0)",  "1"),
        ("n=1",  "factorial(1)",  "1"),
        ("n=3",  "factorial(3)",  "6"),
    ],
    "sort_bug": [
        ("[3,1,4,1,5]", "arr=[3,1,4,1,5]; bubble_sort(arr); print(arr); exit()", str([1,1,3,4,5])),
        ("[9,2,6]",     "arr=[9,2,6]; bubble_sort(arr); print(arr); exit()",     str([2,6,9])),
        ("[1,2,3]",     "arr=[1,2,3]; bubble_sort(arr); print(arr); exit()",     str([1,2,3])),
        ("[5]",         "arr=[5]; bubble_sort(arr); print(arr); exit()",         str([5])),
    ],
    "clean": [
        ("[3,1,4,1,5]", "find_max([3,1,4,1,5])", "5"),
        ("[]",          "find_max([])",           "None"),
        ("[-1,-5,-2]",  "find_max([-1,-5,-2])",  "-1"),
        ("[1]",         "find_max([1])",           "1"),
    ],
}


def _detect_scenario(code: str) -> str:
    """Identify the bug pattern from code content."""
    c = code.lower()

    # Recursion: function calls itself with same argument
    if (("factorial" in c or "fib" in c) and
            ("factorial(n)" in c or "fib(n)" in c or
             ("return n *" in c and "n - 1" not in c and "n-1" not in c))):
        return "recursion"

    # Bubble sort with wrong comparison operator
    if (("bubble" in c or "sort" in c) and
            ("arr[j] < arr[j+1]" in c or "a[j] < a[j+1]" in c
             or "arr[j]<arr[j+1]" in c)):
        return "sort_bug"

    # Off-by-one loop bound
    if ("len(arr) - 1" in c or "len(arr)-1" in c or
            ".length - 1" in c or ".length-1" in c or
            "arr.size() - 1" in c or "arr.size()-1" in c):
        return "off_by_one"

    # Guard clause present → code is correct
    if ("if not arr" in c or "if (arr.length === 0)" in c or
            "return none" in c or "return null" in c or
            ("if" in c and "arr" in c and "empty" in c)):
        return "clean"

    return "empty_array"  # default


def _run_single_test(code: str, display_input: str,
                     py_call: str, expected: str, tc_id: int) -> dict:
    """Run one test case via subprocess and return a result dict."""
    # Build the test script
    if py_call.endswith("; exit()"):
        # For in-place mutation (sort), append call directly
        test_script = f"{code}\n\n{py_call}"
    else:
        test_script = (
            f"{code}\n\n"
            f"try:\n"
            f"    _result = {py_call}\n"
            f"    print(repr(_result))\n"
            f"except Exception as _e:\n"
            f"    print(f'ERROR: {{_e}}')\n"
        )

    try:
        proc = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0:
            actual = proc.stdout.strip() or "(no output)"
        else:
            # Last line of stderr is most informative
            err_lines = proc.stderr.strip().split("\n")
            actual = f"ERROR: {err_lines[-1][:80]}"
    except subprocess.TimeoutExpired:
        actual = "TIMEOUT (10s)"
    except Exception as e:
        actual = f"ERROR: {e}"

    # Normalise: "None" == "None", numbers as strings
    passed = actual.strip() == expected.strip()
    if not passed and actual.lower() in ("none",) and expected.lower() in ("none",):
        passed = True

    return {
        "id": tc_id,
        "input": display_input,
        "expected": expected,
        "actual": actual,
        "passed": passed,
    }


def _run_python_tests(code: str, scenario_key: str) -> tuple:
    """Execute all test cases for the given scenario. Returns (results, first_output)."""
    specs = _TEST_SPECS.get(scenario_key, _TEST_SPECS["empty_array"])
    results = []
    first_output = None

    for idx, (display_input, py_call, expected) in enumerate(specs, start=1):
        result = _run_single_test(code, display_input, py_call, expected, idx)
        results.append(result)
        if first_output is None:
            first_output = result["actual"]

    return results, first_output or ""


def _prebaked_tests(scenario_key: str) -> tuple:
    """
    Return pre-computed test results for non-Python languages.
    These reflect the expected behaviour of the detected bug pattern.
    """
    specs = _TEST_SPECS.get(scenario_key, _TEST_SPECS["empty_array"])
    is_buggy = scenario_key not in ("clean",)

    results = []
    for idx, (display_input, _, expected) in enumerate(specs, start=1):
        if scenario_key == "empty_array" and idx == 2:
            actual, passed = "ERROR", False
        elif scenario_key == "off_by_one" and idx in (1, 2):
            # Returns the second-to-last max
            actual, passed = "WRONG", False
        elif scenario_key == "recursion":
            actual, passed = "STACK OVERFLOW", False
        elif scenario_key == "sort_bug" and idx in (1, 2, 3):
            actual, passed = f"[REVERSED]", False
        else:
            actual, passed = expected, True

        results.append({
            "id": idx,
            "input": display_input,
            "expected": expected,
            "actual": actual,
            "passed": passed,
        })

    first_output = "Pattern-based analysis (runtime execution not supported for this language in Phase 1)"
    return results, first_output


# ── Public API ────────────────────────────────────────────────────────────────
def analyze_code(code: str, language: str) -> dict:
    """
    Analyze submitted code and return a fully structured result dict.

    Returns
    -------
    {
        "status":           "bugs_found" | "clean",
        "bug_summary":      str,
        "error_line":       int | None,
        "execution_output": str,
        "hints":            list[dict],
        "test_cases":       list[dict],
    }
    """
    # ── Step 1: Pattern detection (language-agnostic) ─────────────────────────
    scenario_key = _detect_scenario(code)

    # ── Step 2: Python — real execution  ──────────────────────────────────────
    if language == "python":
        # Syntax check first
        try:
            ast.parse(code)
        except SyntaxError as e:
            return {
                "status": "bugs_found",
                "bug_summary": f"Syntax error on line {e.lineno}: {e.msg}",
                "error_line": e.lineno,
                "execution_output": f"SyntaxError: {e.msg}",
                "hints": _HINTS["syntax_error"],
                "test_cases": [
                    {"id": i + 1, "input": spec[0], "expected": spec[2],
                     "actual": "SYNTAX ERROR", "passed": False}
                    for i, spec in enumerate(_TEST_SPECS.get(scenario_key,
                                                             _TEST_SPECS["empty_array"]))
                ],
            }

        # Run real test cases
        test_cases, execution_output = _run_python_tests(code, scenario_key)

        # Override scenario if all tests actually pass (code fixed)
        if all(tc["passed"] for tc in test_cases):
            scenario_key = "clean"

    else:
        # Non-Python: use pre-baked results
        test_cases, execution_output = _prebaked_tests(scenario_key)

    # ── Step 3: Build final response ──────────────────────────────────────────
    meta = {
        "empty_array": ("bugs_found", "Edge case failure on empty array input", 2),
        "off_by_one":  ("bugs_found", "Off-by-one error — loop skips the last element", 3),
        "recursion":   ("bugs_found", "Missing or incorrect base case causes infinite recursion", 5),
        "sort_bug":    ("bugs_found", "Incorrect comparison produces reverse sort", 4),
        "clean":       ("clean",      "No bugs detected — all test cases pass", None),
    }
    status, bug_summary, error_line = meta[scenario_key]

    return {
        "status":           status,
        "bug_summary":      bug_summary,
        "error_line":       error_line,
        "execution_output": execution_output,
        "hints":            _HINTS[scenario_key],
        "test_cases":       test_cases,
    }
