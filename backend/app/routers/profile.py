"""User progress, submission history, and practice insights."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.database import get_db
from app.models.user import User
from app.models.submission import Submission
from app.models.mistake import Mistake
from app.models.problem import Problem
from app.models.pattern import Pattern
from app.auth import get_current_user
from app.schemas.profile import (
    TopMistakeItem, SubmissionHistoryItem, StatsInfo, ProfileResponse,
    PatternProgressItem, RecommendationItem, ReadinessSnapshot, BadgeItem,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def build_badges(
    total: int,
    passed: int,
    recent_streak: int,
    avg_hint: float,
    weak_patterns: list[PatternProgressItem],
) -> list[BadgeItem]:
    badges: list[BadgeItem] = []

    if passed >= 1:
        badges.append(BadgeItem(
            id="first-accept",
            label="First Accept",
            description="Solved your first graded problem.",
            icon="FA",
            tone="success",
        ))
    if recent_streak >= 3:
        badges.append(BadgeItem(
            id="streak-3",
            label="3-Day Heat",
            description="Built a streak of 3 passed submissions in a row.",
            icon="S3",
            tone="accent",
        ))
    if recent_streak >= 5:
        badges.append(BadgeItem(
            id="streak-5",
            label="Locked In",
            description="Reached a streak of 5 consecutive passed submissions.",
            icon="S5",
            tone="accent",
        ))
    if total >= 10:
        badges.append(BadgeItem(
            id="consistent-practicer",
            label="Consistent Practicer",
            description="Completed at least 10 graded submissions.",
            icon="CP",
            tone="neutral",
        ))
    if passed >= 3 and avg_hint <= 0.75:
        badges.append(BadgeItem(
            id="independent-solver",
            label="Independent Solver",
            description="Solved multiple problems while using very few hints.",
            icon="IS",
            tone="success",
        ))
    strong_pattern = next((item for item in weak_patterns if item.mastery_percent >= 80 and item.attempted >= 2), None)
    if strong_pattern:
        badges.append(BadgeItem(
            id=f"pattern-{strong_pattern.pattern_id}",
            label=f"{strong_pattern.pattern_name} Specialist",
            description=f"Maintained strong mastery in {strong_pattern.pattern_name}.",
            icon="PS",
            tone="warning",
        ))

    return badges


@router.get(
    "/profile/{user_id}",
    response_model=ProfileResponse,
    summary="Get learning profile for a user",
    description="Returns aggregated learning profile: top mistakes, submission history, stats",
)
def get_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProfileResponse:
    """
    GET /api/profile/{user_id}
    
    Returns the learning profile (top mistakes, submission history, stats) for a user.
    Users can only view their own profile (enforced by checking current_user.id).
    """
    # Security: ensure user can only view their own profile
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden: can only view own profile")
    
    # 1. Query top mistakes
    top_mistakes_data = (
        db.query(Mistake.mistake_type, func.count(Mistake.id).label("count"))
        .filter(Mistake.user_id == user_id)
        .group_by(Mistake.mistake_type)
        .order_by(desc(func.count(Mistake.id)))
        .limit(10)
        .all()
    )
    top_mistakes = [
        TopMistakeItem(mistake_type=m.mistake_type, count=m.count)
        for m in top_mistakes_data
    ]
    
    # 2. Query submission history (newest first)
    submissions = (
        db.query(Submission, Problem, Pattern)
        .join(Problem, Submission.problem_id == Problem.id, isouter=True)
        .join(Pattern, Problem.pattern_id == Pattern.id, isouter=True)
        .filter(Submission.user_id == user_id)
        .order_by(desc(Submission.submitted_at))
        .limit(50)
        .all()
    )
    
    submission_history = []
    pattern_stats = {}
    solved_problem_ids = set()
    for sub, problem, pattern in submissions:
        # Get associated mistake if one exists
        mistake = (
            db.query(Mistake)
            .filter(Mistake.submission_id == sub.id)
            .first()
        )
        
        dom_failure = None
        if sub.test_results and isinstance(sub.test_results, dict):
            dom_failure = sub.test_results.get('dominant_failure_type')
        
        item = SubmissionHistoryItem(
            submission_id=sub.id,
            language=sub.language,
            status=sub.status,
            submitted_at=sub.submitted_at,
            problem_id=int(sub.problem_id) if sub.problem_id is not None else None,
            problem_title=problem.title if problem else None,
            pattern_name=pattern.name if pattern else None,
            dominant_failure_type=dom_failure,
            mistake_type=mistake.mistake_type if mistake else None,
            hint_level=sub.hint_level,
        )
        submission_history.append(item)

        if problem and pattern:
            bucket = pattern_stats.setdefault(pattern.id, {
                "pattern_id": pattern.id,
                "pattern_name": pattern.name,
                "attempted": set(),
                "solved": set(),
            })
            bucket["attempted"].add(problem.id)
            if sub.status == "passed":
                bucket["solved"].add(problem.id)
                solved_problem_ids.add(problem.id)
    
    # 3. Calculate stats
    total = len(submissions)
    passed = sum(1 for sub, _, _ in submissions if sub.status == "passed")
    failed = total - passed
    pass_rate = (passed / total * 100) if total > 0 else 0.0
    
    avg_hint = 0.0
    if total > 0:
        total_hints = sum(sub.hint_level for sub, _, _ in submissions)
        avg_hint = total_hints / total

    weak_patterns = []
    for bucket in pattern_stats.values():
        attempted = len(bucket["attempted"])
        solved = len(bucket["solved"])
        mastery = (solved / attempted * 100) if attempted else 0.0
        weak_patterns.append(PatternProgressItem(
            pattern_id=bucket["pattern_id"],
            pattern_name=bucket["pattern_name"],
            attempted=attempted,
            solved=solved,
            mastery_percent=mastery,
        ))
    weak_patterns.sort(key=lambda item: (item.mastery_percent, -item.attempted))

    recommendations = []
    for item in weak_patterns[:2]:
        recommendations.append(RecommendationItem(
            label="Retry",
            title=item.pattern_name,
            problem_id=None,
            reason=f"You have a low mastery score in {item.pattern_name} ({item.mastery_percent:.0f}%).",
        ))

    recent_streak = 0
    for sub, _, _ in submissions:
        if sub.status == "passed":
            recent_streak += 1
        else:
            break

    strongest_patterns = [item.pattern_name for item in sorted(weak_patterns, key=lambda item: item.mastery_percent, reverse=True)[:2]]
    weakest_patterns = [item.pattern_name for item in weak_patterns[:2]]
    
    stats = StatsInfo(
        total_submissions=total,
        passed_submissions=passed,
        failed_submissions=failed,
        pass_rate=pass_rate,
        average_hint_level=avg_hint,
    )
    
    # 4. Compute recent trend (last 10 submissions)
    recent_trend = []
    for sub in reversed(submission_history[:10]):
        recent_trend.append("PASS" if sub.status == "passed" else "FAIL")

    badges = build_badges(total, passed, recent_streak, avg_hint, weak_patterns)
    
    return ProfileResponse(
        user_id=user_id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at,
        top_mistakes=top_mistakes,
        submission_history=submission_history,
        stats=stats,
        solved_problems_count=len(solved_problem_ids),
        badges=badges,
        recent_trend=recent_trend,
        weak_patterns=weak_patterns,
        recommendations=recommendations,
        readiness_snapshot=ReadinessSnapshot(
            strongest_patterns=strongest_patterns,
            weakest_patterns=weakest_patterns,
            recent_streak=recent_streak,
            average_hints=avg_hint,
        ),
    )
