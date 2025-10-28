# Car Trends Analysis Tool

![CI/CD](https://github.com/jesushzv/cars-trends-tool/actions/workflows/ci-cd.yml/badge.svg)
![PR Checks](https://github.com/jesushzv/cars-trends-tool/actions/workflows/pr-checks.yml/badge.svg)
![Nightly Tests](https://github.com/jesushzv/cars-trends-tool/actions/workflows/nightly.yml/badge.svg)
[![codecov](https://codecov.io/gh/jesushzv/cars-trends-tool/branch/main/graph/badge.svg)](https://codecov.io/gh/jesushzv/cars-trends-tool)

An automated web application for tracking car market trends in Tijuana, Mexico by monitoring Facebook Marketplace, Craigslist, and Mercado Libre. The tool analyzes listing frequency, pricing trends, and market dynamics to help identify high-demand vehicles.

## ✅ Production Ready with CI/CD!

**Complete features implemented and tested:**

- ✅ **Full-stack Application**: FastAPI backend + Vanilla JS frontend + PostgreSQL database
- ✅ **Automated Scrapers**: Facebook Marketplace, Craigslist, and Mercado Libre with Tijuana filters
- ✅ **Price Trend Analysis**: Historical pricing data with trend visualization
- ✅ **Market Intelligence**: Top cars, market share analysis, trending vehicles
- ✅ **Real-time Dashboard**: Web-based interface with interactive charts
- ✅ **Authentication**: JWT-based user authentication system
- ✅ **Automated Scheduling**: Daily scraping and data snapshots
- ✅ **CI/CD Pipeline**: Automated testing, building, and deployment
- ✅ **Docker Deployment**: All services containerized and production-ready
- ✅ **Test Coverage**: 72% coverage with comprehensive E2E tests

**Status**: Production-ready with automated CI/CD pipeline ✅

## Features

- **Automated Data Collection**: Daily scraping from Facebook Marketplace, Craigslist, and Mercado Libre
- **Price Trend Analysis**: Historical pricing data with trend visualization
- **Market Intelligence**: Top cars, market share analysis, platform comparison
- **Trending Vehicles**: Identify cars trending up or down in the market
- **Real-time Dashboard**: Web-based interface with interactive charts
- **Historical Tracking**: Daily snapshots for trend analysis over time
- **User Authentication**: Secure JWT-based authentication system
- **Automated Scheduling**: Background jobs for daily scraping and analysis
- **CI/CD Pipeline**: Automated testing, security scanning, and Docker image building

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.13+ (for local development)
- Git

### Docker Installation (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/jesushzv/cars-trends-tool.git
cd cars-trends-tool
```

2. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your configuration (optional for defaults)
```

3. Start the application:
```bash
docker-compose up -d
```

4. Access the application:
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Local Development Setup

1. Install backend dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Set up database:
```bash
# For PostgreSQL (recommended)
./setup_postgres.sh
python migrate_to_postgres.py

# Or use SQLite (development only)
export USE_SQLITE_FALLBACK=true
```

3. Start development server:
```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend (just open index.html or use a simple HTTP server)
cd frontend
python -m http.server 8080
```

4. Access the application:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000

## Project Structure

```
cars-trends-tool/
├── .github/
│   └── workflows/          # CI/CD workflows
├── backend/                # FastAPI backend
│   ├── app/               # Main application
│   ├── models/            # Database models
│   ├── scrapers/          # Web scrapers
│   ├── services/          # Business logic
│   ├── tests/             # Backend tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .flake8            # Code quality config
├── frontend/              # Vanilla JS frontend
│   ├── index.html         # Main HTML file
│   ├── Dockerfile
│   └── nginx.conf         # Nginx configuration
├── database/              # Database schema
│   └── schema.sql
├── docs/                  # Documentation
│   ├── archive/           # Historical docs
│   ├── api_documentation.md
│   ├── development_guide.md
│   └── technical_design.md
├── docker-compose.yml     # Docker orchestration
├── env.example            # Environment variables template
├── DOCKER_DEPLOYMENT.md   # Deployment guide
├── CI_CD_GUIDE.md         # CI/CD documentation
└── README.md
```

## Documentation

### User Guides
- **[CICD Quick Start](CICD_QUICKSTART.md)** - Get started with development workflow
- **[Docker Deployment](DOCKER_DEPLOYMENT.md)** - Production deployment guide
- **[User Guide](docs/user_guide.md)** - How to use the application

### Technical Documentation
- **[CI/CD Guide](CI_CD_GUIDE.md)** - Comprehensive CI/CD pipeline documentation
- **[API Documentation](docs/api_documentation.md)** - API endpoints and examples
- **[Technical Design](docs/technical_design.md)** - Architecture and implementation
- **[Development Guide](docs/development_guide.md)** - Development best practices

### Planning Documents
- [Product Plan](docs/product_plan.md) - Business requirements
- [Product Roadmap](docs/product_roadmap.md) - Development timeline

## Contributing

We use a CI/CD pipeline to ensure code quality. Here's how to contribute:

### Development Workflow

1. **Fork and clone** the repository:
```bash
git clone https://github.com/jesushzv/cars-trends-tool.git
cd cars-trends-tool
```

2. **Create a feature branch**:
```bash
git checkout -b feature/your-feature-name
```

3. **Make your changes** and ensure code quality:
```bash
cd backend
black .          # Format code
isort .          # Sort imports  
flake8 .         # Lint code
pytest tests/ -v # Run tests
```

4. **Commit your changes**:
```bash
git add .
git commit -m "feat: add your feature description"
```

5. **Push and create a pull request**:
```bash
git push origin feature/your-feature-name
```

6. **Wait for CI/CD checks** - Your PR will automatically:
   - Run all tests
   - Check code quality (linting, formatting)
   - Scan for security vulnerabilities
   - Build Docker images

7. **Address any feedback** and get your PR merged!

### Code Standards
- **Python**: Follow PEP 8, use black formatter
- **Tests**: Maintain >70% code coverage
- **Documentation**: Update docs for new features
- **Commits**: Use conventional commit messages (feat:, fix:, docs:, etc.)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or support, please contact the development team or create an issue in the repository.
