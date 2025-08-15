# Copilot Instructions for AI Coding Agents

## Project Overview
This repository implements an **AI Fantasy Draft Assistant**: a production-ready, full-stack tool for fantasy football drafts, featuring real-time AI advice, player rankings, and advanced analytics. The project is organized as a monorepo with Python (FastAPI backend), Next.js (frontend), PostgreSQL, Redis, and containerized with Docker. All build, test, and deployment workflows are automated via scripts and GitHub Actions.

## Architecture & Layout
- **Monorepo structure:**
  - `/backend`: FastAPI app, core algorithms, ingestion jobs, DB models, and tests.
  - `/frontend`: Next.js (App Router), React Server Components, Tailwind, Zustand, Playwright e2e tests.
  - `/ops`: Docker Compose, migration/seed scripts.
  - `.github/workflows/ci.yml`: CI for lint, typecheck, test, and container build.
- **Backend modules:** Core logic in `app/core/` (scoring, VORP, tiers, Monte Carlo, schedule pockets, exposure, opponent modeling). Ingestion in `app/services/`. DB models in `app/db/`.
- **Frontend:** Pages in `app/`, components in `app/components/`, API logic in `app/lib/api.ts`.
- **Testing:** Unit tests (pytest) in `/backend/tests/`, e2e (Playwright) in `/frontend/e2e/`.

## Key Conventions & Patterns
- **Pure functions** in `core/` with unit tests; keep projection sources abstracted behind `services/` with CSV fallback.
- **Type hints, docstrings, and small modules** are required for Python code.
- **Frontend state** via Zustand; UI primitives follow Tailwind/Headless UI patterns.
- **No real secrets** in repo; use `.env.example` for environment variables.
- **Branch/PR workflow:**
  1. Scaffold (feat/scaffold)
  2. Core ranking (feat/core-ranking)
  3. Ingestion (feat/ingestion)
  4. Advice (feat/advice)
  5-9. Nice-to-haves (feat/nh*-*)
  10. Frontend (feat/frontend)
  11. Polish/docs (chore/polish)

## Developer Workflows
- **Backend:**
  - Install: `pip install -e .`
  - Run: `uvicorn app.main:app --reload`
  - Test: `pytest`
  - Lint: `ruff .`
- **Frontend:**
  - Install: `pnpm install`
  - Dev: `pnpm dev`
  - Build: `pnpm build`
  - Test: `pnpm test` (Playwright)
- **Ops:**
  - One-command up: `docker-compose up`
  - DB migration: `./ops/migrate.sh`
  - Seed data: `./ops/seed.sh`

## Acceptance Criteria & CI
- All endpoints and features as described in the build prompt must be implemented and tested.
- CI runs lint, typecheck, unit/e2e tests, and container builds on PRs.
- See `/backend/tests/` and `/frontend/e2e/` for test coverage requirements.

## Examples & References
- See `/backend/app/core/scoring.py` for scoring logic.
- See `/frontend/app/components/Advice.tsx` for advice UI pattern.
- See `/ops/docker-compose.yml` for service orchestration.

## Build Plan & Phases
Follow the "Guided Build Checklist" and PR plan in `.github/bild-prompt.md` for sequential implementation. Each phase should be completed and tested before moving to the next.

---

**When extending this project:**
- Adhere strictly to the repo layout, naming, and modularization described above.
- Document new patterns or conventions in this file if they become project-wide.
- Keep all code and infra changes in line with the acceptance criteria and review checklist in the build prompt.
