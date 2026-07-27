# RPEX Enterprise CRM Frontend

Enterprise-grade React 19 + TypeScript frontend with feature-based architecture.

## Quick Start

1. Copy environment file:
   cp .env.example .env
2. Install dependencies:
   npm install
3. Run dev server:
   npm run dev

## Scripts

- npm run dev
- npm run build
- npm run preview
- npm run test
- npm run lint
- npm run format

## Architecture

- app: providers and store
- core: api/auth/error infrastructure
- routes: router and guards
- layouts: enterprise shell
- components: reusable UI primitives
- features: business modules
- config: env, permissions
- tests: testing setup and baseline tests
