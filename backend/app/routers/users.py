import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_password_hash
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
    email = str(payload.email).lower()
    username = payload.username.strip()

    existing_email = db.query(User).filter(func.lower(User.email) == email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="This email is already registered.")

    existing_username = db.query(User).filter(func.lower(User.username) == username.lower()).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="This username is already taken.")

    try:
        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(payload.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("User created: id=%s username=%s", user.id, user.username)
        return user
    except Exception as exc:
        db.rollback()
        logger.error("User creation failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"User creation failed: {exc}")


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Get a user by ID",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> UserResponse:
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
    return db.query(User).offset(skip).limit(limit).all()
