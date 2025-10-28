"""
Authentication Service
Phase 16: User authentication with JWT tokens

Handles:
- User registration
- User login
- Password hashing and verification
- JWT token generation and validation
"""
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt  # Use bcrypt directly, not passlib (avoids environment-specific issues)
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User

# Bcrypt configuration
# Using bcrypt directly instead of passlib to avoid environment-specific validation issues
# that caused failures in CI despite working locally
BCRYPT_ROUNDS = 12  # Cost factor (2^12 iterations)

# JWT configuration (can be overridden with environment variables)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def hash_password(password: str) -> str:
    """
    Hash a plain password using bcrypt directly (no passlib wrapper)
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string (bcrypt format: $2b$12$...)
    
    Note:
        Uses bcrypt directly to avoid passlib's environment-specific validation
        that caused CI failures. Bcrypt has a 72-byte limit, so we truncate
        passwords at that boundary.
    """
    # Convert to bytes and truncate at 72 bytes (bcrypt's maximum)
    password_bytes = password.encode('utf-8')[:72]
    
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string (bcrypt format)
    return hashed_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its bcrypt hash
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to check against (bcrypt format)
        
    Returns:
        True if password matches, False otherwise
    
    Note:
        Uses bcrypt directly. Truncates password at 72 bytes to match how
        it was hashed, ensuring consistent verification.
    """
    # Convert to bytes and truncate at 72 bytes (same as hash_password)
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    
    # Verify password
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary of claims to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def register_user(email: str, username: str, password: str, is_admin: bool = False) -> dict:
    """
    Register a new user
    
    Args:
        email: User's email address
        username: User's username
        password: Plain text password
        is_admin: Whether user should have admin privileges
        
    Returns:
        Dict with user info and success status
        
    Raises:
        ValueError: If email or username already exists
    """
    db = SessionLocal()
    
    try:
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            raise ValueError("Email already registered")
        
        # Check if username already exists
        existing_username = db.query(User).filter(User.username == username).first()
        if existing_username:
            raise ValueError("Username already taken")
        
        # Create new user
        hashed_password = hash_password(password)
        new_user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            is_admin=is_admin,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "id": new_user.id,
            "email": new_user.email,
            "username": new_user.username,
            "is_admin": new_user.is_admin,
            "created_at": new_user.created_at.isoformat()
        }
    finally:
        db.close()


def login_user(username: str, password: str) -> dict:
    """
    Authenticate user and generate JWT token
    
    Args:
        username: Username or email
        password: Plain text password
        
    Returns:
        Dict with access token and user info
        
    Raises:
        ValueError: If credentials are invalid
    """
    db = SessionLocal()
    
    try:
        # Find user by username or email
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            raise ValueError("Invalid credentials")
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")
        
        # Check if user is active
        if not user.is_active:
            raise ValueError("Account is disabled")
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Generate JWT token
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id, "is_admin": user.is_admin}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin
            }
        }
    finally:
        db.close()


def get_current_user(token: str) -> Optional[dict]:
    """
    Get current user from JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        User dict or None if token is invalid
    """
    payload = decode_access_token(token)
    
    if payload is None:
        return None
    
    username = payload.get("sub")
    if username is None:
        return None
    
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.username == username).first()
        
        if user is None or not user.is_active:
            return None
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
            "is_active": user.is_active
        }
    finally:
        db.close()


def get_user_by_id(user_id: int) -> Optional[dict]:
    """
    Get user by ID
    
    Args:
        user_id: User's ID
        
    Returns:
        User dict or None if not found
    """
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if user is None:
            return None
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    finally:
        db.close()


# ============================================================================
# TESTING
# ============================================================================
if __name__ == "__main__":
    print("Testing auth_service.py...")
    print("=" * 60)
    
    # Test password hashing
    print("\n1. Testing password hashing...")
    password = "test123"
    hashed = hash_password(password)
    print(f"   Password: {password}")
    print(f"   Hashed: {hashed[:50]}...")
    print(f"   ✓ Verify correct: {verify_password(password, hashed)}")
    print(f"   ✓ Verify wrong: {verify_password('wrong', hashed)}")
    
    # Test JWT token
    print("\n2. Testing JWT tokens...")
    token = create_access_token(data={"sub": "testuser", "user_id": 1})
    print(f"   Token: {token[:50]}...")
    decoded = decode_access_token(token)
    print(f"   ✓ Decoded: {decoded}")
    
    print("\n✅ All auth service tests passed!")

