"""
Patterns and Problems endpoints for DSA interview prep.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.pattern import Pattern
from app.models.problem import Problem
from app.models.testcase import TestCase

router = APIRouter(prefix="/api", tags=["patterns"])


class PatternSummary:
    """Pattern with problem count."""
    def __init__(self, id: int, name: str, slug: str, description: str, icon_name: str, problem_count: int):
        self.id = id
        self.name = name
        self.slug = slug
        self.description = description
        self.icon_name = icon_name
        self.problem_count = problem_count


class TestCaseResponse:
    """Visible test case (hidden ones not returned)."""
    def __init__(self, id: int, label: str, input: str, expected_output: str, order_index: int):
        self.id = id
        self.label = label
        self.input = input
        self.expected_output = expected_output
        self.order_index = order_index


class ProblemListItem:
    """Problem summary for listing."""
    def __init__(self, id: int, title: str, slug: str, difficulty: str, short_description: str, order_index: int):
        self.id = id
        self.title = title
        self.slug = slug
        self.difficulty = difficulty
        self.short_description = short_description
        self.order_index = order_index


class ProblemDetail:
    """Full problem with visible test cases and starter code."""
    def __init__(self, problem: Problem, test_cases: List):
        self.id = problem.id
        self.title = problem.title
        self.slug = problem.slug
        self.difficulty = problem.difficulty
        self.statement = problem.statement
        self.constraints = problem.constraints_text
        self.examples = problem.examples_json
        self.starter_code = problem.starter_code_json.get("python", "") if problem.starter_code_json else ""
        self.starter_code_map = problem.starter_code_json or {}
        self.available_languages = sorted(list((problem.starter_code_json or {}).keys()))
        self.test_cases = test_cases
        self.order_index = problem.order_index


@router.get("/patterns")
def get_patterns(db: Session = Depends(get_db)) -> dict:
    """
    Get all patterns with problem counts.
    Used for frontend pattern navigation sidebar.
    """
    patterns = db.query(Pattern).order_by(Pattern.order_index).all()
    result = []
    for p in patterns:
        problem_count = db.query(Problem).filter(Problem.pattern_id == p.id, Problem.is_active == True).count()
        result.append({
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "description": p.description,
            "icon": p.icon_name,
            "icon_name": p.icon_name,
            "problem_count": problem_count
        })
    return {"patterns": result}


@router.get("/patterns/{pattern_id}/problems")
def get_pattern_problems(pattern_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Get all problems for a specific pattern.
    Returns problem list items (not full details).
    """
    pattern = db.query(Pattern).filter(Pattern.id == pattern_id).first()
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    
    problems = db.query(Problem).filter(
        Problem.pattern_id == pattern_id,
        Problem.is_active == True
    ).order_by(Problem.order_index).all()
    
    problem_list = []
    for p in problems:
        problem_list.append({
            "id": p.id,
            "title": p.title,
            "slug": p.slug,
            "difficulty": p.difficulty,
            "short_description": p.short_description,
            "order_index": p.order_index
        })
    
    return {
        "pattern": {
            "id": pattern.id,
            "name": pattern.name,
            "slug": pattern.slug,
            "description": pattern.description,
            "icon": pattern.icon_name
        },
        "problems": problem_list
    }


@router.get("/problems/{problem_id}")
def get_problem_detail(problem_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Get full problem detail with visible test cases and starter code.
    Hidden test cases are NOT returned (those are for backend verification).
    """
    problem = db.query(Problem).filter(
        Problem.id == problem_id,
        Problem.is_active == True
    ).first()
    
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    # Get only visible test cases
    test_cases = db.query(TestCase).filter(
        TestCase.problem_id == problem_id,
        TestCase.is_hidden == False
    ).order_by(TestCase.order_index).all()
    
    test_cases_list = []
    for tc in test_cases:
        test_cases_list.append({
            "id": tc.id,
            "label": tc.label,
            "input": tc.input,
            "expected_output": tc.expected_output,
            "order_index": tc.order_index
        })
    
    return {
        "id": problem.id,
        "title": problem.title,
        "slug": problem.slug,
        "difficulty": problem.difficulty,
        "pattern": {
            "id": problem.pattern.id,
            "name": problem.pattern.name,
            "slug": problem.pattern.slug,
            "description": problem.pattern.description,
            "icon_name": problem.pattern.icon_name,
        } if problem.pattern else None,
        "statement": problem.statement,
        "constraints": problem.constraints_text,
        "examples": problem.examples_json,
        "starter_code": problem.starter_code_json.get("python", "") if problem.starter_code_json else "",
        "starter_code_map": problem.starter_code_json or {},
        "available_languages": sorted(list((problem.starter_code_json or {}).keys())),
        "test_cases": test_cases_list
    }
