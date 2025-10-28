# Testing Guidelines - Preventing CI/CD Failures

**Purpose:** Ensure all tests pass consistently in both local and CI/CD environments.

## 🚨 Common Issues & Solutions

### 1. Environment-Specific Failures

#### Issue: Bcrypt Password Length
**Problem:** Different bcrypt versions handle the 72-byte password limit differently. Tests may pass locally but fail in CI.

**Solution:** Always test with passwords of varying lengths, including > 72 bytes.

```python
def test_hash_long_password_bcrypt_limit(self):
    """Test passwords longer than 72 bytes (bcrypt limit)"""
    long_password = "a" * 100  # Exceeds bcrypt's 72-byte limit
    hashed = hash_password(long_password)
    assert verify_password(long_password, hashed) is True
```

**Fixed in:** `services/auth_service.py` - Added automatic truncation at 72 bytes

---

### 2. Network-Dependent Tests

#### Issue: External API/Website Tests
**Problem:** Tests that make real network calls fail when:
- External service is down
- Rate limiting occurs
- Geo-blocking in CI environment
- No network access in sandboxed CI

**Symptoms:**
```
FAILED tests/test_craigslist.py::test_scraper_finds_real_data
AssertionError: Should find at least 1 car listing
assert 0 > 0
```

**Solution:** Mark network-dependent tests with `@pytest.mark.skip` or use mocks

```python
@pytest.mark.skip(reason="Network-dependent test - may fail in CI due to rate limiting or geo-blocking")
def test_scraper_finds_real_data(self):
    """Scraper should return at least some listings from real Craigslist"""
    result = scrape_craigslist_tijuana(max_results=10)
    assert len(result) > 0
```

**Alternative:** Use pytest markers for optional network tests
```python
@pytest.mark.network  # Run with: pytest -m network
def test_scraper_finds_real_data(self):
    ...
```

---

## ✅ Testing Checklist

Before pushing code, verify:

### Local Testing
- [ ] All tests pass: `pytest` or `make test`
- [ ] Coverage meets target: `pytest --cov=. --cov-report=term-missing`
- [ ] No network-dependent tests in main suite
- [ ] No environment-specific assumptions (file paths, passwords, etc.)
- [ ] **RECOMMENDED:** Test in Docker: `make test-ci` (matches CI environment)

### Code Review
- [ ] Check for external API calls without mocks
- [ ] Verify password/secret handling
- [ ] Check for hardcoded file paths
- [ ] Look for time-dependent tests (may be flaky)

### CI/CD Preparation
- [ ] Tests run in isolated environment (no shared state)
- [ ] Database tests use in-memory or test fixtures
- [ ] No real credentials or secrets in tests
- [ ] All external dependencies are mocked

---

## 🏷️ Test Categories

### Unit Tests (MUST pass in CI)
- Pure logic tests
- Mocked external dependencies
- Fast execution (< 1s each)
- No network, no database

### Integration Tests (SHOULD pass in CI)
- Test component interactions
- Use test database (in-memory SQLite)
- Mock external APIs
- Moderate execution (1-10s each)

### Network Tests (OPTIONAL in CI)
- Real API calls
- External service dependencies
- Mark with `@pytest.mark.skip` or `@pytest.mark.network`
- Run manually or in nightly builds

### E2E Tests (COMPLEX in CI)
- Full application flow
- May require special setup
- Document any known issues
- Consider separate test environment

---

## 🔍 Identifying Problematic Tests

### Red Flags
1. **Network calls without mocks:**
   ```python
   response = requests.get("https://example.com")  # ❌ Will fail if blocked
   ```

2. **Hardcoded credentials:**
   ```python
   password = "super_long_password..." * 100  # ❌ May exceed bcrypt limit
   ```

3. **File system dependencies:**
   ```python
   with open("/absolute/path/file.txt")  # ❌ Path may not exist in CI
   ```

4. **Time-dependent assertions:**
   ```python
   assert datetime.now().hour == 15  # ❌ Depends on CI timezone
   ```

### Good Practices
1. **Mock external dependencies:**
   ```python
   @patch('requests.get')
   def test_scraper(mock_get):
       mock_get.return_value = Mock(status_code=200, text="<html>...</html>")
   ```

2. **Use environment variables:**
   ```python
   SECRET_KEY = os.getenv("JWT_SECRET_KEY", "test-key-for-local-dev")
   ```

3. **Relative paths or fixtures:**
   ```python
   test_file = Path(__file__).parent / "fixtures" / "test_data.json"
   ```

4. **Time-zone aware tests:**
   ```python
   now = datetime.now(timezone.utc)  # ✅ Explicit timezone
   ```

---

## 🐳 Docker Testing (CI Environment Parity)

**Why Docker Testing Matters:**
- Catches environment-specific issues before CI
- Matches exact CI environment (Python 3.13.7, Linux)
- Prevents false negatives (local pass, CI fail)

**Quick Start:**
```bash
# Test in Docker (matches CI environment)
make test-ci

# Debug in Docker container
make test-ci-debug
```

**What Docker Testing Catches:**
- Library behavior differences (macOS vs Linux)
- Binary wheel differences
- Python version differences
- Package configuration issues

**When to Use:**
- Before pushing critical changes
- When fixing CI failures
- When adding environment-dependent code
- Before releases

## 🛠️ Debugging CI Failures

### Step 1: Reproduce Locally
```bash
# Option A: Quick local test (may not catch environment issues)
cd backend
python -m pytest --tb=short -v

# Option B: Docker test (matches CI environment) - RECOMMENDED
make test-ci

# Check for environment differences
python -c "import bcrypt; print(bcrypt.__version__)"
python -c "import sys; print(sys.version)"
```

### Step 2: Check GitHub Actions Logs
1. Go to Actions tab in repository
2. Click on failed workflow
3. Expand failed test step
4. Look for:
   - Import errors
   - Connection timeouts
   - Version mismatches
   - Missing dependencies

### Step 3: Fix Root Cause
- **Dependency issue:** Pin versions in `requirements.txt`
- **Network issue:** Mock the external call
- **Environment issue:** Add explicit handling (like bcrypt truncation)

---

## 📚 Test Maintenance

### When Adding New Tests
1. Run locally first: `pytest -v`
2. Check if test needs network: Mark appropriately
3. Verify in clean environment: `docker run python:3.13 pytest`
4. Add to appropriate test file

### When Tests Fail in CI
1. Don't just skip the test!
2. Investigate root cause
3. Fix the underlying issue
4. Add safeguards to prevent recurrence

### Regular Maintenance
- Review skipped tests monthly
- Update mocks when APIs change
- Keep dependencies up to date
- Monitor CI failure patterns

---

## 🎯 Coverage Requirements

- **Minimum:** 59% (current threshold)
- **Target:** 70% (achieved!)
- **Ideal:** 80%+

**What to cover:**
- ✅ Core business logic (100%)
- ✅ Data transformations (90%+)
- ✅ Error handling (80%+)
- ⚠️ API endpoints (60%+)
- ⚠️ Background jobs (50%+)
- ❌ One-time scripts (optional)

---

## 🚀 CI/CD Integration

### GitHub Actions Workflow
```yaml
- name: Run tests
  run: |
    cd backend
    pytest --cov=. --cov-report=xml --tb=short
```

### Coverage Reporting
- Codecov automatically uploads coverage
- Fails if coverage drops below threshold
- Comments on PRs with coverage changes

---

## 📖 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Mocking in Python](https://docs.python.org/3/library/unittest.mock.html)
- [Bcrypt Password Limits](https://en.wikipedia.org/wiki/Bcrypt#Description)
- [TEST_SUITE_REDESIGN.md](./TEST_SUITE_REDESIGN.md) - Comprehensive test plan

---

**Last Updated:** October 28, 2025
**Maintainer:** Development Team
**Status:** Active - Follow these guidelines for all new tests

