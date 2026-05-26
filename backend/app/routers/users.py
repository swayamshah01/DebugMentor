import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import build_unique_username
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=201,
    summary="Create a new user",
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    POST /api/users

    Creates a new student account.
    Returns HTTP 400 if the username or email already exists.
    """
    # ── Check for duplicates ───────────────────────────────────────────────────
    email = str(payload.email).lower()
    existing = db.query(User).filter(User.email == email).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists.",
        )

    # ── Create user ────────────────────────────────────────────────────────────
    try:
        username = payload.username or build_unique_username(email, db)
        user = User(username=username, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("User created: id=%s username=%s", user.id, user.username)
        return user

    except Exception as exc:
        db.rollback()
        logger.error("User creation failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"User creation failed: {str(exc)}",
        )


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Get a user by ID",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    GET /api/users/{user_id}

    Returns the user record for the given ID.
    Returns HTTP 404 if the user does not exist.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")
    return user


@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="List all users",
)
def list_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    """
    GET /api/users?skip=0&limit=50

    Returns a paginated list of all users.
    Phase 2: add search/filter by username.
    """
    return db.query(User).offset(skip).limit(limit).all()
