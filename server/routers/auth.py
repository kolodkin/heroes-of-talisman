from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from pydantic import BaseModel, EmailStr

from ..database import get_session
from ..models import User
from ..auth import authenticate_user, create_access_token, get_password_hash, get_current_user


router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Request/Response models
class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    last_log_in: Optional[datetime]


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister, session: AsyncSession = Depends(get_session)):
    """Register a new user."""
    # Check if user already exists
    result = await session.execute(select(User).where(User.email == user_data.email))
    existing_user = result.first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(email=user_data.email, password=hashed_password)

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return UserResponse(id=user.id, email=user.email, created_at=user.created_at, last_log_in=user.last_log_in)


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, session: AsyncSession = Depends(get_session)):
    """Login user and return JWT token."""
    user = await authenticate_user(session, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login time
    user.last_log_in = datetime.now()
    session.add(user)
    await session.commit()

    # Create access token
    access_token = create_access_token(data={"sub": user.email})

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at,
        last_log_in=current_user.last_log_in,
    )
