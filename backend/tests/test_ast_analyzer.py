"""
test_ast_analyzer.py — Unit tests for the AST Analysis Engine

Tests all 6 bug patterns plus 1 clean-code case.
"""
import pytest
from app.engines.ast_analyzer import analyze


# ── 1. Infinite Loop ─────────────────────────────────────────────────────────
def test_infinite_loop_detected():
    code = """
while True:
    x = 1
"""
    issues = analyze(code, "python")
    types = [i["type"] for i in issues]
    assert "infinite_loop" in types
    issue = next(i for i in issues if i["type"] == "infinite_loop")
    assert issue["severity"] == "error"
    assert issue["line"] == 2


# ── 2. Mutable Default Argument ──────────────────────────────────────────────
def test_mutable_default_argument():
    code = """
def add_item(item, items=[]):
    items.append(item)
    return items
"""
    issues = analyze(code, "python")
    types = [i["type"] for i in issues]
    assert "mutable_default" in types
    issue = next(i for i in issues if i["type"] == "mutable_default")
    assert issue["severity"] == "warning"


# ── 3. Missing Recursion Base Case ───────────────────────────────────────────
def test_missing_recursion_base_case():
    code = """
def factorial(n):
    return n * factorial(n - 1)
"""
    issues = analyze(code, "python")
    types = [i["type"] for i in issues]
    assert "missing_base_case" in types
    issue = next(i for i in issues if i["type"] == "missing_base_case")
    assert issue["severity"] == "error"


# ── 4. Return Type Inconsistency ─────────────────────────────────────────────
def test_return_type_inconsistency():
    code = """
def process(x):
    if x < 0:
        return
    return x * 2
"""
    issues = analyze(code, "python")
    types = [i["type"] for i in issues]
    assert "return_inconsistency" in types
    issue = next(i for i in issues if i["type"] == "return_inconsistency")
    assert issue["severity"] == "warning"


# ── 5. Unused Variable ──────────────────────────────────────────────────────
def test_unused_variable():
    code = """
def calculate(x):
    temp = 42
    return x * 2
"""
    issues = analyze(code, "python")
    types = [i["type"] for i in issues]
    assert "unused_variable" in types
    issue = next(i for i in issues if i["type"] == "unused_variable")
    assert issue["severity"] == "info"
    assert "temp" in issue["message"]


# ── 6. Off-by-One in range() ────────────────────────────────────────────────
def test_off_by_one():
    code = """
def find_max(arr):
    max_val = arr[0]
    for i in range(len(arr) - 1):
        if arr[i] > max_val:
            max_val = arr[i]
    return max_val
"""
    issues = analyze(code, "python")
    types = [i["type"] for i in issues]
    assert "off_by_one" in types
    issue = next(i for i in issues if i["type"] == "off_by_one")
    assert issue["severity"] == "warning"


# ── 7. Clean Code — No Issues ───────────────────────────────────────────────
def test_clean_code():
    code = """
def find_max(arr):
    if not arr:
        return None
    max_val = arr[0]
    for i in range(len(arr)):
        if arr[i] > max_val:
            max_val = arr[i]
    return max_val
"""
    issues = analyze(code, "python")
    assert len(issues) == 0


# ── 8. SyntaxError handled gracefully ────────────────────────────────────────
def test_syntax_error_handling():
    code = 'def foo(:\n  pass'
    issues = analyze(code, "python")
    assert len(issues) == 1
    assert issues[0]["type"] == "syntax_error"
    assert issues[0]["severity"] == "error"


# ── 9. Non-Python language returns empty ─────────────────────────────────────
def test_non_python_language():
    code = "int main() { return 0; }"
    issues = analyze(code, "cpp")
    assert issues == []
