"""
User service for authentication and user management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional
from datetime import datetime
import logging

from app.models.user import User
from app.schemas.auth import UserCreate
from app.core.security import get_password_hash, verify_password

logger = logging.getLogger(__name__)


class UserService:
    """User service for managing users"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user_data.password)
        
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            is_active=user_data.is_active
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        logger.info(f"Created new user: {user.username}")
        return user
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = await self.get_user_by_username(username)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    async def update_last_login(self, user_id: str) -> None:
        """Update user's last login timestamp"""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.utcnow())
        )
        await self.db.commit()
    
    async def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user information"""
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        if not update_data:
            return None
        
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_user_by_id(user_id)
