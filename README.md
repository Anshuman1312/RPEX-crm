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
