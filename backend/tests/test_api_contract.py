import uuid

from app.models.mistake import Mistake
from app.models.pattern import Pattern
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.testcase import TestCase
from app.models.user import User


def make_curated_problem(db_session, user=None):
    suffix = uuid.uuid4().hex[:8]
    pattern = Pattern(
        name=f"Contract Pattern {suffix}",
        slug=f"contract-pattern-{suffix}",
        description="Contract test pattern",
        icon_name="🧪",
        order_index=1,
    )
    db_session.add(pattern)
    db_session.commit()

    problem = Problem(
        pattern_id=pattern.id,
        title=f"Contract Problem {suffix}",
        slug=f"contract-problem-{suffix}",
        difficulty="easy",
        short_description="Contract problem",
        statement="Return n + 1",
        constraints_text="Use a function",
        examples_json=[{"input": "7", "output": "8", "explanation": "increment"}],
        starter_code_json={"python": "def solve(n):\n    return n + 1"},
        reference_solution_json={"python": "def solve(n):\n    return n + 1"},
        order_index=1,
        is_active=True,
    )
    db_session.add(problem)
    db_session.commit()

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
        label="Hidden",
        input="41",
        expected_output="42",
        is_hidden=True,
        order_index=2,
    )
    db_session.add_all([visible, hidden])
    db_session.commit()

    if user is None:
        user = User(
            username=f"contract_user_{suffix}",
            email=f"contract_user_{suffix}@example.com",
            hashed_password="hashed-password",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

    return {
        "pattern": pattern,
        "problem": problem,
        "visible": visible,
        "hidden": hidden,
        "user": user,
    }


def test_patterns_endpoint_returns_expected_structure(api_client, db_session):
    client, _ = api_client
    data = make_curated_problem(db_session)

    response = client.get("/api/patterns")

    assert response.status_code == 200
    payload = response.json()
    assert "patterns" in payload
    assert isinstance(payload["patterns"], list)
    assert any(item["id"] == data["pattern"].id for item in payload["patterns"])
    pattern_item = next(item for item in payload["patterns"] if item["id"] == data["pattern"].id)
    assert pattern_item["name"] == data["pattern"].name
    assert pattern_item["problem_count"] == 1
    assert "icon" in pattern_item
    assert "icon_name" in pattern_item


def test_pattern_problems_endpoint_returns_problem_list(api_client, db_session):
    client, _ = api_client
    data = make_curated_problem(db_session)

    response = client.get(f"/api/patterns/{data['pattern'].id}/problems")

    assert response.status_code == 200
    payload = response.json()
    assert payload["pattern"]["id"] == data["pattern"].id
    assert payload["pattern"]["name"] == data["pattern"].name
    assert len(payload["problems"]) == 1
    assert payload["problems"][0]["id"] == data["problem"].id
    assert payload["problems"][0]["title"] == data["problem"].title


def test_problem_detail_excludes_hidden_test_cases(api_client, db_session):
    client, _ = api_client
    data = make_curated_problem(db_session)

    response = client.get(f"/api/problems/{data['problem'].id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == data["problem"].id
    assert payload["starter_code"] == data["problem"].starter_code_json["python"]
    assert payload["starter_code_map"]["python"] == data["problem"].starter_code_json["python"]
    assert "python" in payload["available_languages"]
    assert len(payload["test_cases"]) == 1
    assert payload["test_cases"][0]["label"] == data["visible"].label
    assert all(case["label"] != data["hidden"].label for case in payload["test_cases"])


def test_run_endpoint_is_non_persistent(api_client, db_session):
    client, set_current_user = api_client
    data = make_curated_problem(db_session)
    set_current_user(data["user"])

    before = db_session.query(Submission).count()
    response = client.post(
        "/api/run",
        json={
            "code": "def solve(n):\n    return n + 1",
            "language": "python",
            "problem_id": data["problem"].id,
        },
    )
    after = db_session.query(Submission).count()

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["passed_tests"] == 1
    assert payload["failed_tests"] == 0
    assert "Passed all visible tests" in payload["output"]
    assert before == after


def test_run_endpoint_executes_function_style_curated_problem(api_client, db_session):
    client, set_current_user = api_client
    data = make_curated_problem(db_session)
    set_current_user(data["user"])

    response = client.post(
        "/api/run",
        json={
            "code": "def solve(n):\n    return n + 1",
            "language": "python",
            "problem_id": data["problem"].id,
            "test_case_id": data["visible"].id,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["passed_tests"] == 1
    assert payload["test_results"][0]["actual_output"].strip() == "8"


def test_run_endpoint_fails_empty_function_against_visible_tests(api_client, db_session):
    client, set_current_user = api_client
    data = make_curated_problem(db_session)
    set_current_user(data["user"])

    response = client.post(
        "/api/run",
        json={
            "code": "def solve(n):\n    pass",
            "language": "python",
            "problem_id": data["problem"].id,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is False
    assert payload["failed_tests"] == 1
    assert payload["dominant_failure_type"] in {"WRONG_OUTPUT", "EMPTY_OUTPUT"}


def test_run_rejects_blank_code(api_client, db_session):
    client, set_current_user = api_client
    data = make_curated_problem(db_session)
    set_current_user(data["user"])

    response = client.post(
        "/api/run",
        json={
            "code": "   \n\t",
            "language": "python",
            "problem_id": data["problem"].id,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Write some code before running it."


def test_submit_requires_problem_id(api_client, db_session):
    client, set_current_user = api_client
    data = make_curated_problem(db_session)
    set_current_user(data["user"])

    before = db_session.query(Submission).count()
    response = client.post(
        "/api/submit",
        json={
            "code": "def solve(n):\n    return n + 1",
            "language": "python",
        },
    )
    after = db_session.query(Submission).count()

    assert response.status_code == 400
    assert response.json()["detail"] == "problem_id is required for curated submissions"
    assert before == after


def test_submit_rejects_invalid_problem_id(api_client, db_session):
    client, set_current_user = api_client
    data = make_curated_problem(db_session)
    set_current_user(data["user"])

    before = db_session.query(Submission).count()
    response = client.post(
        "/api/submit",
        json={
            "code": "def solve(n):\n    return n + 1",
            "language": "python",
            "problem_id": 999999,
        },
    )
    after = db_session.query(Submission).count()

    assert response.status_code == 404
    assert response.json()["detail"] == "Problem not found"
    assert before == after


def test_submit_rejects_blank_code(api_client, db_session):
    client, set_current_user = api_client
    data = make_curated_problem(db_session)
    set_current_user(data["user"])

    before = db_session.query(Submission).count()
    response = client.post(
        "/api/submit",
        json={
            "code": "   ",
            "language": "python",
            "problem_id": data["problem"].id,
        },
    )
    after = db_session.query(Submission).count()

    assert response.status_code == 400
    assert response.json()["detail"] == "Write some code before submitting it."
    assert before == after


def test_submit_persists_submission(api_client, db_session):
    client, set_current_user = api_client
    data = make_curated_problem(db_session)
    set_current_user(data["user"])

    before = db_session.query(Submission).count()
    response = client.post(
        "/api/submit",
        json={
            "code": "def solve(n):\n    return n + 1",
            "language": "python",
            "problem_id": data["problem"].id,
        },
    )
    after = db_session.query(Submission).count()

    assert response.status_code == 201
    payload = response.json()
    assert payload["problem_id"] == data["problem"].id
    assert payload["status"] == "passed"
    assert after == before + 1


def test_profile_endpoint_returns_expected_structure_for_current_user(api_client, db_session):
    client, set_current_user = api_client
    data = make_curated_problem(db_session)
    set_current_user(data["user"])

    pass_response = client.post(
        "/api/submit",
        json={
            "code": "def solve(n):\n    return n + 1",
            "language": "python",
            "problem_id": data["problem"].id,
        },
    )
    fail_response = client.post(
        "/api/submit",
        json={
            "code": "def solve(n):\n    return n",
            "language": "python",
            "problem_id": data["problem"].id,
        },
    )

    assert pass_response.status_code == 201
    assert fail_response.status_code == 201

    response = client.get(f"/api/profile/{data['user'].id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["user_id"] == data["user"].id
    assert payload["stats"]["total_submissions"] >= 2
    assert "submission_history" in payload
    assert "weak_patterns" in payload
    assert "recommendations" in payload
    assert "readiness_snapshot" in payload
    assert payload["submission_history"][0]["problem_title"] == data["problem"].title
    assert payload["readiness_snapshot"]["recent_streak"] >= 0


def test_profile_endpoint_rejects_other_user(api_client, db_session):
    client, set_current_user = api_client
    data = make_curated_problem(db_session)
    other_user = User(
        username=f"other_user_{uuid.uuid4().hex[:8]}",
        email=f"other_user_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="hashed-password",
    )
    db_session.add(other_user)
    db_session.commit()

    set_current_user(other_user)
    response = client.get(f"/api/profile/{data['user'].id}")

    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden: can only view own profile"
