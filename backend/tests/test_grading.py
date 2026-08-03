from app.models.pattern import Pattern
from app.models.problem import Problem
from app.models.testcase import TestCase
from app.services.grading import _classify, grade_problem, outputs_match, public_report


def create_problem(db_session):
    pattern = Pattern(name="Arrays", slug="arrays", order_index=1)
    db_session.add(pattern)
    db_session.flush()
    problem = Problem(
        pattern_id=pattern.id,
        title="Increment",
        slug="increment",
        difficulty="easy",
        statement="Read n and print n + 1.",
        order_index=1,
    )
    db_session.add(problem)
    db_session.flush()
    visible = TestCase(
        problem_id=problem.id,
        label="Example",
        input="7",
        expected_output="8",
        is_hidden=False,
        order_index=1,
    )
    hidden = TestCase(
        problem_id=problem.id,
        label="Negative",
        input="-2",
        expected_output="-1",
        is_hidden=True,
        order_index=2,
    )
    db_session.add_all([visible, hidden])
    db_session.commit()
    return problem, visible, hidden


def test_output_comparison_handles_structures_booleans_and_floats():
    assert outputs_match("[0, 1]", "[0,1]")
    assert outputs_match("true", "True")
    assert outputs_match("12.75", "12.7500001")
    assert not outputs_match("[0, 1]", "[1, 0]")


def test_empty_output_passes_only_when_empty_is_expected():
    execution = {"stage": "run", "exit_code": 0, "actual_output": ""}

    assert _classify(execution, "") == "PASSED"
    assert _classify(execution, "value") == "EMPTY_OUTPUT"


def test_run_mode_grades_only_selected_visible_case(db_session):
    problem, visible, _ = create_problem(db_session)
    code = "def main():\n    n = int(input())\n    print(n + 1)\n\nmain()"

    report = grade_problem(
        db_session,
        problem,
        code,
        "python",
        include_hidden=False,
        test_case_id=visible.id,
    )

    assert report["success"] is True
    assert report["total"] == 1
    assert report["test_results"][0]["test_case_id"] == visible.id


def test_submit_mode_grades_hidden_cases_and_masks_values(db_session):
    problem, _, _ = create_problem(db_session)
    code = "n = int(input())\nprint(n + 1 if n >= 0 else n)"

    report = grade_problem(db_session, problem, code, "python", include_hidden=True)
    safe = public_report(report)

    assert report["failed"] == 1
    hidden = next(result for result in safe["test_results"] if result["is_hidden"])
    assert hidden["input"] is None
    assert hidden["expected_output"] is None
    assert hidden["actual_output"] is None
