# Bild Prompt for AI Fantasy Draft Assistant

🔧 Build Brief: AI Fantasy Draft Assistant (Python + FastAPI + Next.js)

Objective

Build a production-ready AI-assisted fantasy football draft tool that:
	•	Ranks players by custom scoring using last year’s stats and upcoming projections.
	•	Filters/sorts by position, tiers, ADP, depth charts, injury news, and roster needs.
	•	Tracks an in-person draft (manual picks) or live draft (Sleeper sync).
	•	Provides real-time pick advice with short LLM rationales.
	•	Implements all 4 premium features:
	1.	Monte Carlo season simulations (floor/ceiling, volatility)
	2.	Schedule pockets (startable weeks; early-season usability)
	3.	Exposure control (cap % across multiple leagues)
	4.	Opponent modeling (predict next picks from ADP deltas)

Use FastAPI, PostgreSQL, Redis, and Next.js; containerize with Docker; test with pytest and Playwright; CI via GitHub Actions.

⸻

Repo Layout (create these files)

/fantasy-assistant
  /backend
    app/main.py
    app/api/__init__.py
    app/api/routes_rankings.py
    app/api/routes_draft.py
    app/api/routes_advice.py
    app/core/config.py
    app/core/scoring.py
    app/core/tiers.py
    app/core/vorp.py
    app/core/monte_carlo.py
    app/core/schedule_pockets.py
    app/core/exposure.py
    app/core/opponent_model.py
    app/services/ingest_projections.py
    app/services/ingest_stats_last_year.py
    app/services/ingest_depth.py
    app/services/ingest_injuries.py
    app/services/sleeper_sync.py
    app/services/id_map.py
    app/db/base.py
    app/db/models.py
    app/db/schema_migrations/001_init.sql
    app/workers/scheduler.py
    tests/test_scoring.py
    tests/test_vorp.py
    tests/test_advice.py
    tests/test_monte_carlo.py
    pyproject.toml
    README.md
    .env.example
    Dockerfile
  /frontend
    next.config.js
    package.json
    app/layout.tsx
    app/page.tsx
    app/draft/page.tsx
    app/components/Board.tsx
    app/components/Tiers.tsx
    app/components/Advice.tsx
    app/components/Queue.tsx
    app/components/Filters.tsx
    app/lib/api.ts
    e2e/playwright.config.ts
    e2e/draft.spec.ts
    Dockerfile
  /ops
    docker-compose.yml
    migrate.sh
    seed.sh
  .github/workflows/ci.yml
  LICENSE
  README.md


⸻

Tech & Packages
	•	Backend: FastAPI, pydantic, pandas, numpy, SQLAlchemy, asyncpg, redis, httpx, uvicorn, scikit-learn (for simple models), orjson.
	•	Workers: APScheduler (cron-style jobs).
	•	Monte Carlo: numpy random; percentile summaries.
	•	Frontend: Next.js (App Router), React Server Components, Tailwind, Zustand.
	•	Tests: pytest (unit), Playwright (e2e).
	•	CI: GitHub Actions (lint, type-check, test, container build).

⸻

Environment & Secrets (create .env.example)

POSTGRES_URL=postgresql+asyncpg://postgres:postgres@db:5432/fantasy
REDIS_URL=redis://cache:6379/0
PROJECTIONS_API_KEY=replace_me
INJURIES_API_KEY=replace_me
SLEEPER_LEAGUE_ID=optional_for_live_sync
LLM_API_KEY=replace_me
SCORING_JSON={"pass_yd":0.04,"pass_td":4,"int":-2,"rush_yd":0.1,"rush_td":6,"rec":1,"rec_yd":0.1,"rec_td":6,"fumble":-2}


⸻

Database Schema (create 001_init.sql)
	•	players(id uuid pk, name, team, position, bye_week, age, height, weight, xrefs jsonb, created_at)
	•	projections(id, player_id fk, season int, source text, stats jsonb, updated_at)
	•	historical_stats(id, player_id fk, season int, stats jsonb, updated_at)
	•	depth_charts(id, team, position, player_id fk, rank int, updated_at)
	•	injuries(id, player_id fk, status text, note text, updated_at)
	•	adp(id, player_id fk, platform text, adp numeric, sample_size int, updated_at)
	•	draft_picks(id, league_id text, round int, pick int, player_id fk, team_slot text, ts timestamptz)
	•	user_settings(id, user_id text, scoring jsonb, exposure_limits jsonb, strategy jsonb)
	•	leagues(id, platform text, settings jsonb, scoring jsonb, created_at)
	•	Indices on (position), (team, position, rank), (updated_at), (platform, adp)

⸻

Core Algorithms (backend modules to implement)

1) Scoring & VORP
	•	core/scoring.py: compute fantasy points from projections according to SCORING_JSON.
	•	core/vorp.py: compute baseline by position (QB12/RB24/WR36/TE12 default), set vorp, tier (z-scores with natural gap detection).

2) Advice Engine
	•	Inputs: roster state, ADP, tiers, injuries, depth rank, bye weeks, stacks.
	•	Outputs: top 5 recommendations with reasons + alternatives.
	•	Contextual rules:
	•	Roster construction penalties/bonuses.
	•	ADP drift (prefer value when a player’s market allows waiting).
	•	Stack bonus (QB + WR/TE from same team).
	•	Injury/doubtful demotion, depth rank >3 demotion.

3) Monte Carlo (Nice-to-Have #1)
	•	For each player, simulate season outcomes using variance parameters per stat.
	•	Return median, p10, p90, volatility score, and boom/bust flags.
	•	Surface ceiling/floor columns in /rankings.

4) Schedule Pockets (Nice-to-Have #2)
	•	Using projected weekly usage + defense vs. position (DVP placeholder), compute weeks where player is likely startable.
	•	Return startable_weeks and early_season_value (Weeks 1-4 emphasis).

5) Exposure Control (Nice-to-Have #3)
	•	Track user’s players across multiple drafts (user_id scope).
	•	Enforce soft caps (e.g., cap WR X at 20% exposure).
	•	During advice, flag “overexposed” and promote comparable alternatives.

6) Opponent Modeling (Nice-to-Have #4)
	•	Simple model: for each opponent team, predict next pick by combining roster needs + ADP + positional scarcity.
	•	Show “Likely to be taken before your next pick” badge.

⸻

API Endpoints (implement)

GET /rankings?pos=&limit=&scoring_profile=
Returns merged projections + injuries + depth + ADP + VORP + tiers + MC summaries + schedule pockets.

POST /draft/pick
Body: { league_id, player_id, team_slot?, round, pick }
Marks player taken; updates caches and returns new best-available.

GET /advice?league_id=&round=&pick=&roster_state=
Returns { top5: [...], rationale: "...", fallbacks: [...] } including exposure and opponent modeling signals.

POST /sync/sleeper
Body: { league_id } — fetches league settings, ADP, and live draft picks (if applicable).

GET /healthz
Returns { ok: true }.

⸻

Frontend Pages
	•	/ – overview, load league, configure scoring, see global ranks.
	•	/draft – Live Draft Board:
	•	Columns: Available / Taken / Your Queue / Advice.
	•	Filters: position, tiers, ADP range, injury status, bye weeks, stacks.
	•	On-the-Clock strip: top 5 + one-tap toggles (Need WR / Avoid byes / Chase upside).
	•	Manual “Add Pick” (type-ahead) for in-person drafts.

⸻

Ingestion Jobs (APScheduler)
	•	Nightly: projections, depth charts, ADP (writes to DB).
	•	Every 5 min (in season/draft day): injuries/news.
	•	On demand: Sleeper league sync; one-shot populate last year stats.
	•	Provide seed scripts with synthetic CSVs to run without paid APIs.

⸻

Definition of Done (Acceptance Criteria)
	1.	Rankings endpoint returns 250+ players enriched with: projections points, VORP, tiers, ADP, injury flags, depth rank, MC p10/p50/p90, startable weeks, exposure hints.
	2.	Draft tracking: marking a pick removes the player everywhere and recomputes advice < 300ms (cached).
	3.	Advice explains why (1-2 sentences) and shows 2 alternatives with clear trade-offs.
	4.	Opponent modeling highlights ≥3 players likely gone by your next pick (based on ADP + needs).
	5.	Exposure control: setting a cap updates advice (“overexposed” badge) and suggests swaps.
	6.	Schedule pockets visible as a mini badge (“Startable W1-3”) and sortable column.
	7.	Monte Carlo summaries render in UI (Floor/Ceiling chips) and drive a “Chase upside” toggle.
	8.	E2E test: simulated 12-team draft flow passes; unit tests for scoring, VORP, advice, Monte Carlo pass.
	9.	One-command up via docker-compose up and migrate.sh/seed.sh.
	10.	CI runs lint + tests + builds containers on PR.

⸻

Guided Build Checklist (have Copilot execute sequentially)

Phase 0 — Project Init
	•	Create repo fantasy-assistant and scaffolding per Repo Layout.
	•	Add pyproject.toml and backend dependencies; add frontend package.json with Next.js + Tailwind.
	•	Add .env.example and NEVER commit real secrets.
	•	Configure docker-compose for api, frontend, db (Postgres), cache (Redis).
	•	Add GitHub Actions workflow ci.yml running:
	•	Backend: ruff, pytest
	•	Frontend: pnpm test + Playwright e2e (headless)

Phase 1 — DB & Models
	•	Implement 001_init.sql; write migrate.sh to apply migrations.
	•	Create SQLAlchemy models mirroring tables; init async engine + session in db/base.py.
	•	Implement services/id_map.py to normalize player IDs across sources (sleeper_id, gsis_id, espn_id, pfr_id).

Phase 2 — Scoring + VORP + Tiers
	•	Implement core/scoring.py with a pure function taking stats + scoring JSON.
	•	Implement core/vorp.py with positional baselines and z-score tiers (natural gap heuristic).
	•	Unit tests: test_scoring.py, test_vorp.py with fixtures.

Phase 3 — Ingestion (seed + real)
	•	Add seed.sh and example CSVs to populate: players, historical_stats, projections, depth_charts, injuries, adp.
	•	Implement services/ingest_* modules to load CSVs and (behind flags) call real APIs if keys are present.
	•	Implement workers/scheduler.py with APScheduler jobs and logging.

Phase 4 — Core Endpoints
	•	/rankings: join projections + injuries + depth + ADP → compute points, VORP, tiers.
	•	/draft/pick: accept a pick, write DB, update Redis sets for “available” vs “taken”.
	•	/advice: compute top 5 considering roster needs, ADP drift, stacks, depth, injuries, bye weeks.
	•	Add lightweight LLM rationale function (stub: returns templated rationale when LLM_API_KEY empty).

Phase 5 — The Four Nice-to-Haves
	•	core/monte_carlo.py: simulate N=5,000 seasons per player; return p10/p50/p90 and volatility.
	•	core/schedule_pockets.py: compute startable weeks using weekly usage assumptions + DVP placeholder.
	•	core/exposure.py: track picks across user_id scope; enforce caps; add flags in /advice.
	•	core/opponent_model.py: predict opponent picks (ADP + needs); surface “likely gone” list.

Phase 6 — Frontend
	•	Build / with global ranks, filters (position, tiers, injury, bye, ADP, upside toggle).
	•	Build /draft with Live Board, On-the-Clock strip, Queue, Advice panel.
	•	Add manual “Add Pick” input; wire to /draft/pick; optimistic UI update.
	•	Add chips for Floor/Ceiling, Startable Weeks, Exposure, Likely Gone.

Phase 7 — Tests & CI
	•	Write unit tests for advice, Monte Carlo, schedule pockets, exposure, opponent model.
	•	Write Playwright e2e: simulate picks and assert the UI updates + advice changes.
	•	Ensure CI green; add code coverage badge.

Phase 8 — DX & Ops
	•	Make docker-compose up run API at :8000, Frontend at :3000.
	•	migrate.sh & seed.sh work in containers.
	•	Add README.md with quickstart and screenshots.

⸻

Commands Copilot Should Run (scripts)

Backend (pyproject):

[tool.ruff]
target-version = "py312"

[tool.pytest.ini_options]
pythonpath = ["app"]
addopts = "-q"

package.json (frontend) scripts:

{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "test": "playwright test"
  }
}

docker-compose (ops/docker-compose.yml) targets:
	•	api builds from /backend/Dockerfile, exposes 8000, depends on db, cache.
	•	frontend builds from /frontend/Dockerfile, exposes 3000, depends on api.
	•	db uses postgres:16-alpine with volume.
	•	cache uses redis:7-alpine.

⸻

PR Plan (have Copilot follow this)
	1.	Create branch feat/scaffold.
	2.	Commit repo layout, Docker, CI; open PR “Scaffold: API+UI+Ops”.
	3.	Create branch feat/core-ranking → implement scoring/VORP/tiers + tests → PR.
	4.	Create branch feat/ingestion → seed + jobs → PR.
	5.	Create branch feat/advice → advice endpoint + roster logic → PR.
	6.	Create branch feat/nh1-monte-carlo → PR.
	7.	Create branch feat/nh2-schedule-pockets → PR.
	8.	Create branch feat/nh3-exposure → PR.
	9.	Create branch feat/nh4-opponent-model → PR.
	10.	Create branch feat/frontend → UI + e2e → PR.
	11.	Final branch chore/polish → docs, screenshots, perf, rate limits → PR.

⸻

Review Checklist (tick before merge)
	•	Rankings stable and sort correctly by VORP then FP.
	•	Advice returns in <300ms with Redis hot cache.
	•	MC outputs (p10/p50/p90) visible and used when “Chase Upside” is on.
	•	Startable weeks chips render; sortable column works.
	•	Exposure caps enforce suggestions; badge appears when exceeded.
	•	Opponent model marks at least 3 “likely gone” players correctly on test data.
	•	All tests pass locally and in CI; containers build without warnings.

⸻

Notes for Copilot
	•	Prefer pure functions in core/ with unit tests.
	•	Keep projection sources abstracted behind services/ with a CSV fallback so the app runs without paid keys.
	•	Don’t scrape; use provided seed data structure and stubs for real API calls.
	•	Favor type hints, docstrings, and small modules.

⸻
