# Docker Deployment Guide
**Cars Trends Tool - Phase 18**

Complete guide for deploying the Cars Trends Tool using Docker and Docker Compose.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB free disk space
- Ports 80, 8000, and 5432 available

## 🚀 Quick Start

### 1. Clone and Configure

```bash
# Navigate to project directory
cd cars-trends-tool

# Copy environment file
cp env.example .env

# Edit environment variables (optional)
nano .env
```

### 2. Build and Start

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Access Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

## 📦 Services

### PostgreSQL Database
- **Port**: 5432
- **Database**: carstrends
- **User**: carstrends
- **Password**: Set in `.env`
- **Data Volume**: `carstrends-postgres-data`

### Backend API (FastAPI)
- **Port**: 8000
- **Framework**: FastAPI + Uvicorn
- **Python**: 3.13
- **Features**: REST API, Scraping, Analytics

### Frontend (Nginx)
- **Port**: 80
- **Server**: Nginx Alpine
- **Content**: Static HTML/CSS/JS

## 🔧 Configuration

### Environment Variables

Create `.env` file from `env.example`:

```bash
# Database
POSTGRES_DB=carstrends
POSTGRES_USER=carstrends
POSTGRES_PASSWORD=your_secure_password
POSTGRES_PORT=5432

# Application Ports
BACKEND_PORT=8000
FRONTEND_PORT=80
```

### Custom Ports

To use different ports:

```bash
# In .env file
FRONTEND_PORT=3000
BACKEND_PORT=8080
POSTGRES_PORT=5433
```

Then access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8080

## 📊 Database Management

### Access PostgreSQL

```bash
# Connect to database
docker-compose exec postgres psql -U carstrends -d carstrends

# Common commands
\dt                  # List tables
\d listings          # Describe table
SELECT COUNT(*) FROM listings;
```

### Backup Database

```bash
# Create backup
docker-compose exec postgres pg_dump -U carstrends carstrends > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U carstrends -d carstrends < backup.sql
```

### Initialize Database

Database tables are created automatically on first run. To reset:

```bash
# Stop services
docker-compose down -v

# Start services (fresh database)
docker-compose up -d
```

## 🔍 Troubleshooting

### Check Service Health

```bash
# Check all services
docker-compose ps

# Check specific service logs
docker-compose logs backend
docker-compose logs postgres
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f backend
```

### Common Issues

#### Port Already in Use

```bash
# Change ports in .env file
FRONTEND_PORT=8080
BACKEND_PORT=8001
```

#### Database Connection Failed

```bash
# Check if postgres is healthy
docker-compose ps

# Wait for database to be ready
docker-compose logs postgres

# Restart backend
docker-compose restart backend
```

#### Permission Denied

```bash
# Fix volume permissions
docker-compose down
sudo chown -R $USER:$USER .
docker-compose up -d
```

#### Out of Disk Space

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune
```

## 🧪 Testing

### Health Checks

All services have built-in health checks:

```bash
# Check backend health
curl http://localhost:8000/

# Check frontend health
curl http://localhost/

# Check all services
docker-compose ps
```

### Run API Tests

```bash
# Enter backend container
docker-compose exec backend bash

# Run tests
pytest tests/ -v

# Exit container
exit
```

### Manual Scraping

```bash
# Trigger scraping via API
curl -X POST http://localhost:8000/scrape/craigslist
curl -X POST http://localhost:8000/scrape/mercadolibre

# Check logs
docker-compose logs -f backend
```

## 🔐 Security

### Production Checklist

- [ ] Change default passwords in `.env`
- [ ] Set secure `JWT_SECRET_KEY`
- [ ] Use HTTPS (add reverse proxy)
- [ ] Enable firewall rules
- [ ] Regular backups
- [ ] Keep Docker images updated

### HTTPS with Nginx Reverse Proxy

Add to `docker-compose.yml`:

```yaml
  nginx-proxy:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx-ssl.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl
```

## 📈 Monitoring

### View Resource Usage

```bash
# Real-time stats
docker stats

# Service-specific stats
docker stats carstrends-backend
```

### Logs Management

```bash
# View last 100 lines
docker-compose logs --tail=100

# Save logs to file
docker-compose logs > logs.txt

# Clear logs (restart containers)
docker-compose restart
```

## 🔄 Updates

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Update Database

```bash
# Run migration
docker-compose exec backend python migrate_to_postgres.py
```

## 🗂️ Data Persistence

Data is persisted in Docker volumes:

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect carstrends-postgres-data

# Backup volume
docker run --rm \
  -v carstrends-postgres-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/db-backup.tar.gz /data
```

## 🚦 Production Deployment

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml carstrends

# Check services
docker service ls
```

### Kubernetes

Convert with Kompose:

```bash
# Install kompose
curl -L https://github.com/kubernetes/kompose/releases/download/v1.26.0/kompose-linux-amd64 -o kompose
chmod +x kompose
sudo mv kompose /usr/local/bin/

# Convert to Kubernetes
kompose convert

# Deploy
kubectl apply -f .
```

## 📚 Useful Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart service
docker-compose restart backend

# View logs
docker-compose logs -f

# Execute command in container
docker-compose exec backend bash

# Rebuild specific service
docker-compose build backend

# Scale service (if stateless)
docker-compose up -d --scale backend=3

# Remove everything (including volumes)
docker-compose down -v
docker system prune -a
```

## 🆘 Support

If you encounter issues:

1. Check service health: `docker-compose ps`
2. View logs: `docker-compose logs -f`
3. Verify environment: `cat .env`
4. Test connectivity: `docker-compose exec backend ping postgres`
5. Restart services: `docker-compose restart`

For more help, check:
- Docker documentation: https://docs.docker.com/
- Docker Compose documentation: https://docs.docker.com/compose/
- Project README: `/README.md`

