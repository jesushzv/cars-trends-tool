"""
Tests for authentication system
Phase 16: Authentication

Tests:
- Password hashing and verification
- JWT token creation and validation
- User registration
- User login
- Protected endpoint access
- API endpoints
"""
import pytest
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from services.auth_service import (
    hash_password, verify_password, create_access_token, decode_access_token,
    register_user, login_user, get_current_user
)
from models import User
from database import SessionLocal, create_tables
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def test_db():
    """Create a fresh test database for each test"""
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    # Create tables
    from models import Base
    Base.metadata.create_all(engine)
    
    # Create session
    TestSessionLocal = sessionmaker(bind=engine)
    
    # Monkeypatch SessionLocal in auth_service
    import services.auth_service
    services.auth_service.SessionLocal = TestSessionLocal
    
    yield TestSessionLocal()
    
    # Cleanup
    engine.dispose()


class TestPasswordHashing:
    """Test password hashing functionality"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "test123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt format
    
    def test_verify_correct_password(self):
        """Test verifying correct password"""
        password = "test123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_wrong_password(self):
        """Test verifying wrong password"""
        password = "test123"
        hashed = hash_password(password)
        
        assert verify_password("wrong", hashed) is False
    
    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (salt)"""
        password = "test123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
    
    def test_hash_long_password_bcrypt_limit(self):
        """Test that passwords longer than 72 bytes are handled correctly (bcrypt limit)
        
        This test prevents CI failures when bcrypt is strict about the 72-byte limit.
        Different bcrypt versions/environments may handle this differently.
        """
        # Create a password longer than 72 bytes
        long_password = "a" * 100
        
        # Should not raise an error (would fail in CI without truncation)
        hashed = hash_password(long_password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        
        # Should be able to verify with same long password
        assert verify_password(long_password, hashed) is True
        
        # Different long passwords should produce different hashes
        long_password2 = "b" * 100
        hashed2 = hash_password(long_password2)
        assert verify_password(long_password2, hashed2) is True
        assert verify_password(long_password, hashed2) is False


class TestJWTTokens:
    """Test JWT token functionality"""
    
    def test_create_token(self):
        """Test creating JWT token"""
        data = {"sub": "testuser", "user_id": 1}
        token = create_access_token(data)
        
        assert token is not None
        assert len(token) > 0
        assert token.count(".") == 2  # JWT format: header.payload.signature
    
    def test_decode_token(self):
        """Test decoding JWT token"""
        data = {"sub": "testuser", "user_id": 1, "is_admin": False}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == "testuser"
        assert decoded["user_id"] == 1
        assert decoded["is_admin"] is False
        assert "exp" in decoded  # Expiration time added
    
    def test_decode_invalid_token(self):
        """Test decoding invalid token"""
        decoded = decode_access_token("invalid.token.here")
        
        assert decoded is None
    
    def test_decode_tampered_token(self):
        """Test decoding tampered token"""
        data = {"sub": "testuser", "user_id": 1}
        token = create_access_token(data)
        
        # Tamper with token
        tampered = token[:-10] + "tampered12"
        decoded = decode_access_token(tampered)
        
        assert decoded is None


class TestUserRegistration:
    """Test user registration"""
    
    def test_register_new_user(self, test_db):
        """Test registering a new user"""
        user = register_user(
            email="test@example.com",
            username="testuser",
            password="test123"
        )
        
        assert user is not None
        assert user["email"] == "test@example.com"
        assert user["username"] == "testuser"
        assert user["is_admin"] is False
        assert "id" in user
        assert "created_at" in user
        assert "password" not in user  # Password should not be in response
    
    def test_register_duplicate_email(self, test_db):
        """Test registering with duplicate email"""
        register_user("test@example.com", "user1", "test123")
        
        with pytest.raises(ValueError, match="Email already registered"):
            register_user("test@example.com", "user2", "test123")
    
    def test_register_duplicate_username(self, test_db):
        """Test registering with duplicate username"""
        register_user("test1@example.com", "testuser", "test123")
        
        with pytest.raises(ValueError, match="Username already taken"):
            register_user("test2@example.com", "testuser", "test123")
    
    def test_register_admin_user(self, test_db):
        """Test registering an admin user"""
        user = register_user(
            email="admin@example.com",
            username="admin",
            password="admin123",
            is_admin=True
        )
        
        assert user["is_admin"] is True


class TestUserLogin:
    """Test user login"""
    
    def test_login_with_username(self, test_db):
        """Test login with username"""
        # Register user
        register_user("test@example.com", "testuser", "test123")
        
        # Login
        result = login_user("testuser", "test123")
        
        assert result is not None
        assert "access_token" in result
        assert result["token_type"] == "bearer"
        assert "user" in result
        assert result["user"]["username"] == "testuser"
        assert result["user"]["email"] == "test@example.com"
    
    def test_login_with_email(self, test_db):
        """Test login with email"""
        # Register user
        register_user("test@example.com", "testuser", "test123")
        
        # Login with email
        result = login_user("test@example.com", "test123")
        
        assert result is not None
        assert "access_token" in result
        assert result["user"]["username"] == "testuser"
    
    def test_login_wrong_password(self, test_db):
        """Test login with wrong password"""
        register_user("test@example.com", "testuser", "test123")
        
        with pytest.raises(ValueError, match="Invalid credentials"):
            login_user("testuser", "wrongpassword")
    
    def test_login_nonexistent_user(self, test_db):
        """Test login with nonexistent user"""
        with pytest.raises(ValueError, match="Invalid credentials"):
            login_user("nonexistent", "test123")
    
    def test_login_inactive_user(self, test_db):
        """Test login with inactive user"""
        # Register user
        register_user("test@example.com", "testuser", "test123")
        
        # Deactivate user
        db = test_db
        user = db.query(User).filter(User.username == "testuser").first()
        user.is_active = False
        db.commit()
        
        # Try to login
        with pytest.raises(ValueError, match="Account is disabled"):
            login_user("testuser", "test123")


class TestGetCurrentUser:
    """Test getting current user from token"""
    
    def test_get_user_from_valid_token(self, test_db):
        """Test getting user from valid token"""
        # Register and login
        register_user("test@example.com", "testuser", "test123")
        login_result = login_user("testuser", "test123")
        token = login_result["access_token"]
        
        # Get current user
        user = get_current_user(token)
        
        assert user is not None
        assert user["username"] == "testuser"
        assert user["email"] == "test@example.com"
        assert user["is_active"] is True
    
    def test_get_user_from_invalid_token(self, test_db):
        """Test getting user from invalid token"""
        user = get_current_user("invalid.token.here")
        
        assert user is None
    
    def test_get_inactive_user_from_token(self, test_db):
        """Test getting inactive user from token"""
        # Register and login
        register_user("test@example.com", "testuser", "test123")
        login_result = login_user("testuser", "test123")
        token = login_result["access_token"]
        
        # Deactivate user
        db = test_db
        user_db = db.query(User).filter(User.username == "testuser").first()
        user_db.is_active = False
        db.commit()
        
        # Try to get current user
        user = get_current_user(token)
        
        assert user is None


class TestAuthAPI:
    """Test authentication API endpoints (integration tests)
    
    Note: These tests use the production database and require it to be set up.
    Ensure the database schema is up to date if these tests fail.
    """
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        from main import app
        
        return TestClient(app)
    
    def test_me_endpoint_no_token(self, client):
        """Test /auth/me without token"""
        response = client.get("/auth/me")
        
        assert response.status_code == 401
    
    def test_register_endpoint_validation(self, client):
        """Test that register endpoint exists and validates"""
        # Test with missing parameters (should fail)
        response = client.post("/auth/register")
        
        # Should return 422 (validation error) not 404 (not found)
        assert response.status_code == 422
    
    def test_login_endpoint_validation(self, client):
        """Test that login endpoint exists and validates"""
        # Test with missing parameters (should fail)
        response = client.post("/auth/login")
        
        # Should return 422 (validation error) not 404 (not found)
        assert response.status_code == 422
    
    def test_protected_endpoint_no_token(self, client):
        """Test protected endpoint without token"""
        response = client.get("/auth/protected")
        
        assert response.status_code == 401


if __name__ == "__main__":
    print("Running auth tests...")
    pytest.main([__file__, "-v"])

