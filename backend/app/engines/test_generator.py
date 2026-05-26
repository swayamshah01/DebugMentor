"""
test_generator.py — Automatic Edge-Case Generator (Phase 2)

Parses a Python function to determine its parameter type heuristic
(Array, Numeric, String) and generates a set of tricky edge-case inputs.
"""

import ast
import re
from typing import List, Dict, Any
import ast as _ast
from ast import literal_eval


# ── Heuristic keyword sets ───────────────────────────────────────────────────
ARRAY_KEYWORDS = {"arr", "array", "list", "lst", "nums", "numbers", "items", "elements", "values", "data"}
NUMERIC_KEYWORDS = {"n", "num", "x", "y", "k", "m", "number", "val", "value", "count", "target", "index"}
STRING_KEYWORDS = {"s", "str", "string", "text", "word", "sentence", "name", "char", "chars"}


# ── Edge case banks ──────────────────────────────────────────────────────────
ARRAY_EDGE_CASES = [
    {"input": "[3, 1, 4, 1, 5]",    "label": "Normal array"},
    {"input": "[]",                  "label": "Empty array"},
    {"input": "[-3, -1, -4, -1, -5]", "label": "All negatives"},
    {"input": "[7]",                 "label": "Single element"},
    {"input": "[0, 0, 0, 0]",       "label": "All zeros"},
    {"input": "[999999, -999999, 0]", "label": "Large values"},
]

NUMERIC_EDGE_CASES = [
    {"input": "0",          "label": "Zero"},
    {"input": "-1",         "label": "Negative one"},
    {"input": "1",          "label": "One"},
    {"input": "1000000",    "label": "Large positive"},
    {"input": "-1000000",   "label": "Large negative"},
]

STRING_EDGE_CASES = [
    {"input": '""',            "label": "Empty string"},
    {"input": '"a"',           "label": "Single character"},
    {"input": '"hello"',       "label": "Normal word"},
    {"input": '"   "',         "label": "Spaces only"},
    {"input": '"12345"',       "label": "Digits only"},
    {"input": '"!@#$%"',       "label": "Special characters"},
]


def _extract_function_info(code: str) -> Dict[str, Any]:
    """
    Parse the code to find the first function definition and extract
    its name and parameter names.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {"name": None, "params": []}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            params = [arg.arg for arg in node.args.args]
            return {"name": node.name, "params": params}

    return {"name": None, "params": []}


def _classify_function(params: List[str]) -> str:
    """
    Classify the function type based on parameter names.
    Returns 'array', 'numeric', 'string', or 'generic'.
    """
    param_set = {p.lower() for p in params}

    if param_set & ARRAY_KEYWORDS:
        return "array"
    if param_set & STRING_KEYWORDS:
        return "string"
    if param_set & NUMERIC_KEYWORDS:
        return "numeric"
    return "generic"


def generate_tests(code: str, language: str = "python") -> List[Dict[str, Any]]:
    """
    Generate edge-case test inputs based on the detected function type.

    Parameters
    ----------
    code : str
        The raw source code string.
    language : str
        Programming language (only 'python' fully supported).

    Returns
    -------
    list[dict]
        A list of test case dicts, each containing:
        - input: str – the input value to feed
        - label: str – human-readable description
        - expected_output: str – set to '?' (unknown until Phase 3)
        - func_name: str – the detected function name
        - func_type: str – array / numeric / string / generic
    """
    if language.lower() != "python":
        return []

    info = _extract_function_info(code)
    func_name = info["name"]
    params = info["params"]

    if not func_name:
        return []

    func_type = _classify_function(params)

    if func_type == "array":
        edge_cases = ARRAY_EDGE_CASES
    elif func_type == "numeric":
        edge_cases = NUMERIC_EDGE_CASES
    elif func_type == "string":
        edge_cases = STRING_EDGE_CASES
    else:
        # Generic fallback: combine a subset from each category
        edge_cases = [
            ARRAY_EDGE_CASES[0],   # normal array
            ARRAY_EDGE_CASES[1],   # empty array
            NUMERIC_EDGE_CASES[0], # zero
            NUMERIC_EDGE_CASES[2], # one
            STRING_EDGE_CASES[0],  # empty string
            STRING_EDGE_CASES[2],  # normal word
        ]

    def _compute_expected(fname: str, inp: str):
        """Compute expected output for a few built-in problems when possible.

        Returns the string representation of the expected output or None.
        """
        if not fname:
            return None
        lname = fname.lower()
        try:
            val = literal_eval(inp)
        except Exception:
            # If literal_eval fails, fall back to raw string (for quoted strings)
            val = inp.strip('"\'')

        # find_max / max
        if "find_max" in lname or ("max" == lname) or "findmax" in lname:
            try:
                if isinstance(val, (list, tuple)):
                    if len(val) == 0:
                        return "None"
                    return str(max(val))
            except Exception:
                return None

        # factorial
        if "factorial" in lname:
            try:
                n = int(val)
                if n < 0:
                    return None
                res = 1
                for k in range(2, n + 1):
                    res *= k
                return str(res)
            except Exception:
                return None

        # sum of array
        if "sum" in lname or "sum_of" in lname:
            try:
                if isinstance(val, (list, tuple)):
                    return str(sum(val))
            except Exception:
                return None

        # reverse string
        if "reverse" in lname and isinstance(val, str):
            try:
                return str(val[::-1])
            except Exception:
                return None

        # palindrome
        if "palindrome" in lname:
            try:
                s = str(val)
                return "True" if s == s[::-1] else "False"
            except Exception:
                return None

        return None

    tests = []
    for i, case in enumerate(edge_cases):
        expected = _compute_expected(func_name, case["input"])
        tests.append({
            "input": case["input"],
            "label": case["label"],
            "expected_output": expected if expected is not None else "?",
            "func_name": func_name,
            "func_type": func_type,
        })

    return tests
