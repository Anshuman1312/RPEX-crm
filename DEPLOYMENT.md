# RPEX CRM – Production Deployment Guide

## Overview

This guide documents the production deployment process for the RPEX CRM system. The system is composed of:
- **FastAPI Backend** (Python 3.14) with PostgreSQL + Redis
- **React Frontend** (Vite + TypeScript)
- **Nginx** (Reverse proxy + SSL termination)
- **Docker Compose** (Container orchestration)

**Status**: Production-ready (Step 20 complete)
- **134 REST API routes** across 15 modules
- **32 PostgreSQL tables** with migrations
- **Complete security hardening** (CORS, rate limiting, security headers)
- **Health checks & monitoring** endpoints

---

## Prerequisites

- Docker & Docker Compose (v1.29+)
- Domain with DNS configured
- SSL certificate (Let's Encrypt recommended)
- Min 2GB RAM, 20GB disk space

---

## Quick Start

### 1. Clone & Configure

```bash
git clone <repository-url> /opt/rpex-crm
cd /opt/rpex-crm
cp .env.example .env
```

### 2. Update .env for Production

```bash
# Database
DB_USER=rpex_prod
DB_PASSWORD=<generate-secure-password>
DB_NAME=rpex_crm_prod

# Redis
REDIS_PASSWORD=<generate-secure-password>

# FastAPI
ENVIRONMENT=production
SECRET_KEY=<generate-min-32-char-key>
CORS_ORIGINS=["https://rpex.com", "https://www.rpex.com"]
ALLOWED_HOSTS=["rpex.com", "www.rpex.com", "api.rpex.com"]

# Frontend
VITE_API_URL=https://api.rpex.com

# Email
SMTP_HOST=<smtp-server>
SMTP_USER=<email>
SMTP_PASSWORD=<password>
```

### 3. Initialize Database & Seed Data

```bash
# Pull and build images
docker-compose pull
docker-compose build

# Start database services
docker-compose up -d postgres redis

# Wait for PostgreSQL to be healthy (30s)
sleep 30

# Run migrations
docker-compose exec backend alembic upgrade head

# Seed initial data
docker-compose exec backend python scripts/seed_data.py
```

### 4. Start All Services

```bash
docker-compose up -d
docker-compose ps
```

Verify all services are running and healthy.

### 5. Configure SSL/HTTPS

#### Option A: Let's Encrypt (Recommended)

```bash
# Use certbot to obtain certificate
docker-compose exec certbot certbot certonly \
  --webroot -w /var/www/certbot \
  -d rpex.com -d www.rpex.com \
  -d api.rpex.com

# Update nginx config with certificate paths
# See: infra/nginx/conf.d/default.conf
```

#### Option B: Bring Your Own Certificate

```bash
cp your-cert.pem infra/nginx/letsencrypt/live/domain/fullchain.pem
cp your-key.pem infra/nginx/letsencrypt/live/domain/privkey.pem
```

### 6. Validate Production Readiness

```bash
docker-compose exec backend python scripts/validate_production.py
```

Expected output:
```
✅ PASS: Database Connectivity
✅ PASS: Alembic Migrations  
✅ PASS: Seed Data
✅ PASS: SQLAlchemy Models
✅ PASS: API Routes
✅ PASS: Security Configuration
✅ PASS: Environment Variables
✅ PASS: Docker Compose

🎉 All critical validations passed! System is production-ready.
```

---

## Architecture

### Services Topology

```
┌─────────────────────────────────────────┐
│           Client (Browser)              │
└─────────────┬───────────────────────────┘
              │ HTTPS
┌─────────────▼───────────────────────────┐
│        Nginx (Reverse Proxy)            │
│  ✓ SSL/TLS termination                  │
│  ✓ Rate limiting (100 req/s API)        │
│  ✓ Security headers                     │
│  ✓ Gzip compression                     │
└──────┬──────────────────────┬───────────┘
       │ HTTP                 │ HTTP
       ▼                      ▼
┌─────────────┐         ┌──────────────┐
│   Backend   │         │   Frontend   │
│ (FastAPI)   │         │   (React)    │
│ 4 workers   │         │   Vite       │
│ Gunicorn    │         │   Node.js    │
└──────┬──────┘         └──────────────┘
       │
   ┌───┴────────────────┐
   │                    │
   ▼                    ▼
┌──────────┐       ┌──────────┐
│PostgreSQL│       │  Redis   │
│ (DB)     │       │ (Cache)  │
└──────────┘       └──────────┘
```

### Port Mapping

| Service   | Internal | External | Purpose                |
|-----------|----------|----------|------------------------|
| Nginx     | 80, 443  | 80, 443  | HTTP/HTTPS traffic     |
| Backend   | 8000     | Private  | FastAPI API server     |
| Frontend  | 3000     | Private  | React app server       |
| PostgreSQL| 5432     | 5432     | Database (optional)    |
| Redis     | 6379     | 6379     | Cache (optional)       |

---

## Security Features

### 1. HTTPS/TLS
- Enforced HTTPS redirect
- TLS 1.2+ only
- Strong cipher suites
- HSTS header (1 year)

### 2. Application Security
- JWT authentication with refresh token rotation
- Rate limiting (100 req/s API, 1000 req/s general)
- CORS whitelisting
- SQL injection protection (parameterized queries)
- CSRF protection
- Input validation & sanitization

### 3. Headers
```
Strict-Transport-Security: max-age=31536000
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

### 4. Infrastructure
- Non-root containers
- Network isolation (Docker bridge)
- Secrets in environment variables (not hardcoded)
- Read-only file system (where possible)

---

## Monitoring & Health

### Health Endpoints

```bash
# Backend health
curl https://api.rpex.com/health

# Prometheus metrics
curl https://api.rpex.com/metrics

# OpenAPI docs (disabled in production)
curl https://api.rpex.com/api/openapi.json
```

### Logs

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx

# Export logs to file
docker-compose logs backend > backend.log
```

### Database Monitoring

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U rpex_prod -d rpex_crm_prod

# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Check connections
SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;
```

---

## Database Management

### Migrations

```bash
# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "migration_name"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Downgrade
docker-compose exec backend alembic downgrade -1

# Show migration status
docker-compose exec backend alembic current
```

### Backup

```bash
# Full backup
docker-compose exec postgres pg_dump -U rpex_prod rpex_crm_prod > backup.sql

# Restore
cat backup.sql | docker-compose exec -T postgres psql -U rpex_prod rpex_crm_prod
```

---

## Maintenance

### Updates

```bash
# Pull latest images
docker-compose pull

# Rebuild custom images
docker-compose build --no-cache

# Graceful restart
docker-compose restart backend frontend

# Rolling restart with health checks
for service in backend frontend; do
  docker-compose restart $service
  sleep 10
done
```

### Scaling

```bash
# Scale backend workers (default: 4)
# Edit docker-compose.yml or set env var:
export BACKEND_WORKERS=8

# Scale frontend replicas
docker-compose up -d --scale frontend=2  # (Note: requires custom setup)
```

### Cleanup

```bash
# Remove unused images/volumes
docker-compose down -v

# Prune all (warning: removes all Docker data)
docker system prune -a --volumes
```

---

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database not ready → wait 30s
# 2. Migration not applied → run alembic upgrade head
# 3. Port already in use → check docker-compose port config
```

### Database connection errors

```bash
# Test connection
docker-compose exec backend python -c "
import asyncpg
import asyncio
async def test():
    conn = await asyncpg.connect('postgres://...@postgres:5432/rpex_crm')
    print(await conn.fetchval('SELECT 1'))
asyncio.run(test())
"
```

### Nginx SSL issues

```bash
# Test certificate validity
openssl x509 -in infra/nginx/letsencrypt/live/domain/fullchain.pem -text -noout

# Test configuration syntax
docker run --rm -v $PWD/infra/nginx:/etc/nginx:ro nginx:alpine nginx -t
```

### Redis connection errors

```bash
# Test Redis connection
docker-compose exec redis redis-cli ping

# Check memory
docker-compose exec redis redis-cli info memory
```

---

## Performance Tuning

### PostgreSQL

```sql
-- Increase shared buffers (in /etc/postgresql/postgresql.conf or docker env)
shared_buffers = '256MB'
effective_cache_size = '1GB'
maintenance_work_mem = '64MB'
work_mem = '16MB'
```

### Redis

```
# Increase max memory policy
maxmemory 1gb
maxmemory-policy allkeys-lru
```

### Nginx

```nginx
# Worker processes = CPU cores
worker_processes auto;
worker_connections 4096;
keepalive_timeout 65;
```

---

## Backup & Disaster Recovery

### Automated Backups

```bash
# Create backup script (cron daily)
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U rpex_prod rpex_crm_prod | \
  gzip > /backups/rpex_crm_$DATE.sql.gz
```

### Point-in-Time Recovery

```bash
# Restore to specific time
docker-compose exec -T postgres pg_restore -c -d rpex_crm_prod < backup.sql
```

---

## Support & Documentation

- **API Documentation**: https://api.rpex.com/api/docs
- **Status Page**: https://api.rpex.com/health
- **Logs Location**: /var/log/nginx (on host)
- **Database**: PostgreSQL 16
- **Python Version**: 3.14

---

## Version Info

- **Release**: 1.0.0
- **Build Date**: 2026-07-26
- **Status**: Production Ready
- **Routes**: 134 REST API endpoints
- **Tables**: 32 PostgreSQL tables
- **Test Coverage**: Basic validation suite included

---

For questions or issues, contact the development team or refer to the system documentation in `/docs`.
