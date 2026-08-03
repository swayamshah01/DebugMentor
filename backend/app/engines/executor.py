"""Local multi-language process runner used by the grading service.

The runner accepts a complete console program and sends one test case through
standard input. It is intended for local development; production deployments
must place this process behind a container or another operating-system sandbox.
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from app.config import settings


SUPPORTED_LANGUAGES = {"python", "javascript", "java", "cpp"}
BLOCKED_PYTHON_MODULES = {"ctypes", "multiprocessing", "os", "pathlib", "shutil", "socket", "subprocess"}
MAX_CAPTURED_OUTPUT = 64_000


def _validate_python(code: str) -> str | None:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        modules: list[str] = []
        if isinstance(node, ast.Import):
            modules = [alias.name.split(".", 1)[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules = [node.module.split(".", 1)[0]]

        blocked = next((module for module in modules if module in BLOCKED_PYTHON_MODULES), None)
        if blocked:
            return f"Importing '{blocked}' is not allowed in the local runner."

    return None


def _clean_error(message: str, language: str, stage: str) -> str:
    lines = [line.strip() for line in message.replace("\r", "").splitlines() if line.strip()]
    if not lines:
        return ""

    if language in {"cpp", "java"}:
        error_line = next((line for line in lines if "error:" in line.lower()), None)
        if error_line:
            return re.sub(r"^[A-Za-z]:\\[^:]+(?::\d+){1,2}:\s*", "", error_line)

    if language == "python":
        exception_line = next(
            (line for line in reversed(lines) if re.match(r"^[A-Za-z_][A-Za-z0-9_]*(Error|Exception):", line)),
            None,
        )
        if exception_line:
            return exception_line

    if stage == "compile":
        return lines[0]
    return lines[-1]


def _trim(value: str) -> str:
    if len(value) <= MAX_CAPTURED_OUTPUT:
        return value
    return value[:MAX_CAPTURED_OUTPUT] + "\n[output truncated]"


def _result(
    started_at: float,
    language: str,
    *,
    stdout: str = "",
    stderr: str = "",
    exit_code: int = 0,
    timed_out: bool = False,
    stage: str = "run",
) -> dict:
    stderr = _trim(stderr.strip())
    return {
        "actual_output": _trim(stdout).strip(),
        "error_message": stderr,
        "error_summary": _clean_error(stderr, language, stage),
        "execution_time_ms": int((time.monotonic() - started_at) * 1000),
        "timed_out": timed_out,
        "exit_code": exit_code,
        "stage": stage,
    }


def _run_process(command: list[str], *, stdin: str, cwd: Path, timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        input=stdin,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
        shell=False,
    )


def _prepare_program(workdir: Path, user_code: str, language: str) -> list[str]:
    if language == "python":
        source = workdir / "main.py"
        source.write_text(user_code, encoding="utf-8")
        return [sys.executable, str(source)]

    if language == "javascript":
        source = workdir / "main.js"
        source.write_text(user_code, encoding="utf-8")
        return ["node", str(source)]

    if language == "cpp":
        source = workdir / "main.cpp"
        executable = workdir / ("main.exe" if sys.platform == "win32" else "main")
        source.write_text(user_code, encoding="utf-8")
        completed = _run_process(
            ["g++", "-std=c++17", "-O2", "-Wall", str(source), "-o", str(executable)],
            stdin="",
            cwd=workdir,
            timeout=settings.COMPILE_TIMEOUT_SECONDS,
        )
        if completed.returncode != 0:
            raise CompilationFailed(completed.stderr, completed.returncode)
        return [str(executable)]

    class_match = re.search(r"public\s+class\s+(\w+)", user_code)
    class_name = class_match.group(1) if class_match else "Main"
    source = workdir / f"{class_name}.java"
    source.write_text(user_code, encoding="utf-8")
    completed = _run_process(
        ["javac", str(source)],
        stdin="",
        cwd=workdir,
        timeout=settings.COMPILE_TIMEOUT_SECONDS,
    )
    if completed.returncode != 0:
        raise CompilationFailed(completed.stderr, completed.returncode)
    return ["java", "-cp", str(workdir), class_name]


class CompilationFailed(Exception):
    def __init__(self, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code


def run_code_batch(user_code: str, language: str, test_inputs: list[str]) -> list[dict]:
    """Compile once and execute the same complete program for each input."""
    lang = language.strip().lower()
    input_values = test_inputs or [""]

    if lang not in SUPPORTED_LANGUAGES:
        return [
            _result(time.monotonic(), lang, stderr=f"Language '{language}' is not supported.", exit_code=1, stage="compile")
            for _ in input_values
        ]

    if not user_code.strip():
        return [
            _result(time.monotonic(), lang, stderr="Write a complete program before running it.", exit_code=1, stage="compile")
            for _ in input_values
        ]

    if lang == "python":
        security_error = _validate_python(user_code)
        if security_error:
            return [
                _result(time.monotonic(), lang, stderr=security_error, exit_code=1, stage="compile")
                for _ in input_values
            ]

    with tempfile.TemporaryDirectory(prefix="debugmentor-") as temp_path:
        workdir = Path(temp_path)
        compile_started_at = time.monotonic()
        try:
            command = _prepare_program(workdir, user_code, lang)
        except CompilationFailed as exc:
            compile_result = _result(
                compile_started_at,
                lang,
                stderr=exc.message,
                exit_code=exc.exit_code,
                stage="compile",
            )
            return [dict(compile_result) for _ in input_values]
        except subprocess.TimeoutExpired:
            compile_result = _result(
                compile_started_at,
                lang,
                stderr=f"Compilation timed out after {settings.COMPILE_TIMEOUT_SECONDS} seconds.",
                exit_code=124,
                timed_out=True,
                stage="compile",
            )
            return [dict(compile_result) for _ in input_values]
        except FileNotFoundError as exc:
            tool = Path(exc.filename).name if exc.filename else lang
            compile_result = _result(
                compile_started_at,
                lang,
                stderr=f"Required runtime '{tool}' is not installed on the server.",
                exit_code=1,
                stage="compile",
            )
            return [dict(compile_result) for _ in input_values]

        results: list[dict] = []
        for test_input in input_values:
            started_at = time.monotonic()
            try:
                completed = _run_process(
                    command,
                    stdin=test_input,
                    cwd=workdir,
                    timeout=settings.EXECUTION_TIMEOUT_SECONDS,
                )
                results.append(
                    _result(
                        started_at,
                        lang,
                        stdout=completed.stdout,
                        stderr=completed.stderr,
                        exit_code=completed.returncode,
                    )
                )
            except subprocess.TimeoutExpired:
                results.append(
                    _result(
                        started_at,
                        lang,
                        stderr=f"Execution timed out after {settings.EXECUTION_TIMEOUT_SECONDS} seconds.",
                        exit_code=124,
                        timed_out=True,
                    )
                )
            except Exception as exc:
                results.append(
                    _result(started_at, lang, stderr=f"Execution service error: {exc}", exit_code=1)
                )

        return results


def run_code(user_code: str, language: str, test_input: str = "") -> dict:
    """Execute one complete console program."""
    return run_code_batch(user_code, language, [test_input])[0]
