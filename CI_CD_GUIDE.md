# CI/CD Pipeline Guide
**Cars Trends Tool - Phase 19**

Complete guide for the Continuous Integration and Continuous Deployment pipeline.

## 🎯 Overview

The CI/CD pipeline automates:
- ✅ Code quality checks (linting, formatting)
- ✅ Automated testing with coverage
- ✅ Security scanning
- ✅ Docker image builds
- ✅ Multi-arch support (amd64, arm64)
- ✅ Image publishing to GitHub Container Registry
- ✅ Nightly comprehensive tests

## 🏗️ Architecture

```
┌────────────────────────────────────────────────┐
│          Developer Workflow                    │
│                                                 │
│  feature/* → develop → main                    │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────────┐
│         GitHub Actions Triggers                │
│                                                 │
│  • Pull Request → PR Checks                    │
│  • Push to develop/main → CI/CD               │
│  • Daily 2 AM → Nightly Tests                  │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────────┐
│            Pipeline Jobs                       │
│                                                 │
│  Lint → Test → Security → Build → Push        │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────────┐
│         GitHub Container Registry              │
│                                                 │
│  ghcr.io/username/repo/backend:tag            │
│  ghcr.io/username/repo/frontend:tag           │
└─────────────────────────────────────────────────┘
```

## 📦 Workflows

### 1. Pull Request Checks (`pr-checks.yml`)

**Trigger**: Pull request to `main` or `develop`

**Jobs**:
1. **Lint Python** - flake8, black, isort
2. **Run Tests** - Full test suite with coverage
3. **Security Scan** - bandit, safety
4. **Build Docker** - Verify images build correctly

**Purpose**: Ensure code quality before merge

**Time**: ~5-10 minutes

### 2. CI/CD Pipeline (`ci-cd.yml`)

**Trigger**: Push to `main` or `develop`

**Jobs**:
1. **Test Suite** - Run all tests with coverage
2. **Build & Push** - Build and publish Docker images to GHCR
3. **Scan Images** - Security scan published images with Trivy
4. **Create Release** - Generate GitHub release (main branch only)
5. **Deployment Ready** - Summary and deployment instructions

**Purpose**: Build, test, and publish production-ready images

**Time**: ~10-15 minutes

### 3. Nightly Tests (`nightly.yml`)

**Trigger**: Daily at 2 AM UTC (or manual)

**Jobs**:
1. **Comprehensive Tests** - Full test suite with timeout
2. **Latest Dependencies** - Test with latest package versions
3. **Performance** - Basic performance benchmarks
4. **Notify on Failure** - Create GitHub issue if tests fail

**Purpose**: Catch issues early, test dependency compatibility

**Time**: ~15-20 minutes

## 🔧 Configuration Files

### Backend Configuration

```
backend/
├── .flake8              # Flake8 linting rules
├── pyproject.toml       # Black, isort, pytest config
├── .coveragerc          # Coverage settings
└── requirements.txt     # Dependencies (with CI tools)
```

### GitHub Actions

```
.github/workflows/
├── pr-checks.yml        # Pull request validation
├── ci-cd.yml           # Main CI/CD pipeline
└── nightly.yml         # Nightly comprehensive tests
```

## 🚀 Usage

### For Developers

#### Creating a Pull Request

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes and commit
git add .
git commit -m "Add my feature"

# 3. Push to GitHub
git push origin feature/my-feature

# 4. Create pull request on GitHub
# → PR checks run automatically
```

#### Checking Code Quality Locally

```bash
cd backend

# Run linting
flake8 .
black --check .
isort --check .

# Fix formatting
black .
isort .

# Run tests
pytest tests/ -v --cov=.

# Security scan
bandit -r .
safety check
```

### For Maintainers

#### Merging to Develop

```bash
# Merge PR to develop branch
# → CI/CD runs automatically
# → Images published to GHCR with 'develop' tag
```

#### Releasing to Production

```bash
# 1. Merge develop to main
git checkout main
git merge develop
git push origin main

# → CI/CD runs
# → Images published with 'latest' and 'main' tags
# → GitHub release created
```

## 📊 Monitoring

### GitHub Actions Dashboard

View workflow runs:
```
https://github.com/username/repo/actions
```

### Status Badges

Add to README.md:
```markdown
![CI/CD](https://github.com/username/repo/actions/workflows/ci-cd.yml/badge.svg)
![Tests](https://github.com/username/repo/actions/workflows/pr-checks.yml/badge.svg)
```

### Coverage Reports

Coverage reports are uploaded to Codecov and available as artifacts.

## 🐳 Docker Images

### Pulling Images

```bash
# Latest from main branch
docker pull ghcr.io/username/repo/backend:latest
docker pull ghcr.io/username/repo/frontend:latest

# From develop branch
docker pull ghcr.io/username/repo/backend:develop
docker pull ghcr.io/username/repo/frontend:develop

# Specific commit
docker pull ghcr.io/username/repo/backend:main-abc123
```

### Using Published Images

Update `docker-compose.yml`:
```yaml
services:
  backend:
    image: ghcr.io/username/repo/backend:latest
    # Remove 'build' section
  
  frontend:
    image: ghcr.io/username/repo/frontend:latest
    # Remove 'build' section
```

Then:
```bash
docker-compose pull
docker-compose up -d
```

## 🔐 Security

### Secrets Required

Set in GitHub repository settings → Secrets:

1. **GITHUB_TOKEN** - Automatically provided
2. **CODECOV_TOKEN** - Optional, for coverage reports

### Security Scanning

**Tools Used**:
- **Bandit**: Python code security scanner
- **Safety**: Dependency vulnerability checker
- **Trivy**: Docker image vulnerability scanner

**Scan Results**: Available in GitHub Security tab

## 🧪 Testing

### Test Categories

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/ -v -m unit

# E2E tests only
pytest tests/ -v -m e2e

# Exclude slow tests
pytest tests/ -v -m "not slow"

# With coverage
pytest tests/ -v --cov=. --cov-report=html
```

### Coverage Requirements

- **Minimum**: 70%
- **Reports**: HTML, XML, terminal
- **Enforcement**: CI fails if below threshold

### E2E Tests

Located in `tests/test_e2e.py`:
- Authentication flow
- API health checks
- Scheduler integration
- Trends workflow
- Error handling
- Performance tests (marked as slow)

## 📈 Performance

### Build Optimization

**Caching**:
- Docker layer caching (GitHub Actions cache)
- pip dependency caching
- Playwright browser caching

**Multi-stage Builds**:
- Backend: ~500MB final image
- Frontend: ~25MB final image

**Build Times**:
- Initial build: ~10 minutes
- Cached build: ~3-5 minutes

### Test Optimization

**Strategies**:
- Parallel test execution
- SQLite in-memory for speed
- Selective test runs (changed files only)

## 🔄 Branch Strategy

```
main (production)
  ↑
  | PR + Manual Review
  |
develop (staging)
  ↑
  | PR + Auto Checks
  |
feature/* (development)
```

**Rules**:
- `main`: Protected, requires review + CI pass
- `develop`: Protected, requires CI pass
- `feature/*`: Free development, CI runs on PR

## 🚨 Troubleshooting

### Pipeline Failures

#### Lint Failures
```bash
# Fix locally
black backend/
isort backend/
flake8 backend/
```

#### Test Failures
```bash
# Run tests locally
cd backend
pytest tests/ -v --tb=short
```

#### Build Failures
```bash
# Test Docker build locally
docker build -t test:latest backend/
docker build -t test:latest frontend/
```

#### Security Issues
```bash
# Check security locally
bandit -r backend/
safety check --file backend/requirements.txt
```

### Common Issues

**Issue**: Test coverage below 70%
**Solution**: Add more tests or adjust coverage settings

**Issue**: Docker build timeout
**Solution**: Check Dockerfile, optimize layers

**Issue**: Flaky tests
**Solution**: Add timeouts, improve test isolation

**Issue**: Dependency conflicts
**Solution**: Pin versions, check nightly test results

## 📚 Best Practices

### Commits

```bash
# Good commit messages
git commit -m "feat: add user authentication"
git commit -m "fix: resolve price parsing bug"
git commit -m "docs: update CI/CD guide"
```

### Code Quality

1. **Run checks before pushing**:
   ```bash
   black backend/ && isort backend/ && flake8 backend/
   ```

2. **Write tests for new features**:
   - Aim for >70% coverage
   - Include unit and integration tests

3. **Keep dependencies updated**:
   - Monitor nightly test results
   - Update dependencies regularly

### Pull Requests

1. **Small, focused changes**
2. **Descriptive titles and descriptions**
3. **Link related issues**
4. **Wait for CI to pass before requesting review**

## 📊 Metrics

Track these metrics:
- **Build Success Rate**: Target >95%
- **Average Build Time**: Target <10 minutes
- **Test Coverage**: Target >70%
- **Security Issues**: Target 0 high/critical

View metrics in:
- GitHub Actions dashboard
- Codecov (coverage trends)
- GitHub Security (vulnerabilities)

## 🎯 Future Enhancements

Planned improvements:
- [ ] Add code quality metrics (SonarQube)
- [ ] Implement deployment to cloud platform
- [ ] Add performance regression testing
- [ ] Set up Slack/Discord notifications
- [ ] Implement blue-green deployments
- [ ] Add canary deployments
- [ ] Set up monitoring (Prometheus/Grafana)

## 📞 Support

**Issues with CI/CD?**
1. Check workflow run logs
2. Review this guide
3. Create GitHub issue with `ci` label
4. Check #github-actions in discussions

**Need help?**
- Check GitHub Actions documentation
- Review workflow YAML files
- Contact maintainers

---

## 🎓 Quick Reference

```bash
# Local checks
black backend/ && isort backend/ && flake8 backend/ && pytest backend/tests/ -v

# Build locally
docker-compose build

# Pull latest images
docker pull ghcr.io/username/repo/backend:latest

# View workflow runs
open https://github.com/username/repo/actions

# Manual workflow trigger
gh workflow run nightly.yml
```

---

**Last Updated**: Phase 19 - CI/CD Pipeline Implementation

