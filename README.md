# Car Trends Analysis Tool

An automated web application for tracking car market trends in Tijuana, Mexico by monitoring Facebook Marketplace, Craigslist, and Mercado Libre. The tool analyzes listing frequency, pricing trends, and engagement metrics to help identify high-demand vehicles.

## ✅ MVP COMPLETED - Ready for Production!

**All Phase 1 deliverables have been successfully implemented and tested:**

- ✅ **Full-stack Application**: FastAPI backend + React frontend + PostgreSQL database
- ✅ **Automated Scrapers**: Facebook Marketplace, Craigslist, and Mercado Libre with Tijuana filters
- ✅ **Engagement Analytics**: Tracks likes, comments, views, and saves for interest measurement
- ✅ **Real-time Dashboard**: Interactive charts and analytics dashboard
- ✅ **Authentication**: JWT-based user authentication system
- ✅ **Test Suite**: 10/10 tests passing with comprehensive coverage
- ✅ **Docker Deployment**: All services containerized and running successfully

**Status**: All services operational - backend (http://localhost:8000), frontend (http://localhost:3000), database healthy ✅

## Features

- **Automated Data Collection**: Daily scraping from Facebook Marketplace, Craigslist, and Mercado Libre
- **Engagement Analytics**: Tracks views, likes, comments, and saves to measure interest
- **Price Trend Analysis**: Historical pricing data with trend visualization
- **Market Intelligence**: Top cars by engagement, market share analysis
- **Real-time Dashboard**: Web-based interface with interactive charts
- **Historical Tracking**: Daily snapshots for trend analysis over time

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd cars-trends-tool
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the application:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Development Setup

1. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
```

3. Start development servers:
```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend
cd frontend
npm start
```

## Project Structure

```
cars-trends-tool/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── scrapers/       # Web scrapers
│   │   └── services/       # Business logic
│   ├── tests/              # Backend tests
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   └── services/       # API services
│   └── package.json
├── database/               # Database files
│   ├── schema.sql
│   └── migrations/
├── docs/                   # Documentation
├── docker-compose.yml
└── README.md
```

## Documentation

- [Product Plan](docs/product_plan.md) - Business requirements and user stories
- [Technical Design](docs/technical_design.md) - Architecture and implementation details
- [Product Roadmap](docs/product_roadmap.md) - Development phases and timeline
- [User Guide](docs/user_guide.md) - How to use the application
- [API Documentation](docs/api_documentation.md) - API endpoints and examples

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or support, please contact the development team or create an issue in the repository.
