"""
POST /api/run — Execute code and return stdout/stderr.

Python: real subprocess execution with 10-second timeout.
Other languages: descriptive error (compiler not available in Phase 1).
"""

import subprocess
import sys
import time
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth import get_current_user
from app.models.user import User
from app.engines.executor import run_code as engine_run_code

logger = logging.getLogger(__name__)

router = APIRouter()


class RunRequest(BaseModel):
    code: str
    language: str


class RunResponse(BaseModel):
    success: bool
    output: str
    exec_time: str
    language: str


@router.post(
    "/run",
    response_model=RunResponse,
    summary="Execute code and return output",
    description=(
        "Runs the submitted code directly. "
        "Python is executed via subprocess. "
        "Other languages require a compiler — coming in Phase 2."
    ),
)
def run_code(
    payload: RunRequest,
    current_user: User = Depends(get_current_user)
) -> RunResponse:
    """POST /api/run"""
    lang = payload.language.lower()
    logger.info("Running code (%d chars) for language: %s", len(payload.code), lang)

    try:
        result = engine_run_code(user_code=payload.code, language=lang)
        
        success = result.get("exit_code") == 0 and not result.get("timed_out")
        
        if result.get("timed_out"):
            output = result.get("error_message") or "Execution timed out."
        elif not success:
            output = result.get("error_message") or "Process exited with a non-zero status."
        else:
            output = result.get("actual_output") or "(program produced no output)"
            
        elapsed = f"{result.get('execution_time_ms', 0) / 1000:.3f}s"
        
        return RunResponse(
            success=success,
            output=output,
            exec_time=elapsed,
            language=lang,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("run_code error: %s", exc, exc_info=True)
        return RunResponse(
            success=False,
            output=f"Internal execution error: {exc}",
            exec_time="—",
            language=lang,
        )
