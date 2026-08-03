import uuid

from app.models.pattern import Pattern
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.testcase import TestCase
from app.models.user import User


PASSING_PROGRAM = "def main():\n    n = int(input())\n    print(n + 1)\n\nmain()"
FAILING_PROGRAM = "def main():\n    n = int(input())\n    print(n)\n\nmain()"


def create_catalog(db_session):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"student_{suffix}",
        email=f"student_{suffix}@example.com",
        hashed_password="unused-in-overridden-auth",
    )
    pattern = Pattern(name=f"Basics {suffix}", slug=f"basics-{suffix}", order_index=1)
    db_session.add_all([user, pattern])
    db_session.flush()
    problem = Problem(
        pattern_id=pattern.id,
        title="Increment",
        slug=f"increment-{suffix}",
        difficulty="easy",
        short_description="Add one to an integer.",
        statement="Read n and print n + 1.",
        input_format="Line 1: n - an integer.",
        output_format="Print one integer.",
        starter_code_json={"python": PASSING_PROGRAM},
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
        label="Hidden negative",
        input="-2",
        expected_output="-1",
        is_hidden=True,
        order_index=2,
    )
    db_session.add_all([visible, hidden])
    db_session.commit()
    return user, pattern, problem, visible


def test_catalog_returns_formats_and_never_exposes_hidden_cases(api_client, db_session):
    client, _ = api_client
    _, pattern, problem, visible = create_catalog(db_session)

    patterns = client.get("/api/patterns").json()["patterns"]
    assert next(item for item in patterns if item["id"] == pattern.id)["problem_count"] == 1

    response = client.get(f"/api/problems/{problem.id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["input_format"] == "Line 1: n - an integer."
    assert payload["test_cases"] == [
        {
            "id": visible.id,
            "label": "Example",
            "input": "7",
            "expected_output": "8",
            "order_index": 1,
        }
    ]


def test_run_checks_only_the_selected_visible_case_without_persisting(api_client, db_session):
    client, authenticate_as = api_client
    user, _, problem, visible = create_catalog(db_session)
    authenticate_as(user)

    response = client.post(
        "/api/run",
        json={
            "code": PASSING_PROGRAM,
            "language": "python",
            "problem_id": problem.id,
            "test_case_id": visible.id,
        },
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["total_tests"] == 1
    assert db_session.query(Submission).count() == 0


def test_submit_checks_all_cases_persists_and_masks_hidden_values(api_client, db_session):
    client, authenticate_as = api_client
    user, _, problem, _ = create_catalog(db_session)
    authenticate_as(user)

    response = client.post(
        "/api/submit",
        json={"code": FAILING_PROGRAM, "language": "python", "problem_id": problem.id},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "failed"
    assert payload["total_tests"] == 2
    assert db_session.query(Submission).count() == 1
    hidden = next(result for result in payload["test_results"] if result["is_hidden"])
    assert hidden["input"] is None
    assert hidden["expected_output"] is None
    assert hidden["actual_output"] is None


def test_hint_levels_are_persisted_and_personalized_bundle_is_generated_once(
    api_client,
    db_session,
    monkeypatch,
):
    client, authenticate_as = api_client
    user, _, problem, _ = create_catalog(db_session)
    authenticate_as(user)

    submit = client.post(
        "/api/submit",
        json={"code": FAILING_PROGRAM, "language": "python", "problem_id": problem.id},
    ).json()

    calls = 0

    def fake_bundle(submission, selected_problem):
        nonlocal calls
        calls += 1
        assert "print(n)" in submission.code
        assert selected_problem.id == problem.id
        return {
            "diagnosis": "The program prints n unchanged, so it never performs the required increment.",
            "hints": [
                {"level": 1, "title": "Trace the printed value", "content": "For input 7, what value reaches print, and where should the extra one be applied?", "focus": "data flow"},
                {"level": 2, "title": "Update the expression", "content": "Inspect the expression passed to print; it must represent the required transformation of n.", "focus": "output expression"},
            ],
            "solution": {
                "title": "Complete console solution",
                "explanation": "Read the integer, add one, and print the result.",
                "code": PASSING_PROGRAM,
            },
        }

    monkeypatch.setattr("app.routers.hint.generate_hint_bundle", fake_bundle)

    levels = []
    for _ in range(3):
        response = client.post("/api/hint", json={"submission_id": submit["submission_id"]})
        assert response.status_code == 200
        levels.append(response.json()["level"])

    assert levels == [1, 2, 3]
    assert calls == 1
    saved = db_session.get(Submission, submit["submission_id"])
    assert saved.hint_level == 3
