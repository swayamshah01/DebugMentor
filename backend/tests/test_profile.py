from app.models.pattern import Pattern
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User


def test_profile_summarizes_submission_progress(api_client, db_session):
    client, authenticate_as = api_client
    user = User(username="profile_user", email="profile@example.com", hashed_password="unused")
    pattern = Pattern(name="Arrays", slug="profile-arrays", order_index=1)
    db_session.add_all([user, pattern])
    db_session.flush()
    problem = Problem(
        pattern_id=pattern.id,
        title="Profile Problem",
        slug="profile-problem",
        difficulty="easy",
        statement="Solve it.",
        order_index=1,
    )
    db_session.add(problem)
    db_session.flush()
    db_session.add_all(
        [
            Submission(
                user_id=user.id,
                problem_id=problem.id,
                code="print(1)",
                language="python",
                status="passed",
                test_results={"dominant_failure_type": None, "test_results": []},
            ),
            Submission(
                user_id=user.id,
                problem_id=problem.id,
                code="print(0)",
                language="python",
                status="failed",
                test_results={"dominant_failure_type": "WRONG_OUTPUT", "test_results": []},
            ),
        ]
    )
    db_session.commit()
    authenticate_as(user)

    response = client.get(f"/api/profile/{user.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["stats"]["total_submissions"] == 2
    assert payload["stats"]["passed_submissions"] == 1
    assert payload["submission_history"][0]["problem_title"] == "Profile Problem"


def test_profile_rejects_access_to_another_user(api_client, db_session):
    client, authenticate_as = api_client
    owner = User(username="owner", email="owner@example.com", hashed_password="unused")
    visitor = User(username="visitor", email="visitor@example.com", hashed_password="unused")
    db_session.add_all([owner, visitor])
    db_session.commit()
    authenticate_as(visitor)

    response = client.get(f"/api/profile/{owner.id}")

    assert response.status_code == 403
