"""
Dummy analysis service — Phase 1 placeholder.

Phase 2 replacement plan:
--------------------------
1. Run the submitted code in a sandboxed Docker container
2. Capture stdout, stderr, and exit code
3. Pass code + runtime error to an LLM (OpenAI / Gemini) for hint generation
4. Run AST analysis (Python `ast` module, tree-sitter for multi-language)
5. Return dynamically generated, personalized hints

Keep this function signature stable — only the body changes in Phase 2.
"""


def analyze_code(code: str, language: str) -> dict:
    """
    Analyze submitted code and return a structured result.

    Parameters
    ----------
    code     : the raw source code string submitted by the student
    language : programming language identifier ("python", "cpp", etc.)

    Returns
    -------
    dict with keys:
        status     : "analyzed" | "error"
        hint_level : int (0 = first nudge, 1 = more specific, 2 = solution)
        feedback   : str — the hint text shown to the student
    """
    # ── Phase 1: hardcoded dummy response ─────────────────────────────────────
    # Quick heuristic sniff — gives Phase 1 a tiny bit of realism
    code_lower = code.lower()

    if "recursion" in code_lower or ("def " in code_lower and code_lower.count("(n)") > 1):
        feedback = (
            "Hint: Your recursive function may never terminate. "
            "Every recursion needs a base case — a condition where it stops calling itself."
        )
    elif "range(" in code_lower and ("- 1" in code or "-1" in code):
        feedback = (
            "Hint: Check your loop bounds carefully. "
            "An off-by-one error in `range()` can cause you to skip the last element."
        )
    elif "sort" in code_lower or "bubble" in code_lower:
        feedback = (
            "Hint: Your comparison operator may be inverted. "
            "Check whether `arr[j] > arr[j+1]` or `arr[j] < arr[j+1]` gives ascending order."
        )
    else:
        feedback = (
            "Hint: Check your loop termination condition. "
            "Are you sure the loop exits at the right time, "
            "and that all edge cases (e.g. empty input) are handled?"
        )

    return {
        "status":     "analyzed",
        "hint_level": 0,
        "feedback":   feedback,
    }
