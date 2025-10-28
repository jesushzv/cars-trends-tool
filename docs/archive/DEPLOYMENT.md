# Local Deployment Guide

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Docker Desktop installed and running
- At least 4GB RAM available
- Ports 3000, 5432, 6379, and 8000 available

### Step-by-Step Deployment

#### 1. Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings (optional for local development)
nano .env
```

**Important Settings:**
- `DATABASE_URL`: PostgreSQL connection string (default works for Docker)
- `SECRET_KEY`: Change this for production! Generate with: `openssl rand -hex 32`
- `REACT_APP_API_URL`: Frontend API endpoint (default: http://localhost:8000)

#### 2. Start All Services
```bash
# Start all services in detached mode
docker-compose up -d

# Or start with logs visible
docker-compose up
```

This will start:
- **PostgreSQL Database** on port 5432
- **Redis Cache** on port 6379
- **Backend API** on port 8000
- **Frontend Dashboard** on port 3000

#### 3. Verify Services are Running
```bash
# Check status of all services
docker-compose ps

# View logs for all services
docker-compose logs

# View logs for specific service
docker-compose logs backend
docker-compose logs frontend
```

#### 4. Access the Application
- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

#### 5. Create First User
```bash
# Access the backend container
docker-compose exec backend python

# In Python shell, create a user:
```python
from app.core.database import database
from app.services.user_service import UserService
from app.schemas.auth import UserCreate
import asyncio

async def create_user():
    await database.connect()
    user_service = UserService(database)
    user_data = UserCreate(
        email="admin@example.com",
        password="changeme123"
    )
    user = await user_service.create_user(user_data)
    print(f"User created: {user.email}")
    await database.disconnect()

asyncio.run(create_user())
```

Or use the API directly:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"changeme123"}'
```

## 🔧 Managing the Application

### Starting Services
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend
```

### Stopping Services
```bash
# Stop all services
docker-compose down

# Stop all services and remove volumes (⚠️ deletes all data)
docker-compose down -v
```

### Restarting Services
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Viewing Logs
```bash
# Follow logs for all services
docker-compose logs -f

# Follow logs for specific service
docker-compose logs -f backend

# View last 100 lines
docker-compose logs --tail=100 backend
```

### Rebuilding Services (after code changes)
```bash
# Rebuild and restart all services
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build backend
```

## 🧪 Running Tests

### Backend Tests
```bash
# Run all tests
docker-compose exec backend python -m pytest tests/ -v

# Run with coverage
docker-compose exec backend python -m pytest tests/ --cov=app --cov-report=html

# Run specific test file
docker-compose exec backend python -m pytest tests/test_scrapers.py -v
```

### View Test Coverage
```bash
docker-compose exec backend python -m pytest tests/ --cov=app --cov-report=term-missing
```

## 🔍 Troubleshooting

### Services Won't Start

**Check if ports are already in use:**
```bash
# Check port 3000 (frontend)
lsof -i :3000

# Check port 8000 (backend)
lsof -i :8000

# Check port 5432 (database)
lsof -i :5432
```

**Kill processes using ports:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Database Connection Issues

**Check database health:**
```bash
docker-compose exec db pg_isready -U user -d car_trends_db
```

**Reset database:**
```bash
# ⚠️ This will delete all data
docker-compose down -v
docker-compose up -d
```

**Manually connect to database:**
```bash
docker-compose exec db psql -U user -d car_trends_db
```

### Backend Not Responding

**Check backend logs:**
```bash
docker-compose logs backend --tail=100
```

**Common issues:**
- Database not ready → Wait 10-15 seconds and check again
- Missing environment variables → Check `.env` file
- Port conflicts → Stop other services using port 8000

**Restart backend:**
```bash
docker-compose restart backend
```

### Frontend Not Loading

**Check frontend logs:**
```bash
docker-compose logs frontend --tail=100
```

**Common issues:**
- Backend not running → Start backend first
- CORS issues → Check `REACT_APP_API_URL` in `.env`
- Build errors → Rebuild with `docker-compose up -d --build frontend`

### Clear Everything and Start Fresh
```bash
# Stop all services
docker-compose down

# Remove all volumes (⚠️ deletes all data)
docker-compose down -v

# Remove all Docker images for this project
docker-compose down --rmi all

# Rebuild and start everything
docker-compose up -d --build
```

## 📊 Running Scrapers Manually

### Trigger Scraper via API
```bash
# Get authentication token first
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"changeme123"}' | jq -r '.access_token')

# Trigger Facebook Marketplace scraper
curl -X POST "http://localhost:8000/api/v1/scrapers/facebook/trigger" \
  -H "Authorization: Bearer $TOKEN"

# Trigger Craigslist scraper
curl -X POST "http://localhost:8000/api/v1/scrapers/craigslist/trigger" \
  -H "Authorization: Bearer $TOKEN"

# Trigger Mercado Libre scraper
curl -X POST "http://localhost:8000/api/v1/scrapers/mercadolibre/trigger" \
  -H "Authorization: Bearer $TOKEN"
```

### Run Scraper from Command Line
```bash
# Access backend container
docker-compose exec backend python

# Run scraper in Python:
```python
from app.scrapers.facebook_marketplace import FacebookMarketplaceScraper
from app.core.database import database
import asyncio

async def run_scraper():
    await database.connect()
    scraper = FacebookMarketplaceScraper(database)
    result = await scraper.scrape()
    print(f"Found {result['listings_found']} listings")
    await database.disconnect()

asyncio.run(run_scraper())
```

## 🔒 Security Considerations

### For Local Development
The default configuration is suitable for local development.

### For Production Deployment
1. **Change SECRET_KEY**: Generate a strong random key
   ```bash
   openssl rand -hex 32
   ```

2. **Update database credentials**: Use strong passwords

3. **Enable HTTPS**: Use a reverse proxy (nginx, traefik)

4. **Set proper CORS origins**: Update `BACKEND_CORS_ORIGINS` in backend config

5. **Use environment-specific .env files**

6. **Enable database backups**

7. **Set up monitoring and logging**

## 📈 Performance Optimization

### Increase Database Performance
```yaml
# Add to docker-compose.yml under db service
environment:
  - POSTGRES_SHARED_BUFFERS=256MB
  - POSTGRES_WORK_MEM=16MB
```

### Increase Backend Workers
```yaml
# Update backend command in docker-compose.yml
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Enable Redis Caching
Redis is already configured and running. The backend will automatically use it for caching API responses.

## 🔄 Database Migrations

### View Current Schema
```bash
docker-compose exec db psql -U user -d car_trends_db -c "\dt"
```

### Backup Database
```bash
docker-compose exec db pg_dump -U user car_trends_db > backup.sql
```

### Restore Database
```bash
docker-compose exec -T db psql -U user car_trends_db < backup.sql
```

## 📱 Accessing from Other Devices

To access the dashboard from other devices on your local network:

1. Find your local IP address:
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

2. Update `.env`:
   ```
   REACT_APP_API_URL=http://YOUR_LOCAL_IP:8000
   ```

3. Restart services:
   ```bash
   docker-compose restart
   ```

4. Access from other devices:
   - Frontend: http://YOUR_LOCAL_IP:3000
   - Backend: http://YOUR_LOCAL_IP:8000

## 🎯 Next Steps

1. ✅ Services running → Login at http://localhost:3000
2. ✅ Create first user → Use registration endpoint or Python script
3. ✅ Run first scrape → Trigger via API or dashboard
4. ✅ View results → Check dashboard for trends and analytics
5. ✅ Schedule daily runs → Already configured with APScheduler (runs at 2 AM daily)

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Product Plan**: `docs/product_plan.md`
- **Technical Design**: `docs/technical_design.md`
- **User Guide**: `docs/user_guide.md`
- **Development Guide**: `docs/development_guide.md`

## ❓ Need Help?

Check the logs first:
```bash
docker-compose logs backend --tail=100
docker-compose logs frontend --tail=100
```

Common commands:
```bash
# Health check
curl http://localhost:8000/health

# Test database connection
docker-compose exec backend python -c "from app.core.database import database; import asyncio; asyncio.run(database.connect()); print('Connected!')"
```


