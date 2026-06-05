"""Tests for curated problem evaluation against stored test cases."""

import uuid

from app.engines.llm_layer import build_contextual_fallback
from app.database import SessionLocal
from app.models.pattern import Pattern
from app.models.problem import Problem
from app.models.testcase import TestCase
from app.services.problem_evaluator import evaluate_problem_submission, classify_hint_intent


def test_evaluate_problem_submission_uses_stored_test_cases():
    db = SessionLocal()
    try:
        pattern = Pattern(
            name=f"DP {uuid.uuid4().hex[:6]}",
            slug=f"dp-{uuid.uuid4().hex[:6]}",
            description="DP problems",
            icon_name="🔄",
            order_index=1,
        )
        db.add(pattern)
        db.flush()

        problem = Problem(
            pattern_id=pattern.id,
            title="Increment",
            slug=f"increment-{uuid.uuid4().hex[:6]}",
            difficulty="easy",
            short_description="Increment a number",
            statement="Return n + 1",
            starter_code_json={"python": "def solve(n):\n    return n + 1"},
            is_active=True,
            order_index=1,
        )
        db.add(problem)
        db.commit()

        db.add_all([
            TestCase(problem_id=problem.id, label="Visible", input="1", expected_output="2", is_hidden=False, order_index=1),
            TestCase(problem_id=problem.id, label="Hidden", input="2", expected_output="3", is_hidden=True, order_index=2),
        ])
        db.commit()

        raw_results, failure_report, test_cases = evaluate_problem_submission(
            problem=problem,
            code="def solve(n):\n    return n + 1",
            language="python",
            db=db,
        )

        assert len(test_cases) == 2
        assert len(raw_results) == 2
        assert failure_report["failed"] == 0
        assert failure_report["dominant_failure_type"] is None
    finally:
        db.query(TestCase).delete()
        db.query(Problem).delete()
        db.query(Pattern).delete()
        db.commit()
        db.close()


def test_classify_hint_intent_prefers_bug_fix_for_runtime_and_wrong_output():
    assert classify_hint_intent({"dominant_failure_type": "WRONG_OUTPUT"}, []) == "conceptual"
    assert classify_hint_intent({"dominant_failure_type": "RUNTIME_ERROR"}, []) == "bug_fix"


def test_build_contextual_fallback_uses_visible_wrong_output_case():
    result = build_contextual_fallback(
        language="python",
        failure_report={
            "dominant_failure_type": "WRONG_OUTPUT",
            "test_results": [
                {
                    "status": "WRONG_OUTPUT",
                    "input": "[2, 7, 11, 15]\n9",
                    "expected_output": "[0, 1]",
                    "actual_output": "[1, 0]",
                }
            ],
        },
        ast_issues=[],
        problem_title="Two Sum",
    )

    assert "Two Sum" in result["explanation"]
    assert "[0, 1]" in result["explanation"]
    assert "visible testcase" in result["hint_1"].lower() or "visible case" in result["hint_1"].lower()
    assert result["hint_2"]


def test_build_contextual_fallback_uses_runtime_error_message():
    result = build_contextual_fallback(
        language="python",
        failure_report={
            "dominant_failure_type": "RUNTIME_ERROR",
            "test_results": [
                {
                    "status": "RUNTIME_ERROR",
                    "error_message": "Traceback...\nTypeError: solve() takes 0 positional arguments but 2 were given",
                }
            ],
        },
        ast_issues=[],
        problem_title="Two Sum",
    )

    assert "TypeError" in result["explanation"]
    assert "function signature" in result["hint_1"].lower()
