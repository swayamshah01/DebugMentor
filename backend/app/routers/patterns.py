"""Read-only endpoints for the curated practice catalog."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.pattern import Pattern
from app.models.problem import Problem
from app.models.testcase import TestCase


router = APIRouter(prefix="/api")


@router.get("/patterns")
def get_patterns(db: Session = Depends(get_db)) -> dict:
    rows = (
        db.query(Pattern, func.count(Problem.id).label("problem_count"))
        .outerjoin(
            Problem,
            and_(Problem.pattern_id == Pattern.id, Problem.is_active.is_(True)),
        )
        .group_by(Pattern.id)
        .order_by(Pattern.order_index)
        .all()
    )
    return {
        "patterns": [
            {
                "id": pattern.id,
                "name": pattern.name,
                "slug": pattern.slug,
                "description": pattern.description,
                "icon_name": pattern.icon_name,
                "problem_count": problem_count,
            }
            for pattern, problem_count in rows
        ]
    }


@router.get("/patterns/{pattern_id}/problems")
def get_pattern_problems(pattern_id: int, db: Session = Depends(get_db)) -> dict:
    pattern = db.query(Pattern).filter(Pattern.id == pattern_id).first()
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found.")

    problems = (
        db.query(Problem)
        .filter(Problem.pattern_id == pattern_id, Problem.is_active.is_(True))
        .order_by(Problem.order_index)
        .all()
    )
    return {
        "pattern": {
            "id": pattern.id,
            "name": pattern.name,
            "slug": pattern.slug,
            "description": pattern.description,
        },
        "problems": [
            {
                "id": problem.id,
                "title": problem.title,
                "slug": problem.slug,
                "difficulty": problem.difficulty,
                "short_description": problem.short_description,
                "order_index": problem.order_index,
            }
            for problem in problems
        ],
    }


@router.get("/problems/{problem_id}")
def get_problem_detail(problem_id: int, db: Session = Depends(get_db)) -> dict:
    problem = (
        db.query(Problem)
        .options(joinedload(Problem.pattern))
        .filter(Problem.id == problem_id, Problem.is_active.is_(True))
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found.")

    visible_cases = (
        db.query(TestCase)
        .filter(TestCase.problem_id == problem_id, TestCase.is_hidden.is_(False))
        .order_by(TestCase.order_index)
        .all()
    )
    starter_code = problem.starter_code_json or {}

    return {
        "id": problem.id,
        "title": problem.title,
        "slug": problem.slug,
        "difficulty": problem.difficulty,
        "short_description": problem.short_description,
        "statement": problem.statement,
        "input_format": problem.input_format,
        "output_format": problem.output_format,
        "constraints": problem.constraints_text,
        "examples": problem.examples_json or [],
        "starter_code_map": starter_code,
        "available_languages": [
            language
            for language in ("python", "javascript", "java", "cpp")
            if language in starter_code
        ],
        "pattern": {
            "id": problem.pattern.id,
            "name": problem.pattern.name,
            "slug": problem.pattern.slug,
            "description": problem.pattern.description,
        },
        "test_cases": [
            {
                "id": case.id,
                "label": case.label,
                "input": case.input,
                "expected_output": case.expected_output,
                "order_index": case.order_index,
            }
            for case in visible_cases
        ],
    }
