from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TopMistakeItem(BaseModel):
    """Represents a single mistake type with its frequency."""
    mistake_type: str
    count: int


class SubmissionHistoryItem(BaseModel):
    """Represents a single submission in the user's history."""
    submission_id: int
    language: str
    status: str
    submitted_at: datetime
    problem_id: Optional[int] = None
    problem_title: Optional[str] = None
    pattern_name: Optional[str] = None
    dominant_failure_type: Optional[str] = None
    mistake_type: Optional[str] = None
    hint_level: int


class StatsInfo(BaseModel):
    """Aggregated stats about the user's submissions."""
    total_submissions: int
    passed_submissions: int
    failed_submissions: int
    pass_rate: float
    average_hint_level: float


class PatternProgressItem(BaseModel):
    pattern_id: int
    pattern_name: str
    attempted: int
    solved: int
    mastery_percent: float


class RecommendationItem(BaseModel):
    label: str
    title: str
    problem_id: Optional[int] = None
    reason: str


class ReadinessSnapshot(BaseModel):
    strongest_patterns: List[str]
    weakest_patterns: List[str]
    recent_streak: int
    average_hints: float


class BadgeItem(BaseModel):
    id: str
    label: str
    description: str
    icon: str
    tone: str


class ProfileResponse(BaseModel):
    """Complete learning profile for a user."""
    user_id: int
    username: str
    email: str
    created_at: datetime
    top_mistakes: List[TopMistakeItem]
    submission_history: List[SubmissionHistoryItem]
    stats: StatsInfo
    solved_problems_count: int = 0
    badges: Optional[List[BadgeItem]] = None
    recent_trend: Optional[List[str]] = None  # e.g. ["PASS", "FAIL", "PASS", ...]
    weak_patterns: Optional[List[PatternProgressItem]] = None
    recommendations: Optional[List[RecommendationItem]] = None
    readiness_snapshot: Optional[ReadinessSnapshot] = None
