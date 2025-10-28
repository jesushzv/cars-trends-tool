# CI/CD Quick Start Guide
**Cars Trends Tool - Phase 19**

## 🚀 Getting Started with CI/CD

### First Time Setup

#### 1. Enable GitHub Container Registry (GHCR)

The workflows are already configured to push to GHCR. When you push to GitHub, it will automatically use the `GITHUB_TOKEN` to authenticate.

**No additional setup needed!** GitHub Actions automatically provides the token.

#### 2. (Optional) Add Code Coverage Badge

If you want code coverage tracking:

1. Go to [codecov.io](https://codecov.io)
2. Sign in with GitHub
3. Enable your repository
4. Copy the upload token
5. Add as GitHub secret: `CODECOV_TOKEN`

**Or skip this** - the pipeline works without it!

#### 3. Update Badge URLs in README

Edit `README.md` and replace `username` with your GitHub username:

```markdown
![CI/CD](https://github.com/YOUR_USERNAME/cars-trends-tool/actions/workflows/ci-cd.yml/badge.svg)
![PR Checks](https://github.com/YOUR_USERNAME/cars-trends-tool/actions/workflows/pr-checks.yml/badge.svg)
```

### Daily Workflow

#### Creating a Feature

```bash
# 1. Create feature branch
git checkout -b feature/my-awesome-feature

# 2. Make changes
# ... edit files ...

# 3. (Optional) Run checks locally
cd backend
black .
flake8 .
pytest tests/ -v

# 4. Commit and push
git add .
git commit -m "feat: add awesome feature"
git push origin feature/my-awesome-feature
```

#### Creating a Pull Request

1. Go to GitHub
2. Click "Compare & pull request"
3. Write description
4. Click "Create pull request"
5. **Wait for CI checks to pass** ✅
6. Request review
7. Merge when approved!

**The Pipeline Automatically**:
- ✅ Lints your code
- ✅ Runs all tests
- ✅ Checks security
- ✅ Builds Docker images
- ✅ Shows results in PR

#### Deploying to Staging

```bash
# Merge to develop branch
git checkout develop
git merge feature/my-awesome-feature
git push origin develop
```

**Automatic Actions**:
- 🧪 Runs all tests
- 🐳 Builds Docker images
- 📤 Pushes to GHCR with `develop` tag
- 📊 Creates deployment summary

#### Deploying to Production

```bash
# Merge to main branch
git checkout main
git merge develop
git push origin main
```

**Automatic Actions**:
- 🧪 Runs all tests
- 🐳 Builds multi-arch Docker images
- 📤 Pushes to GHCR with `latest` and `main` tags
- 📦 Creates GitHub release
- 📢 Deployment ready notification

### Pulling Docker Images

Once images are published, anyone can pull them:

```bash
# Latest production version
docker pull ghcr.io/YOUR_USERNAME/cars-trends-tool/backend:latest
docker pull ghcr.io/YOUR_USERNAME/cars-trends-tool/frontend:latest

# Development version
docker pull ghcr.io/YOUR_USERNAME/cars-trends-tool/backend:develop
docker pull ghcr.io/YOUR_USERNAME/cars-trends-tool/frontend:develop

# Specific commit
docker pull ghcr.io/YOUR_USERNAME/cars-trends-tool/backend:main-abc123
```

### Using Published Images

Update `docker-compose.yml`:

```yaml
services:
  backend:
    image: ghcr.io/YOUR_USERNAME/cars-trends-tool/backend:latest
    # Remove 'build' section
  
  frontend:
    image: ghcr.io/YOUR_USERNAME/cars-trends-tool/frontend:latest
    # Remove 'build' section
```

Then:

```bash
docker-compose pull
docker-compose up -d
```

## 📊 Monitoring

### View Workflow Runs

```bash
# Open GitHub Actions dashboard
open https://github.com/YOUR_USERNAME/cars-trends-tool/actions
```

### Check Build Status

Status badges in README show current status:
- ✅ Green = All checks pass
- ❌ Red = Some checks failed
- 🟡 Yellow = In progress

### Download Build Artifacts

1. Go to GitHub Actions
2. Click on a workflow run
3. Scroll to "Artifacts" section
4. Download coverage reports, test results, etc.

## 🐛 Troubleshooting

### CI Fails with "Linting Errors"

```bash
# Fix locally
cd backend
black .
isort .
flake8 .
```

### CI Fails with "Tests Failed"

```bash
# Run tests locally
cd backend
pytest tests/ -v
```

### CI Fails with "Docker Build Error"

```bash
# Test Docker build locally
docker build -t test:latest backend/
docker build -t test:latest frontend/
```

### "Permission Denied" for GHCR

The `GITHUB_TOKEN` should have write access to packages automatically.
If you get permission errors, check your repository settings:
- Settings → Actions → General
- Workflow permissions → Read and write permissions

## 📚 Commands Cheat Sheet

```bash
# Run all checks locally
cd backend && black . && isort . && flake8 . && pytest tests/ -v

# Run specific test file
pytest tests/test_e2e.py -v

# Run tests without slow tests
pytest tests/ -v -m "not slow"

# Check coverage
pytest tests/ --cov=. --cov-report=html

# Security scan
bandit -r backend/
safety check --file backend/requirements.txt

# Build Docker images
docker-compose build

# View workflow logs (requires gh CLI)
gh run list
gh run view
```

## 🎯 Best Practices

1. **Always run checks locally before pushing**
2. **Write tests for new features**
3. **Keep commits small and focused**
4. **Use descriptive commit messages**
5. **Wait for CI to pass before requesting review**
6. **Don't merge failing PRs**
7. **Monitor nightly test results**

## 💡 Tips

- **Use `git commit -m "feat: "`** for new features
- **Use `git commit -m "fix: "`** for bug fixes
- **Use `git commit -m "docs: "`** for documentation
- **Add `[skip ci]`** to commit message to skip CI (use sparingly!)

## 🆘 Need Help?

1. Check `CI_CD_GUIDE.md` for detailed documentation
2. Review workflow files in `.github/workflows/`
3. Check GitHub Actions logs for specific errors
4. Create an issue with `ci` label

## 🎉 You're Ready!

Your CI/CD pipeline is fully operational. Just:
1. Create feature branch
2. Make changes
3. Push to GitHub
4. Create PR
5. Watch the magic happen! ✨

---

**Next Steps**: Set up cloud deployment (Phase 20) 🚀

