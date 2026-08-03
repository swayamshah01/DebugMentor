from datetime import datetime

from pydantic import BaseModel, Field, field_validator


SUPPORTED_LANGUAGES = {"python", "javascript", "java", "cpp"}


class CodePayload(BaseModel):
    code: str = Field(min_length=1)
    language: str
    problem_id: int

    @field_validator("code")
    @classmethod
    def code_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Write a complete program before continuing.")
        return value

    @field_validator("language")
    @classmethod
    def language_must_be_supported(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {value}")
        return normalized


class RunRequest(CodePayload):
    test_case_id: int


class SubmitRequest(CodePayload):
    pass


class TestResultResponse(BaseModel):
    test_case_id: int
    label: str
    input: str | None = None
    expected_output: str | None = None
    actual_output: str | None = None
    error_summary: str = ""
    execution_time_ms: int = 0
    stage: str = "run"
    is_hidden: bool = False
    status: str


class GradeResponse(BaseModel):
    success: bool
    mode: str
    summary: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    dominant_failure_type: str | None = None
    test_results: list[TestResultResponse] = Field(default_factory=list)


class SubmissionResponse(GradeResponse):
    submission_id: int
    problem_id: int
    status: str
    submitted_at: datetime
    hints_available: bool


class HintRequest(BaseModel):
    submission_id: int


class HintResponse(BaseModel):
    submission_id: int
    level: int
    title: str
    content: str
    focus: str
    is_solution: bool
    solution_code: str | None = None
    levels_remaining: int
