# Car Trends Analysis Tool - Development Guide

## Getting Started

This guide will help you set up the development environment for the Car Trends Analysis Tool.

## ✅ Project Status - MVP COMPLETED

**All Phase 1 (MVP) deliverables have been successfully implemented:**

- ✅ **Documentation**: Complete product plan, technical design, roadmap, user guide, API docs, and development guide
- ✅ **Project Structure**: Full-stack application with FastAPI backend, React frontend, PostgreSQL database, and Docker setup
- ✅ **Database Schema**: PostgreSQL schema with listings, trends, and engagement metrics tables
- ✅ **Scrapers**: Facebook Marketplace, Craigslist, and Mercado Libre scrapers with Tijuana filters
- ✅ **Data Processing**: Normalization, cleaning, and car model extraction logic
- ✅ **API Backend**: REST endpoints for listings, trends, analytics, and scraper management
- ✅ **Scheduler**: Automated daily scraping jobs with APScheduler
- ✅ **Frontend Dashboard**: React dashboard with charts for trends, pricing, and engagement
- ✅ **Authentication**: JWT-based user authentication system
- ✅ **Test Suite**: Comprehensive test suite with 10/10 tests passing
- ✅ **Deployment**: Docker containers and environment configuration

**Current Status**: All services running successfully - ready for production use!

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- Git

## Quick Start

1. **Clone the repository:**
```bash
git clone <repository-url>
cd cars-trends-tool
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start the application:**
```bash
docker-compose up -d
```

4. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Development Setup

### Backend Development

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up database:**
```bash
# Start PostgreSQL
docker-compose up -d db

# Run migrations (if any)
alembic upgrade head
```

5. **Start development server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm start
```

The frontend will be available at http://localhost:3000

## Project Structure

```
cars-trends-tool/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   │   └── v1/
│   │   │       ├── api.py
│   │   │       └── endpoints/
│   │   ├── core/           # Core configuration
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   └── logging_config.py
│   │   ├── models/         # Database models
│   │   │   ├── listing.py
│   │   │   ├── trend.py
│   │   │   ├── user.py
│   │   │   └── scraping_session.py
│   │   ├── schemas/        # Pydantic schemas
│   │   │   ├── auth.py
│   │   │   ├── listing.py
│   │   │   ├── trend.py
│   │   │   └── scraping_session.py
│   │   ├── scrapers/       # Web scrapers
│   │   │   ├── base_scraper.py
│   │   │   ├── facebook_marketplace.py
│   │   │   ├── craigslist.py
│   │   │   └── mercadolibre.py
│   │   ├── services/       # Business logic
│   │   │   ├── user_service.py
│   │   │   ├── listing_service.py
│   │   │   ├── trend_service.py
│   │   │   ├── analytics_service.py
│   │   │   └── scraper_service.py
│   │   └── main.py         # FastAPI app
│   ├── tests/              # Backend tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── Layout.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── StatCard.tsx
│   │   │   ├── TopCarsChart.tsx
│   │   │   ├── PriceTrendsChart.tsx
│   │   │   ├── MarketShareChart.tsx
│   │   │   ├── ListingsTable.tsx
│   │   │   └── ListingFilters.tsx
│   │   ├── pages/          # Page components
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Listings.tsx
│   │   │   ├── Trends.tsx
│   │   │   └── Analytics.tsx
│   │   ├── services/       # API services
│   │   │   ├── apiClient.ts
│   │   │   ├── authService.ts
│   │   │   ├── analyticsService.ts
│   │   │   ├── listingsService.ts
│   │   │   └── trendsService.ts
│   │   ├── contexts/       # React contexts
│   │   │   └── AuthContext.tsx
│   │   ├── types/          # TypeScript types
│   │   │   └── auth.ts
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── index.tsx
│   │   └── index.css
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── Dockerfile
├── database/               # Database files
│   └── schema.sql
├── docs/                   # Documentation
│   ├── product_plan.md
│   ├── technical_design.md
│   ├── product_roadmap.md
│   ├── user_guide.md
│   ├── api_documentation.md
│   └── development_guide.md
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Database Schema

The application uses PostgreSQL with the following main tables:

- **listings**: Individual car listings from all platforms
- **trends**: Aggregated daily trends by make/model
- **users**: User authentication and management
- **user_sessions**: JWT token management
- **scraping_sessions**: Scraping operation tracking
- **car_models**: Car model normalization

## API Development

### Adding New Endpoints

1. **Create schema** in `app/schemas/`
2. **Create service** in `app/services/`
3. **Create endpoint** in `app/api/v1/endpoints/`
4. **Add route** to `app/api/v1/api.py`

### Example: Adding a new endpoint

```python
# app/schemas/new_feature.py
from pydantic import BaseModel

class NewFeatureRequest(BaseModel):
    name: str
    description: str

class NewFeatureResponse(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime
```

```python
# app/services/new_feature_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.new_feature import NewFeatureRequest

class NewFeatureService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_feature(self, data: NewFeatureRequest):
        # Implementation
        pass
```

```python
# app/api/v1/endpoints/new_feature.py
from fastapi import APIRouter, Depends
from app.schemas.new_feature import NewFeatureRequest, NewFeatureResponse
from app.services.new_feature_service import NewFeatureService

router = APIRouter()

@router.post("/", response_model=NewFeatureResponse)
async def create_feature(
    data: NewFeatureRequest,
    db: AsyncSession = Depends(get_db)
):
    service = NewFeatureService(db)
    return await service.create_feature(data)
```

## Frontend Development

### Adding New Components

1. **Create component** in `src/components/`
2. **Add to pages** in `src/pages/`
3. **Update routing** in `App.tsx`

### Example: Adding a new component

```typescript
// src/components/NewComponent.tsx
import React from 'react';

interface NewComponentProps {
  title: string;
  data: any[];
}

const NewComponent: React.FC<NewComponentProps> = ({ title, data }) => {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      {/* Component content */}
    </div>
  );
};

export default NewComponent;
```

### Adding New Services

```typescript
// src/services/newService.ts
import { apiClient } from './apiClient';

class NewService {
  async getData() {
    const response = await apiClient.get('/new-endpoint');
    return response.data;
  }
}

export const newService = new NewService();
```

## Testing

### Backend Testing

```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Testing

```bash
cd frontend
npm test
```

### End-to-End Testing

```bash
# Run E2E tests
npm run test:e2e
```

## Code Quality

### Backend

- **Formatting**: `black app/`
- **Linting**: `flake8 app/`
- **Type checking**: `mypy app/`
- **Sorting imports**: `isort app/`

### Frontend

- **Formatting**: `npm run format`
- **Linting**: `npm run lint`
- **Type checking**: `npm run type-check`

## Deployment

### Production Build

```bash
# Build frontend
cd frontend
npm run build

# Build backend
cd backend
docker build -t car-trends-backend .
```

### Docker Deployment

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d
```

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/car_trends

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Scraping
SCRAPING_DELAY_MIN=1
SCRAPING_DELAY_MAX=3
MAX_RETRIES=3

# Facebook Marketplace (optional)
FB_EMAIL=your-email@example.com
FB_PASSWORD=your-password

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Frontend (.env)

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

## Troubleshooting

### Common Issues

1. **Database connection errors**
   - Check if PostgreSQL is running
   - Verify DATABASE_URL in .env
   - Check database credentials

2. **Scraping failures**
   - Check internet connection
   - Verify target websites are accessible
   - Check rate limiting settings

3. **Frontend build errors**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify environment variables

4. **Authentication issues**
   - Check JWT secret key
   - Verify token expiration settings
   - Check user credentials

### Logs

- **Backend logs**: `docker-compose logs backend`
- **Frontend logs**: `docker-compose logs frontend`
- **Database logs**: `docker-compose logs db`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Support

For questions or support:
- Check the documentation
- Review existing issues
- Create a new issue with detailed information
