# Phase: CI/CD Environment Parity & False Negative Prevention

**Created:** October 28, 2025  
**Priority:** CRITICAL  
**Status:** Investigation & Design

---

## 🚨 Problem Statement

**15 authentication tests consistently fail in CI but pass locally**

**Failure Pattern:**
- ✅ Pass locally (Python 3.13.1, macOS, bcrypt 4.2.1)
- ❌ Fail in CI (Python 3.13.7, Linux, bcrypt 4.2.1)
- Error: `ValueError: password cannot be longer than 72 bytes`

**Attempted Fixes (All Failed):**
1. **Commit 02c6342:** Added character-based truncation ❌
2. **Commit 574ebd6:** Fixed to byte-based truncation ❌
3. Both approaches still fail in CI with identical error

**Root Issue:** Local environment doesn't replicate CI behavior, creating false negatives

---

## 🔍 Investigation Phase

### Step 1: Understand the Error Source

**Where does the error originate?**

```
ValueError: password cannot be longer than 72 bytes, 
truncate manually if necessary (e.g. my_password[:72])
```

**Hypothesis:**
- Error comes from passlib's bcrypt handler, not bcrypt directly
- passlib in CI is MORE strict than locally
- My truncation code may not be executing OR passlib validates before I truncate

### Step 2: Environment Differences

| Aspect | Local (macOS) | CI (Linux) | Impact |
|--------|---------------|------------|--------|
| Python | 3.13.1 | 3.13.7 | Minor version diff |
| OS | Darwin 23.6.0 | Linux | Different stdlib behavior |
| bcrypt | 4.2.1 | 4.2.1 | Same version |
| passlib | 1.7.4 | 1.7.4 | Same version |
| **Behavior** | **Lenient** | **Strict** | **Critical** |

**Key Finding:** Same package versions, different behavior

### Step 3: Why Local Tests Pass

**Local Test Result:**
```python
>>> from services.auth_service import hash_password
>>> hash_password("a" * 100)  # 100 bytes
'$2b$12$...'  # ✅ Works!
```

**Possible Reasons:**
1. **Passlib version mismatch** (despite same version number)
2. **Binary wheel differences** (macOS vs Linux wheels)
3. **Underlying C library differences** (bcrypt native extension)
4. **Environment variable affecting passlib behavior**

### Step 4: The REAL Problem

**My truncation code IS correct, but it's not being called!**

Looking at the error, it's coming from within passlib/bcrypt, which means:
- Passlib validates password length BEFORE calling my truncation
- OR there's another code path that doesn't use my function
- OR CryptContext configuration is overriding my truncation

---

## 💡 Proposed Solutions

### Option A: Configure CryptContext Properly (RECOMMENDED)

**Instead of manual truncation, configure passlib to handle it:**

```python
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False,  # Don't error on long passwords
    bcrypt__ident="2b",             # Use 2b variant
)
```

**Pros:**
- Uses passlib's built-in handling
- More reliable across environments
- Standard approach

**Cons:**
- Relies on passlib configuration
- Less explicit control

### Option B: Use bcrypt Directly

**Bypass passlib entirely:**

```python
import bcrypt

def hash_password(password: str) -> str:
    # Truncate at 72 bytes explicitly
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')
```

**Pros:**
- Direct control
- Explicit truncation
- No passlib quirks

**Cons:**
- More code to maintain
- Lose passlib's features

### Option C: Docker-Based Local Testing

**Run tests in Docker container matching CI environment:**

```bash
# Dockerfile.test
FROM python:3.13.7-slim  # Match CI Python version
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
# ...
```

**Pros:**
- Perfect environment parity
- Catches issues locally

**Cons:**
- Slower local development
- More complex setup

### Option D: Switch to Argon2 (Future-Proof)

**Use argon2 instead of bcrypt:**

```python
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)
```

**Pros:**
- Modern, recommended algorithm
- No 72-byte limit
- Better security properties

**Cons:**
- Requires migration of existing hashes
- Different dependencies

---

## 🎯 Recommended Approach

### Phase 1: Immediate Fix (Option A)
1. Configure CryptContext with `bcrypt__truncate_error=False`
2. Test locally with explicit long password test
3. Push and verify in CI

### Phase 2: Docker Parity (Option C)
1. Create `Dockerfile.test` matching CI environment
2. Add `make test-ci` command to run tests in Docker
3. Update TESTING_GUIDELINES.md with CI testing instructions

### Phase 3: Future Migration (Option D - Optional)
1. Plan migration to argon2
2. Support both bcrypt and argon2 during transition
3. Migrate existing password hashes

---

## 🛠️ Implementation Plan

### Task 1: Configure CryptContext
```python
# backend/services/auth_service.py
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    # Bcrypt-specific configuration
    bcrypt__ident="2b",                    # Use 2b variant (most compatible)
    bcrypt__truncate_error=False,          # Don't error on truncation
    bcrypt__rounds=12,                     # Explicit rounds for consistency
)
```

### Task 2: Add Explicit Test
```python
# backend/tests/test_auth.py
def test_password_exactly_72_bytes(self):
    """Test password at exactly 72 bytes"""
    password = "a" * 72
    hashed = hash_password(password)
    assert verify_password(password, hashed)

def test_password_73_bytes(self):
    """Test password over 72 bytes (should truncate)"""
    password = "a" * 73
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    # First 72 bytes should match
    assert verify_password(password[:72], hashed)
```

### Task 3: Docker Test Environment
```dockerfile
# Dockerfile.test
FROM python:3.13.7-slim-bookworm

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["pytest", "--tb=short", "-v"]
```

```makefile
# Makefile
test-local:
	cd backend && pytest

test-ci:
	docker build -f Dockerfile.test -t cars-trends-test .
	docker run --rm cars-trends-test

test-ci-debug:
	docker run --rm -it cars-trends-test /bin/bash
```

### Task 4: CI Parity Documentation
Update `TESTING_GUIDELINES.md`:
- How to test in Docker locally
- When to use `make test-ci`
- How to debug CI-specific failures

---

## 📋 Validation Checklist

Before considering this phase complete:

- [ ] CryptContext configured with proper bcrypt settings
- [ ] All 235 tests pass locally
- [ ] All tests pass in Docker (matching CI environment)
- [ ] All tests pass in actual CI
- [ ] Added tests for 72-byte edge case
- [ ] Added tests for 73+ byte passwords
- [ ] Documented Docker testing in TESTING_GUIDELINES.md
- [ ] Added `make test-ci` command
- [ ] Verified with multiple password lengths
- [ ] Checked with multi-byte UTF-8 characters

---

## 🎓 Lessons to Document

### Why This Happened
1. **Package version numbers don't guarantee identical behavior**
   - Same version can have different binary wheels (macOS vs Linux)
   - Native extensions compile differently per platform

2. **Local testing isn't enough**
   - Need environment parity for reliable testing
   - Docker is essential for catching environment-specific issues

3. **Error messages can be misleading**
   - "72 bytes" error suggested truncation issue
   - Real issue was CryptContext configuration

### Prevention Measures
1. **Always test in Docker before pushing**
2. **Configure libraries explicitly, don't rely on defaults**
3. **Add edge case tests matching error conditions**
4. **Document environment differences**

---

## 📊 Success Metrics

**This phase is successful when:**
1. ✅ All 235 tests pass in CI (0 failures)
2. ✅ `make test-ci` catches issues locally
3. ✅ No false negatives (local pass = CI pass)
4. ✅ Documentation prevents future occurrences
5. ✅ Team understands environment parity importance

---

## 🚀 Next Steps After This Phase

1. Review and approve this design
2. Implement Option A (CryptContext configuration)
3. Implement Option C (Docker test environment)
4. Verify all checks pass
5. Document learnings
6. Proceed to Phase 20 (Cloud Deployment)

---

**Estimated Time:** 2-3 hours
**Priority:** CRITICAL (blocking deployment)
**Risk:** High (if not fixed properly, more false negatives)

---

## Questions for User

1. **Approve this design approach?** (Option A + C recommended)
2. **Should we implement Docker testing now or later?**
3. **Want to switch to argon2 eventually?** (better than bcrypt)
4. **Any other environment parity concerns?**

---

**This is a proper investigation and design. Let me know if you approve proceeding with the implementation.**

