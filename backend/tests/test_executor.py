import pytest
from fastapi import HTTPException
from app.engines.executor import run_code

def test_correct_python_program():
    code = 'print("hello")'
    result = run_code(code, "python")
    assert result["exit_code"] == 0
    assert result["actual_output"].strip() == "hello"
    assert result["timed_out"] is False

def test_syntax_error():
    code = 'print("hello"'
    result = run_code(code, "python")
    assert result["exit_code"] != 0
    assert "SyntaxError" in result["error_message"]
    assert result["timed_out"] is False

def test_infinite_loop():
    code = 'while True: pass'
    result = run_code(code, "python")
    assert result["timed_out"] is True
    assert result["exit_code"] != 0
    assert "timed out" in result["error_message"].lower()

def test_stdin_input():
    code = 'name = input()\nprint(f"Hello {name}")'
    result = run_code(code, "python", test_input="Alice")
    assert result["exit_code"] == 0
    assert result["actual_output"].strip() == "Hello Alice"

def test_dangerous_imports():
    code = 'import os\nos.system("echo hacked")'
    with pytest.raises(HTTPException) as exc_info:
        run_code(code, "python")
    assert exc_info.value.status_code == 400
    assert "Dangerous imports or patterns detected" in exc_info.value.detail
