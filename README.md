# RPEX SEO Inquiry CRM and Analytics Platform

Enterprise-grade CRM and analytics platform for collecting and managing SEO inquiries from multiple websites.

## Stack
- Backend: FastAPI, SQLAlchemy Async, PostgreSQL, Redis, Celery, WebSocket, JWT, Pydantic v2
- Frontend: React, TypeScript, Redux Toolkit, React Query, Tailwind CSS, Recharts
- Infrastructure: Docker, Docker Compose, Nginx

## Quick Start
1. Copy `.env.example` to `.env` and update secrets.
2. Run `docker compose up --build`.
3. API docs: `http://localhost/api/docs`
4. Frontend: `http://localhost`
5. Direct backend (bypassing Nginx): `http://localhost:8001/docs`

## Architecture
- Clean architecture with service and repository layers.
- Async database operations and Redis-backed real-time notifications.
- Celery for scheduled report generation.

## Automation Engine (Implemented)
- Auto lead assignment
- Duplicate lead detection
- Missed follow-up alerts
- WhatsApp reminders (queue events)
- Email automation (queue events)
- Booking confirmation notifications (queue events)
- Invoice auto-generation from bookings
- Payment reminders
- Anniversary and birthday wishes (queue events)
- Daily performance reports
- Manager approval workflow support
- Commission calculation
- AI lead scoring refresh (heuristic v1)

### On-demand automation API
- List workflows: GET /api/v1/automation/workflows
- Run workflow: POST /api/v1/automation/run/{workflow_name}

## Authorization
- Permission-driven RBAC backed by `permissions` + `role_permissions`.
- Route guards validate permissions from DB mappings (not hardcoded role checks).
- Public registration endpoint: `POST /api/v1/auth/register`.

## Lead Search and Saved Views
- Advanced lead search endpoint: `GET /api/v1/leads`.
- Supports full-text query (`q`), status/source/medium/campaign/assignee filters, date range, JSONB dynamic field filters (`extra_filters`), and pageable sorting.
- Saved views endpoints:
	- `POST /api/v1/leads/views`
	- `GET /api/v1/leads/views`
	- `DELETE /api/v1/leads/views/{view_id}`

## Phases
- Phase 1 is implemented as foundation + auth/RBAC.
- Core modules are scaffolded and wired for progressive hardening.

## Production Expansion Blueprint
- Detailed module-wise production roadmap: `docs/production-crm-blueprint.md`

## CI/CD to Hostinger VPS (Direct SSH Deploy)

This repository includes:
- Workflow: `.github/workflows/ci-cd-hostinger-vps.yml`
- Server deploy script: `scripts/deploy_vps.sh`

### 1) One-time VPS bootstrap
Run these commands on your VPS:

```bash
mkdir -p /opt/rpex-crm
cd /opt/rpex-crm
git clone <YOUR_GITHUB_REPO_URL> .
cp .env.example .env
# Edit .env with production values
docker compose up -d --build
```

### 2) Add GitHub Actions secrets
In your GitHub repository settings, add:
- `VPS_HOST` (example: `200.97.170.226`)
- `VPS_USER` (example: `root`)
- `VPS_PASSWORD` (VPS SSH password)
- `VPS_APP_DIR` (example: `/opt/rpex-crm`)

If your SSH server does not run on port `22`, update the workflow file accordingly.

### 3) Deployment flow
- Push to `main` or `master`.
- GitHub Actions runs backend + frontend CI checks.
- On success, it SSHes into VPS and runs:
	- `git pull --ff-only origin <branch>`
	- `docker compose up -d --build --remove-orphans`

### 4) Recommended hardening
- Prefer SSH key auth over password auth for production.
- Restrict VPS firewall to allow SSH only from trusted IPs.
- Use strong values for all secrets in `.env`.

## HTTPS Setup (Let's Encrypt + Certbot)

This repository includes a Certbot workflow for `srv1829331.hstgr.cloud`.

### Prerequisites
- DNS A record for `srv1829331.hstgr.cloud` must point to your VPS public IP.
- Ports `80` and `443` must be open in the VPS firewall/security group.

### Step 1: Start services in HTTP mode
```bash
docker compose up -d --build
```

### Step 2: Issue certificate and enable HTTPS
```bash
chmod +x scripts/enable_https_letsencrypt.sh
DOMAIN=srv1829331.hstgr.cloud EMAIL=you@example.com ./scripts/enable_https_letsencrypt.sh
```

### Step 3: Keep cert renewal running
```bash
docker compose up -d certbot
```

The script switches Nginx to `infra/nginx/nginx.ssl.conf` after certificate issuance.
