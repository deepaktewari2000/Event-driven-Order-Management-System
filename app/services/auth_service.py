from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import timedelta

from app.models.user import User, UserRole
from app.schemas.user import UserCreate
from app.schemas.auth import Token, TokenData
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from app.core.exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
    InvalidTokenException
)
from app.core.config import settings


async def register_user(db: AsyncSession, user_data: UserCreate) -> User:
    """
    Register a new user.
    
    Args:
        db: Database session
        user_data: User registration data
        
    Returns:
        Created user
        
    Raises:
        UserAlreadyExistsException: If email already exists
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise UserAlreadyExistsException(user_data.email)
    
    # Create new user
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role=UserRole.CUSTOMER  # Default role
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    """
    Authenticate a user by email and password.
    
    Args:
        db: Database session
        email: User email
        password: Plain password
        
    Returns:
        Authenticated user
        
    Raises:
        InvalidCredentialsException: If credentials are invalid
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsException()
    
    if not user.is_active:
        raise InvalidCredentialsException()
    
    return user


async def create_user_token(user: User) -> Token:
    """
    Create JWT token for user.
    
    Args:
        user: User instance
        
    Returns:
        JWT token
    """
    token_data = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role.value
    }
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(access_token=access_token)


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Get user by email.
    
    Args:
        db: Database session
        email: User email
        
    Returns:
        User or None
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Get user by ID.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User or None
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


def get_token_data(token: str) -> TokenData:
    """
    Extract and validate token data.
    
    Args:
        token: JWT token
        
    Returns:
        Token data
        
    Raises:
        InvalidTokenException: If token is invalid
    """
    payload = decode_access_token(token)
    
    if payload is None:
        raise InvalidTokenException()
    
    email = payload.get("sub")
    user_id = payload.get("user_id")
    role = payload.get("role")
    
    if email is None or user_id is None:
        raise InvalidTokenException()
    
    return TokenData(email=email, user_id=user_id, role=role)
