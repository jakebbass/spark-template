# Fantasy Assistant Backend

FastAPI backend for the AI Fantasy Draft Assistant.

## Features

- RESTful API for player rankings, draft tracking, and advice
- Real-time draft advice with AI rationale
- VORP (Value Over Replacement Player) calculations
- Monte Carlo season simulations
- Schedule analysis and exposure control
- Opponent modeling for draft strategy

## Quick Start

### Development Setup

1. Install dependencies:
```bash
pip install -e .
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app
```

### Linting

Check code style:
```bash
ruff check .
ruff format .
```

Type checking:
```bash
mypy app/
```

## API Endpoints

### Rankings
- `GET /rankings/` - Get player rankings with VORP, tiers, and projections

### Draft
- `POST /draft/pick` - Record a draft pick
- `POST /sync/sleeper` - Sync with Sleeper league

### Advice
- `GET /advice/` - Get draft advice and recommendations

### Health
- `GET /healthz` - Health check

## Architecture

### Core Modules (`app/core/`)
- `scoring.py` - Fantasy point calculations
- `vorp.py` - VORP and tier calculations  
- `monte_carlo.py` - Season simulations
- `schedule_pockets.py` - Schedule analysis
- `exposure.py` - Multi-league exposure control
- `opponent_model.py` - Draft pick predictions

### Services (`app/services/`)
- `ingest_*.py` - Data ingestion from APIs/CSV
- `sleeper_sync.py` - Sleeper platform integration
- `id_map.py` - Player ID mapping across platforms

### Database (`app/db/`)
- `models.py` - SQLAlchemy models
- `base.py` - Database connection and session management
- `schema_migrations/` - SQL migration files

## Configuration

Environment variables (see `.env.example`):

- `POSTGRES_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string  
- `PROJECTIONS_API_KEY` - Projections API key (optional)
- `INJURIES_API_KEY` - Injuries API key (optional)
- `LLM_API_KEY` - LLM API key for advice rationale (optional)
- `SCORING_JSON` - Default scoring configuration

## Data Sources

The application supports multiple data sources with CSV fallbacks:

1. **Projections** - Player projections for upcoming season
2. **Historical Stats** - Previous season performance data
3. **Depth Charts** - Team depth chart information
4. **Injuries** - Current injury status and news
5. **ADP** - Average draft position across platforms

When API keys are not provided, the system falls back to CSV files in the `data/` directory.

## Background Jobs

The scheduler (`app/workers/scheduler.py`) runs automated jobs:

- **Nightly** - Update projections and ADP data
- **Every 5 minutes** - Update injury reports (during season)
- **Weekly** - Update depth charts and historical stats

## Testing Strategy

- **Unit tests** for all core calculation functions
- **Integration tests** for API endpoints  
- **Mock external APIs** to avoid rate limits in tests
- **Test fixtures** for consistent test data