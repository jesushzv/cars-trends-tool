"""
User models for authentication
"""

from sqlalchemy import Column, String, Boolean, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class User(Base):
    """User model for authentication"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True, index=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name="check_email"),
        {"extend_existing": True}
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
    
    def to_dict(self):
        """Convert to dictionary (excluding sensitive data)"""
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }


class UserSession(Base):
    """User session model for JWT token management"""
    
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("expires_at > created_at", name="check_expiry"),
        {"extend_existing": True}
    )
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"
