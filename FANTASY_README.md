# AI Fantasy Draft Assistant

A production-ready, full-stack fantasy football draft tool featuring real-time AI advice, player rankings, and advanced analytics.

## 🚀 Quick Start

### One-Command Setup

```bash
# Clone and start all services
docker-compose -f ops/docker-compose.yml up -d

# Apply database migrations
./ops/migrate.sh

# Seed with sample data
./ops/seed.sh
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## ✨ Features

### Core Functionality
- **Real-time Draft Tracking** - Manual pick entry or live sync with Sleeper
- **AI-Powered Advice** - Context-aware recommendations with explanations
- **VORP Rankings** - Value Over Replacement Player calculations with tiers
- **Advanced Filtering** - Position, injury status, bye weeks, ADP ranges

### Premium Analytics
- **Monte Carlo Simulations** - Season outcome projections (floor/ceiling)
- **Schedule Analysis** - Identify startable weeks and early-season value
- **Exposure Control** - Manage player percentages across multiple leagues
- **Opponent Modeling** - Predict next picks based on roster needs and ADP

## 🏗️ Architecture

### Monorepo Structure
```
├── backend/          # FastAPI Python API
├── frontend/         # Next.js React Application  
├── ops/              # Docker Compose & Scripts
└── .github/          # CI/CD Workflows
```

### Tech Stack
- **Backend**: FastAPI, PostgreSQL, Redis, SQLAlchemy
- **Frontend**: Next.js 15, React 19, Tailwind CSS, Zustand
- **Infrastructure**: Docker, GitHub Actions
- **Testing**: pytest, Playwright

## 🔧 Development

### Backend Development
```bash
cd backend/
pip install -e .[dev]
uvicorn app.main:app --reload  # http://localhost:8000
```

### Frontend Development
```bash
cd frontend/
npm install
npm run dev                    # http://localhost:3000
```

### Testing
```bash
# Backend tests
cd backend/ && pytest

# Frontend tests  
cd frontend/ && npm run test

# All tests via CI
gh workflow run ci.yml
```

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/rankings/` | Player rankings with VORP, tiers, projections |
| `POST` | `/draft/pick` | Record a draft pick |
| `GET` | `/advice/` | Get AI draft recommendations |
| `POST` | `/sync/sleeper` | Sync with Sleeper league |
| `GET` | `/healthz` | Health check |

## 🎯 Core Algorithms

### VORP (Value Over Replacement Player)
Calculates player value above positional baselines:
- **QB**: 12th ranked player baseline
- **RB**: 24th ranked player baseline  
- **WR**: 36th ranked player baseline
- **TE**: 12th ranked player baseline

### Tier Detection
Uses natural gap detection in VORP scores to group players into tiers automatically.

### Draft Advice Engine
Contextual recommendations considering:
- Roster construction needs
- ADP value opportunities  
- Injury risk assessment
- Bye week conflicts
- Team stacking bonuses

## ⚙️ Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:

```bash
# Database
POSTGRES_URL=postgresql+asyncpg://postgres:postgres@db:5432/fantasy
REDIS_URL=redis://cache:6379/0

# Optional API Keys (CSV fallback if not provided)
PROJECTIONS_API_KEY=your_key_here
INJURIES_API_KEY=your_key_here
LLM_API_KEY=your_key_here

# Scoring (PPR example)
SCORING_JSON={"pass_yd":0.04,"pass_td":4,"int":-2,"rush_yd":0.1,"rush_td":6,"rec":1,"rec_yd":0.1,"rec_td":6,"fumble":-2}
```

### Data Sources
The system supports multiple data sources with CSV fallbacks:
- **Projections** - Fantasy point projections
- **Historical Stats** - Previous season performance  
- **Depth Charts** - Team depth information
- **Injuries** - Current player health status
- **ADP** - Average draft position across platforms

## 🔄 Background Jobs

Automated data updates via APScheduler:
- **Nightly**: Projection and ADP updates
- **Every 5 minutes**: Injury status (during season)
- **Weekly**: Depth chart updates

## 🐳 Docker Deployment

### Production Deployment
```bash
# Build and deploy
docker-compose -f ops/docker-compose.yml up -d --build

# Scale services
docker-compose -f ops/docker-compose.yml up -d --scale api=3

# View logs
docker-compose -f ops/docker-compose.yml logs -f
```

### Health Monitoring
All services include health checks:
- Database connectivity
- Redis availability  
- API endpoint responses
- Frontend build status

## 🧪 Testing Strategy

### Unit Tests
- **Backend**: Core algorithm functions (`scoring`, `vorp`, `advice`)
- **Coverage**: All `app/core/` modules with pytest

### Integration Tests
- **API Endpoints**: Request/response validation
- **Database**: Model operations and queries

### End-to-End Tests
- **Draft Flow**: Complete user journey via Playwright
- **Cross-browser**: Chrome, Firefox, Safari

## 📈 Performance

### Caching Strategy
- **Redis**: Player rankings, advice calculations
- **Database**: Optimized indexes on frequent queries
- **Frontend**: Static generation for rankings pages

### Benchmarks
- **Advice Generation**: < 300ms with hot cache
- **Rankings API**: < 500ms for 250+ players
- **Draft Pick Processing**: < 100ms

## 🔒 Security

- **No Secrets in Repo**: All sensitive data via environment variables
- **Database**: Parameterized queries prevent injection
- **API**: CORS configured for allowed origins only
- **Containers**: Non-root users, minimal base images

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`feat/new-feature`)
3. **Test** your changes (`npm run test` and `pytest`)
4. **Submit** a pull request

### PR Checklist
- [ ] All tests pass locally and in CI
- [ ] Code follows project style (ruff, eslint)
- [ ] Documentation updated if needed
- [ ] No breaking changes without migration plan

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Built with ❤️ for fantasy football enthusiasts**