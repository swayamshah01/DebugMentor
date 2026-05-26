"""Official curated submission pipeline.

`POST /api/submit` is the graded action for a curated problem. It must
receive a valid `problem_id`, executes against the stored official test
cases for that problem, persists the submission, updates learning state,
and returns structured hints/results.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.submission import Submission
from app.models.problem import Problem
from app.schemas.submission import SubmissionCreate, SubmissionResponse
from app.engines.ast_analyzer import analyze as ast_analyze
from app.engines.llm_layer import generate_hints
from app.auth import get_current_user
from app.models.user import User
from app.models.mistake import Mistake
from app.services.problem_evaluator import (
    evaluate_problem_submission,
    build_problem_context,
    classify_hint_intent,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/submit",
    response_model=SubmissionResponse,
    status_code=201,
    summary="Submit code for full Phase 2 analysis",
    description=(
        "Accepts a code submission, runs AST analysis, generates edge-case "
        "tests, executes them, classifies failures, persists to the database, "
        "and returns a structured response."
    ),
)
def submit_code(
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionResponse:
    """
    POST /api/submit — Phase 2 Pipeline

    Flow
    ----
    1. AST analysis (syntax error → return immediately)
    2. Generate edge-case test inputs
    3. Execute each test via the Phase 1 executor
    4. Classify failures with the failure detector
    5. Persist to DB (ast_findings, test_results as JSON)
    6. Return structured response (hints = null)
    """
    logger.info(
        "Submission: user_id=%s lang=%s code_len=%d problem_id=%s",
        current_user.id, payload.language, len(payload.code), payload.problem_id,
    )

    if payload.problem_id is None:
        raise HTTPException(status_code=400, detail="problem_id is required for curated submissions")

    problem = db.query(Problem).filter(
        Problem.id == payload.problem_id,
        Problem.is_active.is_(True),
    ).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # ── Step 1: AST Analysis ──────────────────────────────────────────────────
    ast_issues = ast_analyze(payload.code, payload.language)

    # If a syntax error was found, return immediately with no execution
    has_syntax_error = any(i["type"] == "syntax_error" for i in ast_issues)
    if has_syntax_error:
        failure_report = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "has_failures": True,
            "dominant_failure_type": "SYNTAX_ERROR",
            "error_category": "syntax_error",
            "failure_summary": "Code has a syntax error and cannot be executed.",
            "test_results": [],
        }

        try:
            submission = Submission(
                user_id      = current_user.id,
                code         = payload.code,
                language     = payload.language,
                status       = "failed",
                hint_level   = 0,
                feedback     = "",
                ast_findings = ast_issues,
                test_results = failure_report,
                problem_id   = payload.problem_id,
            )
            db.add(submission)
            db.commit()
            db.refresh(submission)
        except Exception as exc:
            db.rollback()
            logger.error("DB write failed: %s", exc, exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to save submission: {exc}")

        return SubmissionResponse(
            id             = submission.id,
            user_id        = submission.user_id,
            code           = submission.code,
            language       = submission.language,
            submitted_at   = submission.submitted_at,
            hint_level     = submission.hint_level,
            status         = submission.status,
            feedback       = submission.feedback,
            ast_issues     = ast_issues,
            failure_report = failure_report,
            hints          = None,
            problem_id     = submission.problem_id,
        )

    # ── Step 2/3/4: Evaluate against stored problem tests when possible ──────
    raw_results, failure_report, test_cases = evaluate_problem_submission(
        problem=problem,
        code=payload.code,
        language=payload.language,
        db=db,
    )

    # ── Step 5: Generate AI Hints (Phase 3) ───────────────────────────────────
    hint_intent = classify_hint_intent(failure_report, ast_issues)
    problem_context = build_problem_context(problem, failure_report.get("test_results", []))
    hints_payload = generate_hints(
        code=payload.code,
        language=payload.language,
        failure_report=failure_report,
        ast_issues=ast_issues,
        user_id=current_user.id,
        db=db,
        problem_desc=problem_context,
        problem_id=problem.id,
        hint_intent=hint_intent,
        pattern_name=problem.pattern.name if problem.pattern else None,
        problem_title=problem.title,
        constraints_text=problem.constraints_text,
    )
    hints_payload["hint_intent"] = hint_intent
    hints_payload["problem_title"] = problem.title
    hints_payload["pattern_name"] = problem.pattern.name if problem.pattern else None
    if isinstance(problem.reference_solution_json, dict):
        solution_code = problem.reference_solution_json.get(payload.language.lower())
        if solution_code:
            hints_payload["solution_code"] = solution_code

    # ── Step 6: Determine status and persist ──────────────────────────────────
    db_status = "passed" if not failure_report["has_failures"] and not ast_issues else "failed"

    try:
        submission = Submission(
            user_id      = current_user.id,
            code         = payload.code,
            language     = payload.language,
            status       = db_status,
            hint_level   = 0,
            feedback     = hints_payload.get("explanation", ""),
            ast_findings = ast_issues,
            test_results = failure_report,
            hints        = hints_payload,
            problem_id   = payload.problem_id,
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        logger.info("Submission saved: id=%s status=%s", submission.id, submission.status)
    except Exception as exc:
        db.rollback()
        logger.error("DB write failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save submission: {exc}")

    # ── Step 8: Record dominant mistake for learning profile (Phase 4) ──────────
    try:
        # Prefer AST-based classifications
        mistake_type = None
        if ast_issues:
            priority = [
                'syntax_error', 'infinite_loop', 'unused_variable',
                'missing_base_case', 'mutable_default', 'off_by_one'
            ]
            found = None
            for p in priority:
                if any(i.get('type') == p for i in ast_issues):
                    found = p
                    break
            mistake_type = found or 'static_analysis_error'
        else:
            # Map dominant failure types
            dom = failure_report.get('dominant_failure_type')
            mapping = {
                'WRONG_OUTPUT': 'wrong_output',
                'RUNTIME_ERROR': 'runtime_error',
                'TIMEOUT': 'timeout',
                'EMPTY_OUTPUT': 'empty_output',
            }
            mistake_type = mapping.get(dom)

        if mistake_type:
            # Avoid duplicates for the same submission
            exists = db.query(Mistake).filter(Mistake.submission_id == submission.id).first()
            if not exists:
                desc = failure_report.get('failure_summary') or ''
                if ast_issues and isinstance(ast_issues, list) and len(ast_issues) > 0:
                    desc = ast_issues[0].get('message', desc)

                ml = Mistake(
                    user_id=submission.user_id,
                    submission_id=submission.id,
                    mistake_type=mistake_type,
                    description=desc or ''
                )
                db.add(ml)
                db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning("Failed to log mistake for submission %s: %s", submission.id, exc)

    # ── Step 7: Return structured response ────────────────────────────────────
    return SubmissionResponse(
        id             = submission.id,
        user_id        = submission.user_id,
        code           = submission.code,
        language       = submission.language,
        submitted_at   = submission.submitted_at,
        hint_level     = submission.hint_level,
        status         = submission.status,
        feedback       = submission.feedback,
        ast_issues     = ast_issues,
        failure_report = failure_report,
        hints          = hints_payload,
        problem_id     = submission.problem_id,
    )
