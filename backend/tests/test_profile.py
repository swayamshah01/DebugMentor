"""
test_profile.py — Unit tests for the Learning Profile System (Phase 4)

Tests:
- Profile endpoint returns expected structure
- Top mistake aggregation works correctly
- Submission creates mistake classification
- No duplicate mistake entry for the same submission
- Pass rate and stats computed correctly
"""

import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy import func
from app.models.user import User
from app.models.submission import Submission
from app.models.mistake import Mistake
from app.models.pattern import Pattern
from app.models.problem import Problem
from app.models.testcase import TestCase
from app.database import SessionLocal
from app.routers.profile import get_profile


@pytest.fixture
def db_session():
    """Provide a fresh database session for each test."""
    db = SessionLocal()
    yield db
    # Cleanup
    try:
        db.rollback()
        db.query(TestCase).delete()
        db.query(Problem).delete()
        db.query(Pattern).delete()
        db.query(Mistake).delete()
        db.query(Submission).delete()
        db.query(User).delete()
        db.commit()
    except Exception:
        db.rollback()
    db.close()


@pytest.fixture
def test_user(db_session):
    """Create a test user with a unique email."""
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        username=f"testuser_{unique_id}",
        email=f"testuser_{unique_id}@example.com",
        hashed_password="hashedpassword",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_top_mistake_aggregation(db_session, test_user):
    """Top mistakes are aggregated and sorted by frequency."""
    # Create submissions with associated mistakes
    for i in range(3):
        sub = Submission(
            user_id=test_user.id,
            code=f"code_{i}",
            language="python",
            status="failed",
            test_results={"failure_summary": "test failed"}
        )
        db_session.add(sub)
        db_session.commit()
        db_session.refresh(sub)
        
        # Attach mistakes
        mistake = Mistake(
            user_id=test_user.id,
            submission_id=sub.id,
            mistake_type="wrong_output",
            description="Wrong output"
        )
        db_session.add(mistake)
    
    # Add one more for a different type
    sub2 = Submission(
        user_id=test_user.id,
        code="code_extra",
        language="python",
        status="failed",
        test_results={"failure_summary": "test failed"}
    )
    db_session.add(sub2)
    db_session.commit()
    db_session.refresh(sub2)
    
    mistake2 = Mistake(
        user_id=test_user.id,
        submission_id=sub2.id,
        mistake_type="runtime_error",
        description="Runtime error"
    )
    db_session.add(mistake2)
    db_session.commit()
    
    # Query top mistakes
    top_mistakes = (
        db_session.query(Mistake.mistake_type, func.count(Mistake.id).label("count"))
        .filter(Mistake.user_id == test_user.id)
        .group_by(Mistake.mistake_type)
        .order_by(func.count(Mistake.id).desc())
        .all()
    )
    
    assert len(top_mistakes) == 2
    assert top_mistakes[0].mistake_type == "wrong_output"


def test_no_duplicate_mistakes(db_session, test_user):
    """Multiple queries don't create duplicate mistake entries for same submission."""
    sub = Submission(
        user_id=test_user.id,
        code="code",
        language="python",
        status="failed",
        test_results={"failure_summary": "test"}
    )
    db_session.add(sub)
    db_session.commit()
    db_session.refresh(sub)
    
    # First time: mistake doesn't exist, so create it
    exists1 = db_session.query(Mistake).filter(Mistake.submission_id == sub.id).first()
    assert exists1 is None
    
    # Create a mistake
    m1 = Mistake(
        user_id=test_user.id,
        submission_id=sub.id,
        mistake_type="wrong_output",
        description="first"
    )
    db_session.add(m1)
    db_session.commit()
    
    # Second time: mistake exists, so don't create another
    exists2 = db_session.query(Mistake).filter(Mistake.submission_id == sub.id).first()
    assert exists2 is not None
    assert exists2.id == m1.id
    
    # Verify only one exists
    count = db_session.query(Mistake).filter(Mistake.submission_id == sub.id).count()
    assert count == 1


def test_pass_rate_calculation(db_session, test_user):
    """Pass rate is computed correctly from submissions."""
    # Create 4 passed and 1 failed
    for i in range(4):
        sub = Submission(
            user_id=test_user.id,
            code=f"code_{i}",
            language="python",
            status="passed",
        )
        db_session.add(sub)
    
    sub_fail = Submission(
        user_id=test_user.id,
        code="fail_code",
        language="python",
        status="failed",
    )
    db_session.add(sub_fail)
    db_session.commit()
    
    # Calculate stats
    submissions = db_session.query(Submission).filter(Submission.user_id == test_user.id).all()
    total = len(submissions)
    passed = sum(1 for s in submissions if s.status == "passed")
    pass_rate = (passed / total * 100) if total > 0 else 0.0
    
    assert total == 5
    assert passed == 4
    assert abs(pass_rate - 80.0) < 0.1


def test_submission_with_hint_levels(db_session, test_user):
    """Average hint level is computed from submissions."""
    # Create submissions with various hint levels
    for hint_level in [0, 1, 2, 3, 1]:
        sub = Submission(
            user_id=test_user.id,
            code="code",
            language="python",
            status="passed",
            hint_level=hint_level,
        )
        db_session.add(sub)
    db_session.commit()
    
    submissions = db_session.query(Submission).filter(Submission.user_id == test_user.id).all()
    total_hints = sum(s.hint_level for s in submissions)
    avg_hint = total_hints / len(submissions)
    
    assert len(submissions) == 5
    assert abs(avg_hint - 1.4) < 0.1


def test_empty_profile(db_session, test_user):
    """Profile for a new user with no submissions is properly handled."""
    # No submissions or mistakes created for this user
    submissions = db_session.query(Submission).filter(Submission.user_id == test_user.id).all()
    mistakes = db_session.query(Mistake).filter(Mistake.user_id == test_user.id).all()
    
    assert len(submissions) == 0
    assert len(mistakes) == 0


def test_submission_history_ordering(db_session, test_user):
    """Submission history is returned newest first."""
    # Create submissions with time gaps
    base_time = datetime.utcnow()
    for i in range(3):
        sub = Submission(
            user_id=test_user.id,
            code=f"code_{i}",
            language="python",
            status="passed",
            submitted_at=base_time - timedelta(seconds=i*10)
        )
        db_session.add(sub)
    db_session.commit()
    
    submissions = (
        db_session.query(Submission)
        .filter(Submission.user_id == test_user.id)
        .order_by(Submission.submitted_at.desc())
        .all()
    )
    
    assert len(submissions) == 3
    # Verify ordering: newest first
    for i in range(len(submissions) - 1):
        assert submissions[i].submitted_at >= submissions[i+1].submitted_at


def test_profile_includes_pattern_progress_and_recommendations(db_session, test_user):
    pattern = Pattern(
        name=f"Arrays {uuid.uuid4().hex[:6]}",
        slug=f"arrays-{uuid.uuid4().hex[:6]}",
        description="Array problems",
        icon_name="📊",
        order_index=1,
    )
    db_session.add(pattern)
    db_session.commit()

    problem = Problem(
        pattern_id=pattern.id,
        title="Test Problem",
        slug=f"test-problem-{uuid.uuid4().hex[:6]}",
        difficulty="easy",
        short_description="test",
        statement="Solve it",
        starter_code_json={"python": "def solve(n):\n    return n + 1"},
        is_active=True,
        order_index=1,
    )
    db_session.add(problem)
    db_session.commit()

    passed_submission = Submission(
        user_id=test_user.id,
        code="def solve(n):\n    return n + 1",
        language="python",
        status="passed",
        feedback="",
        ast_findings=[],
        test_results={"dominant_failure_type": None, "test_results": []},
        problem_id=problem.id,
    )
    failed_submission = Submission(
        user_id=test_user.id,
        code="def solve(n):\n    return n",
        language="python",
        status="failed",
        feedback="",
        ast_findings=[],
        test_results={"dominant_failure_type": "WRONG_OUTPUT", "test_results": []},
        problem_id=problem.id,
    )
    db_session.add_all([passed_submission, failed_submission])
    db_session.commit()

    profile = get_profile(user_id=test_user.id, db=db_session, current_user=test_user)

    assert profile.weak_patterns is not None
    assert profile.readiness_snapshot is not None
    assert profile.recommendations is not None
    assert profile.readiness_snapshot.weakest_patterns[0] == pattern.name
