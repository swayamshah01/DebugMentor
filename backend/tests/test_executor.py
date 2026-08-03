from app.config import settings
from app.engines.executor import run_code, run_code_batch


def test_python_program_reads_stdin_and_prints_output():
    code = "def main():\n    value = int(input())\n    print(value + 1)\n\nmain()"
    result = run_code(code, "python", "7")

    assert result["exit_code"] == 0
    assert result["actual_output"] == "8"


def test_batch_runner_executes_each_input():
    code = "value = int(input())\nprint(value * 2)"
    results = run_code_batch(code, "python", ["2", "5"])

    assert [result["actual_output"] for result in results] == ["4", "10"]


def test_python_syntax_error_is_captured():
    result = run_code('print("hello"', "python")

    assert result["exit_code"] != 0
    assert "SyntaxError" in result["error_message"]


def test_timeout_is_captured(monkeypatch):
    monkeypatch.setattr(settings, "EXECUTION_TIMEOUT_SECONDS", 1)
    result = run_code("while True:\n    pass", "python")

    assert result["timed_out"] is True
    assert result["exit_code"] == 124


def test_blocked_python_import_returns_compile_error():
    result = run_code("import os\nprint(os.getcwd())", "python")

    assert result["exit_code"] != 0
    assert result["stage"] == "compile"
    assert "not allowed" in result["error_summary"]
