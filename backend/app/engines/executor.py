import subprocess
import sys
import time
import re
from fastapi import HTTPException

# Dangerous Python imports / patterns
DANGEROUS_PATTERNS = [
    r"import\s+(os|subprocess|sys|shutil|pty|socket)",
    r"from\s+(os|subprocess|sys|shutil|pty|socket)\s+import",
    r"__[a-z]+__"  # Blocks __import__, __builtins__ etc. as a basic check
]

def check_security(code: str, language: str):
    """
    Basic security pre-check.
    In a real app, you would use an AST parser or a restricted execution environment.
    """
    if language.lower() == "python":
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                raise HTTPException(status_code=400, detail="Dangerous imports or patterns detected in code.")


def summarize_error(message: str, language: str, stage: str = "run") -> str:
    if not message:
        return ""

    cleaned = message.replace("\r\n", "\n").replace("\r", "\n").strip()
    lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
    if not lines:
        return ""

    if language == "cpp":
        error_lines = [line for line in lines if " error:" in line or line.startswith("error:")]
        note_lines = [line for line in lines if " note:" in line or line.startswith("note:")]
        if error_lines:
            primary = error_lines[0]
            primary = re.sub(r"^[A-Za-z]:\\[^:]+:\d+:\d+:\s*", "", primary)
            primary = primary.replace("error:", "Error:").strip()
            if note_lines:
                note = re.sub(r"^[A-Za-z]:\\[^:]+:\d+:\d+:\s*", "", note_lines[0]).strip()
                return f"{primary} {note}"
            return primary

    if language == "java":
        error_lines = [line for line in lines if " error:" in line or line.startswith("error:")]
        if error_lines:
            primary = re.sub(r"^[A-Za-z]:\\[^:]+:\d+:\s*", "", error_lines[0])
            return primary.replace("error:", "Error:").strip()

    if language == "python":
        traceback_lines = [line for line in lines if line.startswith(("TypeError", "NameError", "ValueError", "IndexError", "KeyError", "SyntaxError", "AttributeError", "ZeroDivisionError", "RecursionError", "RuntimeError"))]
        if traceback_lines:
            return traceback_lines[-1]

    if stage == "compile":
        return lines[0].replace("error:", "Error:").strip()

    return lines[-1]

def run_code(user_code: str, language: str, test_input: str = "") -> dict:
    """
    Executes the given user code with the specified language.
    Passes `test_input` via standard input.
    """
    check_security(user_code, language)

    lang = language.lower()
    start_time = time.monotonic()
    
    import tempfile
    import os
    
    temp_dir_obj = None
    
    def standard_return(actual_output, error_message, timed_out, exit_code, stage="run"):
        return {
            "actual_output": actual_output,
            "error_message": error_message,
            "error_summary": summarize_error(error_message, lang, stage),
            "execution_time_ms": int((time.monotonic() - start_time) * 1000),
            "timed_out": timed_out,
            "exit_code": exit_code,
            "stage": stage,
        }
    
    try:
        # Determine the command to run based on language
        if lang == "python":
            cmd = [sys.executable, "-c", user_code]
        elif lang == "javascript":
            cmd = ["node", "-e", user_code]
        elif lang == "cpp":
            temp_dir_obj = tempfile.TemporaryDirectory()
            temp_dir = temp_dir_obj.name
            cpp_file = os.path.join(temp_dir, "main.cpp")
            exe_file = os.path.join(temp_dir, "main.exe")
            
            with open(cpp_file, "w", encoding="utf-8") as f:
                f.write(user_code)
                
            try:
                compile_proc = subprocess.run(
                    ["g++", "-Wall", cpp_file, "-o", exe_file], 
                    capture_output=True, text=True, timeout=10
                )
            except FileNotFoundError:
                return standard_return("", "C++ compiler (g++) is not installed on the server.", False, 1, "compile")
            except subprocess.TimeoutExpired:
                return standard_return("", "Compilation timed out.", True, 124, "compile")
                
            if compile_proc.returncode != 0:
                return standard_return("", compile_proc.stderr.strip(), False, compile_proc.returncode, "compile")
                
            cmd = [exe_file]
            
        elif lang == "java":
            match = re.search(r"public\s+class\s+(\w+)", user_code)
            class_name = match.group(1) if match else "Solution"
            
            temp_dir_obj = tempfile.TemporaryDirectory()
            temp_dir = temp_dir_obj.name
            java_file = os.path.join(temp_dir, f"{class_name}.java")
            
            with open(java_file, "w", encoding="utf-8") as f:
                f.write(user_code)
                
            try:
                compile_proc = subprocess.run(
                    ["javac", java_file], 
                    capture_output=True, text=True, timeout=10
                )
            except FileNotFoundError:
                return standard_return("", "Java compiler (javac) is not installed on the server.", False, 1, "compile")
            except subprocess.TimeoutExpired:
                return standard_return("", "Compilation timed out.", True, 124, "compile")
                
            if compile_proc.returncode != 0:
                return standard_return("", compile_proc.stderr.strip(), False, compile_proc.returncode, "compile")
                
            cmd = ["java", "-cp", temp_dir, class_name]
            
        else:
            return standard_return(
                f"Language {language} execution not supported.", 
                f"Language {language} execution not supported.", 
                False, -1, "run"
            )
        
        proc = subprocess.run(
            cmd,
            input=test_input,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Capture error from stderr if exit_code != 0
        error_msg = proc.stderr.strip() if proc.returncode != 0 else ""
        return standard_return(proc.stdout, error_msg, False, proc.returncode, "run")
        
    except subprocess.TimeoutExpired:
        return standard_return("", "Execution timed out after 5 seconds.", True, 124, "run")
    except FileNotFoundError:
        return standard_return("", f"Runtime environment for {language} is not installed.", False, 1, "run")
    except Exception as exc:
        return standard_return("", f"Internal server error during execution: {exc}", False, 1, "run")
    finally:
        if temp_dir_obj is not None:
            try:
                temp_dir_obj.cleanup()
            except Exception:
                pass
