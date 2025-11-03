# Enhanced Developer Tools

This directory contains tools to improve local development experience.

## Components

### 1. Unified Dev Dashboard - `dashboard/`

Web-based dashboard showing real-time service status.

**Features**:
- Service health monitoring (database, cache, auth, jobs, etc.)
- Unified log viewer with correlation IDs
- Quick actions (restart service, clear cache, run migrations)
- Performance metrics visualization

**Access**: `pnpm dev:dashboard` → http://localhost:3001

**Files**:
- `src/App.tsx.jinja` - Dashboard UI
- `src/components/ServiceStatus.tsx.jinja` - Service health component
- `src/components/LogViewer.tsx.jinja` - Log aggregation viewer
- `package.json.jinja` - Dependencies

### 2. Offline Development Mode - `offline-mode/`

Service mocking for development without internet connection.

**Mocked Services**:
- Authentication (JWT signing with local key)
- Billing (simulated subscription states)
- AI (canned responses or local Ollama)
- Email (log to console, save to file)
- Storage (local filesystem)
- Search (in-memory index)
- Cache (in-memory cache)

**Enable**: `pnpm dev --offline` or `OFFLINE_MODE=true pnpm dev`

**Files**:
- `mocks/auth-mock.ts.jinja` - Authentication mock
- `mocks/billing-mock.ts.jinja` - Billing mock
- `mocks/ai-mock.ts.jinja` - AI response mock
- `mocks/index.ts.jinja` - Mock registry
- `enable-offline.ts.jinja` - Offline mode toggle

### 3. Fixture Management - `fixtures/`

Realistic test data generation and management.

**Features**:
- Factory-based fixture generation (Faker.js)
- Quick database reset
- 1000+ records generation in <15 seconds
- Seeded data for development and testing

**Commands**:
- `pnpm dev:fixtures` - Seed fixtures
- `pnpm dev:fixtures --reset` - Clear and reseed
- `pnpm dev:fixtures --count=100` - Custom count

**Files**:
- `factories/user-factory.ts.jinja` - User fixture factory
- `factories/org-factory.ts.jinja` - Organization factory
- `factories/subscription-factory.ts.jinja` - Subscription factory
- `seed.ts.jinja` - Seeding script
- `reset.ts.jinja` - Reset script

## One-Command Setup

All dev tools integrate with one-command setup:

```bash
pnpm dev:setup
```

**Sequence**:
1. Validate prerequisites (Node.js, Docker, database)
2. Start local services (docker-compose up)
3. Wait for service health checks
4. Run database migrations
5. Seed fixtures
6. Validate environment variables
7. Launch development server

**Target**: <5 minutes complete setup

## docker-compose Configuration

Included `docker-compose.yml.jinja` for local service orchestration:

```yaml
services:
  postgres:    # Local Postgres
  redis:       # Local Redis (if cache enabled)
  meilisearch: # Local search (if meilisearch selected)
  mailhog:     # Email testing
```

## Usage

```bash
# Launch dev dashboard
pnpm dev:dashboard

# One-command setup
pnpm dev:setup

# Start in offline mode
pnpm dev --offline

# Reset fixtures
pnpm dev:fixtures --reset
```

## Status

- **Phase 8**: Enhanced dev tools (Planned)

Last Updated: 2025-11-02
