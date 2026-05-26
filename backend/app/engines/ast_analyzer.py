"""
ast_analyzer.py — Static Analysis Engine (Phase 2)

Python  : Traverses the AST to detect 6 specific bug patterns.
C++     : Regex-based static analysis detecting 5 common bug patterns.

Returns a list of issue dicts for consumption by the /submit pipeline.
"""

import ast
import re
from typing import List, Dict, Any


# ═══════════════════════════════════════════════════════════════════════════════
#  PYTHON — AST-based detectors
# ═══════════════════════════════════════════════════════════════════════════════

# ── 1. Infinite Loop Detector ────────────────────────────────────────────────
def _detect_infinite_loops(tree: ast.AST) -> List[Dict[str, Any]]:
    """Flag `while True` loops that lack a `break` or `return` in the body."""
    issues = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.While):
            continue
        cond = node.test
        is_true = False
        if isinstance(cond, ast.Constant) and cond.value is True:
            is_true = True
        elif isinstance(cond, ast.NameConstant) and cond.value is True:
            is_true = True

        if not is_true:
            continue

        has_exit = False
        for child in ast.walk(node):
            if isinstance(child, (ast.Break, ast.Return)):
                has_exit = True
                break

        if not has_exit:
            issues.append({
                "type": "infinite_loop",
                "line": node.lineno,
                "col": node.col_offset,
                "severity": "error",
                "title": "Potential Infinite Loop",
                "message": (
                    "`while True` loop without a `break` or `return` statement. "
                    "This will run forever."
                ),
                "suggestion": (
                    "Add a `break` or `return` inside the loop to allow it to terminate."
                ),
            })
    return issues


# ── 2. Mutable Default Argument Detector ─────────────────────────────────────
def _detect_mutable_defaults(tree: ast.AST) -> List[Dict[str, Any]]:
    """Flag mutable objects (list, dict, set) used as default arguments."""
    issues = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                type_name = type(default).__name__.lower()
                issues.append({
                    "type": "mutable_default",
                    "line": node.lineno,
                    "col": node.col_offset,
                    "severity": "warning",
                    "title": "Mutable Default Argument",
                    "message": (
                        f"Function `{node.name}` has a mutable default argument "
                        f"({type_name}). This is shared across all calls."
                    ),
                    "suggestion": (
                        "Use `None` as the default and initialize the mutable object "
                        "inside the function body."
                    ),
                })
    return issues


# ── 3. Missing Recursion Base Case Detector ──────────────────────────────────
def _detect_missing_base_case(tree: ast.AST) -> List[Dict[str, Any]]:
    """Flag recursive functions that lack an `if` statement (base case)."""
    issues = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        func_name = node.name
        calls_self = False
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                fn = child.func
                if isinstance(fn, ast.Name) and fn.id == func_name:
                    calls_self = True
                    break

        if not calls_self:
            continue

        has_if = any(isinstance(stmt, ast.If) for stmt in node.body)

        if not has_if:
            issues.append({
                "type": "missing_base_case",
                "line": node.lineno,
                "col": node.col_offset,
                "severity": "error",
                "title": "Missing Recursion Base Case",
                "message": (
                    f"Function `{func_name}` calls itself recursively but has "
                    f"no `if` statement to act as a base case."
                ),
                "suggestion": (
                    "Add a base-case `if` condition that returns without a "
                    "recursive call (e.g., `if n <= 1: return 1`)."
                ),
            })
    return issues


# ── 4. Return Type Inconsistency Detector ────────────────────────────────────
def _detect_return_inconsistency(tree: ast.AST) -> List[Dict[str, Any]]:
    """Flag functions that mix bare `return` with `return <value>`."""
    issues = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        returns = [
            child for child in ast.walk(node)
            if isinstance(child, ast.Return)
        ]
        if len(returns) < 2:
            continue

        bare_returns = [r for r in returns if r.value is None]
        value_returns = [r for r in returns if r.value is not None]

        if bare_returns and value_returns:
            issues.append({
                "type": "return_inconsistency",
                "line": bare_returns[0].lineno,
                "col": bare_returns[0].col_offset,
                "severity": "warning",
                "title": "Return Type Inconsistency",
                "message": (
                    f"Function `{node.name}` mixes bare `return` statements with "
                    f"`return <value>` statements."
                ),
                "suggestion": (
                    "Decide on a consistent return strategy. If you must return early, "
                    "explicitly return `None` (e.g., `return None`) for clarity."
                ),
            })
    return issues


# ── 5. Unused Variable Detector ──────────────────────────────────────────────
def _detect_unused_variables(tree: ast.AST) -> List[Dict[str, Any]]:
    """Track variables assigned (Store) vs. referenced (Load). Flag assigned-but-never-read."""
    issues = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        stored: Dict[str, ast.Name] = {}
        loaded = set()

        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                if isinstance(child.ctx, ast.Store):
                    if child.id not in stored:
                        stored[child.id] = child
                elif isinstance(child.ctx, ast.Load):
                    loaded.add(child.id)

        param_names = {a.arg for a in node.args.args}

        for var_name, var_node in stored.items():
            if var_name.startswith("_"):
                continue
            if var_name in param_names:
                continue
            if var_name not in loaded:
                issues.append({
                    "type": "unused_variable",
                    "line": var_node.lineno,
                    "col": var_node.col_offset,
                    "severity": "info",
                    "title": "Unused Variable",
                    "message": (
                        f"Variable `{var_name}` is assigned but never used in "
                        f"function `{node.name}`."
                    ),
                    "suggestion": (
                        f"Remove `{var_name}` or prefix it with `_` if it's intentionally unused."
                    ),
                })
    return issues


# ── 6. Off-by-One in range() Detector ────────────────────────────────────────
def _detect_off_by_one(tree: ast.AST) -> List[Dict[str, Any]]:
    """Detect `range(len(x) - 1)` patterns that may skip the last element."""
    issues = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if not (isinstance(fn, ast.Name) and fn.id == "range"):
            continue
        if len(node.args) < 1:
            continue

        arg = node.args[0]
        if not isinstance(arg, ast.BinOp):
            continue
        if not isinstance(arg.op, ast.Sub):
            continue
        right = arg.right
        is_one = isinstance(right, ast.Constant) and right.value == 1
        if not is_one:
            continue
        left = arg.left
        if not isinstance(left, ast.Call):
            continue
        left_fn = left.func
        if not (isinstance(left_fn, ast.Name) and left_fn.id == "len"):
            continue

        issues.append({
            "type": "off_by_one",
            "line": node.lineno,
            "col": node.col_offset,
            "severity": "warning",
            "title": "Possible Off-by-One Error",
            "message": (
                "`range(len(...) - 1)` skips the last element of the sequence. "
                "This is a common source of off-by-one bugs."
            ),
            "suggestion": (
                "If you need to iterate over every element, use `range(len(arr))` "
                "or, even better, iterate directly: `for item in arr`."
            ),
        })
    return issues


# ═══════════════════════════════════════════════════════════════════════════════
#  C++ — Regex-based detectors
# ═══════════════════════════════════════════════════════════════════════════════

def _strip_cpp_comments(code: str) -> str:
    """Remove // line comments and /* block comments */ from C++ source."""
    # Block comments
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    # Line comments
    code = re.sub(r'//[^\n]*', '', code)
    return code


def _cpp_line_of(code: str, match_start: int) -> int:
    """Return 1-indexed line number for a character position in the code."""
    return code[:match_start].count('\n') + 1


def _detect_cpp_infinite_loops(code: str) -> List[Dict[str, Any]]:
    """Flag `while(true)` / `while(1)` blocks that lack a break or return."""
    issues = []
    clean = _strip_cpp_comments(code)

    pattern = re.compile(r'\bwhile\s*\(\s*(true|1)\s*\)\s*\{', re.IGNORECASE)
    for m in pattern.finditer(clean):
        # Find the matching closing brace
        start = m.end() - 1  # position of opening '{'
        depth = 0
        body = ""
        for i in range(start, len(clean)):
            if clean[i] == '{':
                depth += 1
            elif clean[i] == '}':
                depth -= 1
                if depth == 0:
                    body = clean[start:i]
                    break

        has_exit = bool(re.search(r'\b(break|return)\b', body))
        if not has_exit:
            line = _cpp_line_of(clean, m.start())
            issues.append({
                "type": "infinite_loop",
                "line": line,
                "col": 0,
                "severity": "error",
                "title": "Potential Infinite Loop",
                "message": (
                    f"`while({m.group(1)})` loop at line {line} has no `break` or "
                    "`return` statement — it will run forever."
                ),
                "suggestion": (
                    "Add a `break` statement inside the loop body, or restructure "
                    "the condition to be a finite expression."
                ),
            })
    return issues


def _detect_cpp_assignment_in_condition(code: str) -> List[Dict[str, Any]]:
    """Flag `if (x = value)` — likely a typo for `==`."""
    issues = []
    clean = _strip_cpp_comments(code)

    # Match if(...) where the condition contains = but not ==, !=, <=, >=
    pattern = re.compile(
        r'\bif\s*\(([^)]*[^=!<>])=(?!=)([^)]*)\)',
        re.MULTILINE,
    )
    for m in pattern.finditer(clean):
        line = _cpp_line_of(clean, m.start())
        issues.append({
            "type": "assignment_in_condition",
            "line": line,
            "col": 0,
            "severity": "error",
            "title": "Assignment Inside Condition",
            "message": (
                f"Line {line}: `if ({m.group(0)[3:].strip()})` uses `=` "
                "inside a condition — this is almost always a bug (meant `==`)."
            ),
            "suggestion": (
                "Change `=` to `==` for comparison. "
                "If intentional, wrap in double parentheses: `if ((x = value))`."
            ),
        })
    return issues


def _detect_cpp_memory_leaks(code: str) -> List[Dict[str, Any]]:
    """Flag `new` allocations that have no matching `delete`."""
    issues = []
    clean = _strip_cpp_comments(code)

    new_count   = len(re.findall(r'\bnew\b', clean))
    delete_count = len(re.findall(r'\bdelete\b', clean))

    if new_count > 0 and delete_count < new_count:
        # Find the first `new` for line reporting
        m = re.search(r'\bnew\b', clean)
        line = _cpp_line_of(clean, m.start()) if m else 1
        issues.append({
            "type": "memory_leak",
            "line": line,
            "col": 0,
            "severity": "warning",
            "title": "Potential Memory Leak",
            "message": (
                f"Found {new_count} `new` allocation(s) but only {delete_count} "
                "`delete` call(s). Heap memory may not be freed."
            ),
            "suggestion": (
                "Pair every `new` with a corresponding `delete` (or `delete[]` for arrays). "
                "Consider using smart pointers (`std::unique_ptr`, `std::shared_ptr`) "
                "to manage memory automatically."
            ),
        })
    return issues


def _detect_cpp_off_by_one(code: str) -> List[Dict[str, Any]]:
    """Flag `i <= arr.size()` / `i <= n` patterns in for-loops (off-by-one)."""
    issues = []
    clean = _strip_cpp_comments(code)

    # for(...; i <= container.size(); ...) or <= n where n is the length
    pattern = re.compile(
        r'\bfor\s*\([^;]*;[^;]*\w+\s*<=\s*(?:\w+\.size\(\)|strlen\s*\([^)]+\)|\w+\.length\(\))',
        re.MULTILINE,
    )
    for m in pattern.finditer(clean):
        line = _cpp_line_of(clean, m.start())
        issues.append({
            "type": "off_by_one",
            "line": line,
            "col": 0,
            "severity": "warning",
            "title": "Possible Off-by-One Error",
            "message": (
                f"Line {line}: loop condition uses `<=` with `.size()` or `.length()`. "
                "This accesses one index past the end of the container."
            ),
            "suggestion": (
                "Use `<` instead of `<=` when iterating with `.size()` / `.length()`: "
                "`for (int i = 0; i < arr.size(); i++)`."
            ),
        })
    return issues


def _detect_cpp_missing_return(code: str) -> List[Dict[str, Any]]:
    """Flag non-void functions that may not have a return on all paths."""
    issues = []
    clean = _strip_cpp_comments(code)

    # Match non-void function definitions
    func_pattern = re.compile(
        r'\b(?!void\b)(int|long|long long|double|float|bool|string|auto|char)\s+'
        r'(\w+)\s*\([^)]*\)\s*\{',
        re.MULTILINE,
    )

    for func_m in func_pattern.finditer(clean):
        func_name = func_m.group(2)
        # Skip main
        if func_name == 'main':
            continue

        # Extract function body
        start = func_m.end() - 1
        depth = 0
        body = ""
        for i in range(start, len(clean)):
            if clean[i] == '{':
                depth += 1
            elif clean[i] == '}':
                depth -= 1
                if depth == 0:
                    body = clean[start + 1:i]
                    break

        # Check if function ends with a return
        stripped_body = body.strip()
        last_line = stripped_body.split('\n')[-1].strip() if stripped_body else ''

        # Simple heuristic: no return statement at all
        if not re.search(r'\breturn\b', body):
            line = _cpp_line_of(clean, func_m.start())
            issues.append({
                "type": "missing_return",
                "line": line,
                "col": 0,
                "severity": "warning",
                "title": "Missing Return Statement",
                "message": (
                    f"Function `{func_name}` has a non-void return type "
                    f"(`{func_m.group(1)}`) but contains no `return` statement."
                ),
                "suggestion": (
                    f"Add a `return` statement that returns a value of type "
                    f"`{func_m.group(1)}`. Forgetting to return causes undefined behaviour."
                ),
            })

    return issues


def _analyze_cpp(code: str) -> List[Dict[str, Any]]:
    """Run all C++ regex-based static analysis detectors."""
    issues: List[Dict[str, Any]] = []
    issues.extend(_detect_cpp_infinite_loops(code))
    issues.extend(_detect_cpp_assignment_in_condition(code))
    issues.extend(_detect_cpp_memory_leaks(code))
    issues.extend(_detect_cpp_off_by_one(code))
    issues.extend(_detect_cpp_missing_return(code))
    return issues


# ═══════════════════════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════════════════════

def analyze(code: str, language: str) -> List[Dict[str, Any]]:
    """
    Run static analysis on the given code.

    Parameters
    ----------
    code : str
        The raw source code string.
    language : str
        The programming language. Supported: 'python', 'cpp'.

    Returns
    -------
    list[dict]
        A list of issue dicts with keys:
        type, line, col, severity, title, message, suggestion.
    """
    lang = language.lower()

    # ── C++ ───────────────────────────────────────────────────────────────────
    if lang == "cpp":
        return _analyze_cpp(code)

    # ── Python ────────────────────────────────────────────────────────────────
    if lang == "python":
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [{
                "type": "syntax_error",
                "line": e.lineno or 1,
                "col": e.offset or 0,
                "severity": "error",
                "title": "Syntax Error",
                "message": str(e.msg) if hasattr(e, "msg") else str(e),
                "suggestion": "Fix the syntax error before further analysis can proceed.",
            }]

        issues: List[Dict[str, Any]] = []
        issues.extend(_detect_infinite_loops(tree))
        issues.extend(_detect_mutable_defaults(tree))
        issues.extend(_detect_missing_base_case(tree))
        issues.extend(_detect_return_inconsistency(tree))
        issues.extend(_detect_unused_variables(tree))
        issues.extend(_detect_off_by_one(tree))
        return issues

    # ── Unsupported language ──────────────────────────────────────────────────
    return []
