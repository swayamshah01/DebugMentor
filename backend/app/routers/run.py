"""
POST /api/run — Execute code and return stdout/stderr.

Python: real subprocess execution with 10-second timeout.
Other languages: descriptive error (compiler not available in Phase 1).
"""

import subprocess
import sys
import time
import logging

from fastapi import APIRouter
from pydantic import BaseModel

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
def run_code(payload: RunRequest) -> RunResponse:
    """POST /api/run"""
    lang = payload.language.lower()

    if lang != "python":
        return RunResponse(
            success=False,
            output=(
                f"Runtime execution for {payload.language} requires a compiler.\n"
                "Phase 2 will add sandboxed Docker execution for C++, Java, and JavaScript.\n\n"
                "To test, switch to Python in the language selector."
            ),
            exec_time="—",
            language=payload.language,
        )

    # ── Python: subprocess execution ──────────────────────────────────────────
    logger.info("Running Python code (%d chars)", len(payload.code))
    start = time.monotonic()

    try:
        proc = subprocess.run(
            [sys.executable, "-c", payload.code],
            capture_output=True,
            text=True,
            timeout=10,
        )
        elapsed = f"{time.monotonic() - start:.3f}s"

        if proc.returncode == 0:
            output = proc.stdout or "(program produced no output)"
            return RunResponse(
                success=True,
                output=output,
                exec_time=elapsed,
                language=lang,
            )
        else:
            # Return full stderr so student sees the real traceback
            output = proc.stderr.strip() or "Process exited with a non-zero status."
            return RunResponse(
                success=False,
                output=output,
                exec_time=elapsed,
                language=lang,
            )

    except subprocess.TimeoutExpired:
        return RunResponse(
            success=False,
            output="Execution timed out — your code ran for more than 10 seconds.\nCheck for infinite loops or unbounded recursion.",
            exec_time="10.000s",
            language=lang,
        )
    except Exception as exc:
        logger.error("run_code error: %s", exc, exc_info=True)
        return RunResponse(
            success=False,
            output=f"Internal execution error: {exc}",
            exec_time="—",
            language=lang,
        )
