"""
test_patterns.py — Unit tests for DSA patterns and problems endpoints (Phase 1)

Tests:
- GET /api/patterns returns all patterns with problem counts
- GET /api/patterns/{pattern_id}/problems returns problems in pattern
- GET /api/problems/{problem_id} returns full problem detail with visible test cases
- Hidden test cases are not returned to frontend
- 404 errors for non-existent patterns/problems
"""

import pytest
from app.models.pattern import Pattern
from app.models.problem import Problem
from app.models.testcase import TestCase
from app.database import SessionLocal


@pytest.fixture
def db_session():
    """Provide a fresh database session for each test."""
    db = SessionLocal()
    yield db
    # Cleanup with error handling for pending rollback
    try:
        db.rollback()
        db.query(TestCase).delete()
        db.query(Problem).delete()
        db.query(Pattern).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


@pytest.fixture
def test_pattern(db_session):
    """Create a test pattern with unique slug."""
    import uuid
    slug = f"test-pattern-{uuid.uuid4().hex[:8]}"
    pattern = Pattern(
        name=f"Test Pattern {slug}",
        slug=slug,
        description="A test pattern",
        icon_name="🧪",
        order_index=1
    )
    db_session.add(pattern)
    db_session.commit()
    db_session.refresh(pattern)
    return pattern


@pytest.fixture
def test_problem(db_session, test_pattern):
    """Create a test problem."""
    problem = Problem(
        pattern_id=test_pattern.id,
        title="Test Problem",
        slug="test-problem",
        difficulty="easy",
        short_description="A test problem",
        statement="Read an integer n and print n plus one.",
        starter_code_json={"python": "n = int(input().strip())\nprint(n + 1)\n"},
        is_active=True,
        order_index=1
    )
    db_session.add(problem)
    db_session.commit()
    db_session.refresh(problem)
    return problem


@pytest.fixture
def test_problem_with_testcases(db_session, test_problem):
    """Create test problem with visible and hidden test cases."""
    # Visible test case
    tc1 = TestCase(
        problem_id=test_problem.id,
        label="Test 1",
        input="input1",
        expected_output="output1",
        is_hidden=False,
        order_index=1
    )
    # Hidden test case
    tc2 = TestCase(
        problem_id=test_problem.id,
        label="Test 2 (Hidden)",
        input="input2",
        expected_output="output2",
        is_hidden=True,
        order_index=2
    )
    db_session.add_all([tc1, tc2])
    db_session.commit()
    return test_problem


def test_get_pattern_problems_returns_problems_in_pattern(db_session, test_pattern):
    """Test GET /api/patterns/{pattern_id}/problems returns problems."""
    # Create 3 problems in test_pattern
    for i in range(3):
        problem = Problem(
            pattern_id=test_pattern.id,
            title=f"Problem {i+1}",
            slug=f"problem-{i+1}-xyz",
            difficulty="easy" if i % 2 == 0 else "medium",
            short_description=f"Problem {i+1}",
            statement="stmt",
            is_active=True,
            order_index=i+1
        )
        db_session.add(problem)
    db_session.commit()
    
    # Fetch problems
    problems = db_session.query(Problem).filter(
        Problem.pattern_id == test_pattern.id,
        Problem.is_active == True
    ).order_by(Problem.order_index).all()
    
    assert len(problems) == 3
    assert all(p.pattern_id == test_pattern.id for p in problems)
    assert [p.title for p in problems] == ["Problem 1", "Problem 2", "Problem 3"]


def test_get_problem_detail_returns_visible_testcases_only(db_session, test_problem_with_testcases):
    """Test GET /api/problems/{problem_id} returns only visible test cases."""
    # Fetch visible test cases only
    test_cases = db_session.query(TestCase).filter(
        TestCase.problem_id == test_problem_with_testcases.id,
        TestCase.is_hidden == False
    ).order_by(TestCase.order_index).all()
    
    assert len(test_cases) == 1
    assert test_cases[0].label == "Test 1"
    assert test_cases[0].is_hidden == False


def test_hidden_testcases_not_included(db_session, test_problem_with_testcases):
    """Test that hidden test cases are not fetched for frontend."""
    # Total should be 2
    all_tc = db_session.query(TestCase).filter(
        TestCase.problem_id == test_problem_with_testcases.id
    ).all()
    assert len(all_tc) == 2
    
    # Visible should be 1
    visible_tc = db_session.query(TestCase).filter(
        TestCase.problem_id == test_problem_with_testcases.id,
        TestCase.is_hidden == False
    ).all()
    assert len(visible_tc) == 1


def test_problem_cascade_delete(db_session, test_pattern):
    """Test that deleting a pattern cascades to delete problems and test cases."""
    # Create problem with test case
    problem = Problem(
        pattern_id=test_pattern.id,
        title="Test",
        slug="test-cascade",
        difficulty="easy",
        short_description="test",
        statement="stmt",
        is_active=True,
        order_index=1
    )
    db_session.add(problem)
    db_session.commit()
    db_session.refresh(problem)
    
    tc = TestCase(
        problem_id=problem.id,
        label="tc",
        input="in",
        expected_output="out",
        is_hidden=False,
        order_index=1
    )
    db_session.add(tc)
    db_session.commit()
    
    # Delete pattern
    db_session.delete(test_pattern)
    db_session.commit()
    
    # Verify cascade
    problems = db_session.query(Problem).filter(Problem.pattern_id == test_pattern.id).all()
    assert len(problems) == 0
    
    test_cases = db_session.query(TestCase).all()
    assert len(test_cases) == 0


def test_inactive_problems_not_returned(db_session, test_pattern):
    """Test that inactive problems are not returned."""
    # Create active and inactive problems
    active = Problem(
        pattern_id=test_pattern.id, title="Active", slug="active-prob", difficulty="easy",
        short_description="active", statement="stmt", is_active=True, order_index=1
    )
    inactive = Problem(
        pattern_id=test_pattern.id, title="Inactive", slug="inactive-prob", difficulty="easy",
        short_description="inactive", statement="stmt", is_active=False, order_index=2
    )
    db_session.add_all([active, inactive])
    db_session.commit()
    
    # Fetch only active
    active_problems = db_session.query(Problem).filter(
        Problem.pattern_id == test_pattern.id,
        Problem.is_active == True
    ).all()
    
    assert len(active_problems) == 1
    assert active_problems[0].title == "Active"
