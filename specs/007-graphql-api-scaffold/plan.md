# Implementation Plan: GraphQL API Scaffold (Strawberry)

**Branch**: `007-graphql-api-scaffold` | **Date**: 2025-11-01 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/007-graphql-api-scaffold/spec.md`

## Summary

Create a production-ready GraphQL API scaffold using Strawberry framework that provides flexible data querying with field selection, interactive playground for API exploration, DataLoader optimization for N+1 query prevention, mutations for data modification, real-time subscriptions via WebSocket, comprehensive error handling, and security controls (query depth limiting to 15 levels, complexity analysis up to 5000 points, optional per-field authentication). The scaffold includes both cursor-based (Relay) and offset-based pagination with sensible defaults (20 items/page, max 100).

## Technical Context

**Language/Version**: Python 3.11+ (consistent with Riso template baseline, managed via uv)  
**Primary Dependencies**: Strawberry GraphQL ≥0.200.0, FastAPI ≥0.104.0 (ASGI integration), uvicorn (ASGI server), pydantic ≥2.0.0 (data validation)  
**Storage**: Pluggable resolver pattern - supports any data source (PostgreSQL via async SQLAlchemy recommended, but also REST APIs, in-memory, etc.)  
**Testing**: pytest ≥7.4.0, pytest-asyncio (async test support), GraphQL query testing via Strawberry test client  
**Target Platform**: Linux server (containerized via Docker from feature 005), ASGI-compatible deployment  
**Project Type**: Single project with optional API module track (integrates with existing Riso Python project structure)  
**Performance Goals**: <100ms response time for simple queries, <200ms for complex queries with joins, handle 100+ concurrent requests  
**Constraints**: Query depth ≤15 levels, complexity ≤5000 points, pagination max 100 items, per-field auth overhead minimal  
**Scale/Scope**: Template module generating ~15-20 core files, supports 10-50 GraphQL types in typical project, scales to 1000+ req/s with proper infrastructure

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Riso Template Principles

**✅ Module Sovereignty**: GraphQL API scaffold is an optional Copier module (`graphql_api_module=enabled`), does not affect baseline template

**✅ Deterministic Generation**: All GraphQL scaffolding files generated via Jinja2 templates with predictable structure, reproducible across renders

**✅ Minimal Baseline**: GraphQL API is opt-in, not included in minimal template variant, does not bloat default projects

**✅ Quality Integration**: Integrates with existing quality suite (ruff, mypy, pylint, pytest from feature 003), extends with GraphQL-specific tests

**✅ Container Support**: Leverages existing Docker/docker-compose infrastructure (feature 005), adds GraphQL service definition

**✅ CI/CD Integration**: Extends existing GitHub Actions workflows (feature 004) with GraphQL schema validation, query testing

**✅ Documentation Standards**: Generates Markdown documentation compatible with Fumadocs/Sphinx/Docusaurus (feature 002)

**✅ Technology Consistency**: Python 3.11+ via uv matches template baseline, Strawberry chosen for FastAPI integration and type safety

### Potential Complexity Concerns

| Concern | Mitigation | Status |
|---------|-----------|--------|
| Additional dependency (Strawberry) | Well-maintained (10k+ GitHub stars), official FastAPI recommendation, stable API | ✅ Justified |
| GraphQL learning curve | Comprehensive quickstart.md, example queries, playground for experimentation | ✅ Addressed |
| Schema complexity | Modular schema composition, clear type definitions, auto-generated documentation | ✅ Addressed |
| Performance overhead (DataLoaders) | Opt-in per resolver, clear patterns, benchmarking in quickstart | ✅ Addressed |

**Gate Status**: ✅ PASS - No constitution violations. Feature aligns with modular, opt-in architecture.

## Project Structure

### Documentation (this feature)

```text
specs/007-graphql-api-scaffold/
├── plan.md              # This file
├── research.md          # Phase 0: Technology decisions, patterns, best practices
├── data-model.md        # Phase 1: GraphQL schema design, type system
├── quickstart.md        # Phase 1: Developer onboarding guide
├── contracts/           # Phase 1: GraphQL schema definitions
│   └── schema.graphql   # Complete API schema
└── tasks.md             # Phase 2: Implementation task breakdown (NOT created yet)
```

### Source Code (Riso template integration)

```text
template/files/
├── python/
│   └── graphql_api/                    # New module (conditional on graphql_api_module=enabled)
│       ├── __init__.py.jinja
│       ├── schema.py.jinja             # Root schema definition
│       ├── types/                      # GraphQL object types
│       │   ├── __init__.py.jinja
│       │   ├── user.py.jinja           # Example: User type
│       │   └── post.py.jinja           # Example: Post type
│       ├── queries/                    # Query resolvers
│       │   ├── __init__.py.jinja
│       │   └── user_queries.py.jinja
│       ├── mutations/                  # Mutation resolvers
│       │   ├── __init__.py.jinja
│       │   └── user_mutations.py.jinja
│       ├── subscriptions/              # Subscription resolvers
│       │   ├── __init__.py.jinja
│       │   └── user_subscriptions.py.jinja
│       ├── dataloaders.py.jinja        # DataLoader implementations
│       ├── context.py.jinja            # GraphQL context (auth, DB, etc.)
│       ├── auth.py.jinja               # Per-field authentication
│       ├── pagination.py.jinja         # Cursor + offset pagination
│       ├── complexity.py.jinja         # Query complexity analysis
│       └── main.py.jinja               # FastAPI integration + playground
│
├── shared/
│   └── graphql/                        # Shared across Python projects
│       ├── config.toml.jinja           # GraphQL configuration
│       └── __init__.py.jinja
│
└── tests/
    └── graphql/                        # GraphQL test templates
        ├── test_queries.py.jinja
        ├── test_mutations.py.jinja
        ├── test_subscriptions.py.jinja
        ├── test_dataloaders.py.jinja
        ├── test_auth.py.jinja
        └── test_complexity.py.jinja

docs/modules/
└── graphql.md.jinja                    # Module documentation

scripts/ci/
└── validate_graphql_schemas.py         # CI schema validation
```

**Structure Decision**: Single project with optional module. GraphQL API integrates into existing Python project structure via `{{package_name}}.graphql_api` namespace. Module is conditionally generated when `graphql_api_module=enabled` in Copier answers. Follows Riso pattern of feature isolation with shared utilities.

## Complexity Tracking

> **No violations requiring justification** - All checks passed

---

## Phase 0: Research & Technology Decisions

**Status**: Starting research phase

### Research Tasks

1. **Strawberry vs. Alternatives**:
   - Compare Strawberry, Ariadne, Graphene
   - Evaluate FastAPI integration quality
   - Assess type safety and IDE support
   - Decision: Strawberry (official FastAPI recommendation, excellent type hints)

2. **DataLoader Patterns**:
   - Research batching strategies
   - Evaluate caching approaches
   - Study N+1 prevention techniques
   - Best practices from Facebook DataLoader

3. **Authentication Integration**:
   - Per-field auth decorators
   - Context-based auth checks
   - Integration with FastAPI dependency injection
   - JWT token validation patterns

4. **Query Complexity Analysis**:
   - Complexity calculation algorithms
   - Depth vs. breadth tradeoffs
   - GitHub GraphQL API approach
   - Shopify GraphQL rate limiting

5. **Pagination Standards**:
   - Relay Cursor Connections specification
   - Offset pagination patterns
   - Hybrid approach implementation
   - Edge cases and consistency

6. **Subscription Infrastructure**:
   - WebSocket server configuration
   - Event broadcasting patterns
   - Connection management
   - Cleanup and resource handling

7. **Testing Strategies**:
   - GraphQL query testing with Strawberry
   - Snapshot testing for schema changes
   - Integration testing with test client
   - Performance testing for DataLoaders

8. **Schema Design Patterns**:
   - Modular schema composition
   - Type reusability
   - Input vs. output types
   - Error handling conventions

- ### Output: research.md

Will contain:

- Technology selections with rationale
- Best practices for each component
- Code examples and patterns
- Performance benchmarks
- Security considerations

---

## Phase 1: Design & Contracts

**Prerequisites**: research.md complete

### 1.1 Data Model Design (data-model.md)

Extract from spec and design:

- **Core GraphQL Types**:

- Query (root query type)
- Mutation (root mutation type)
- Subscription (root subscription type)
- User (example domain type)
- Post (example domain type)
- PageInfo (pagination metadata)
- Connection (Relay connection pattern)
- Edge (Relay edge pattern)

- **Authentication Context**:

- User identity
- Permissions
- Request metadata

- **DataLoader Types**:

- Batch function signatures
- Cache keys
- Load strategies

- **Pagination Types**:

- Cursor structure
- Connection metadata
- Edge wrapping

### 1.2 API Contracts (contracts/schema.graphql)

Generate complete GraphQL schema:

- All query fields with documentation
- All mutation fields with input/output types
- All subscription fields
- Custom scalar types
- Interfaces and unions
- Directives for auth and complexity

Example structure:

```graphql
type Query {
  user(id: ID!): User
  users(first: Int, after: String, offset: Int, limit: Int): UserConnection!
}

type Mutation {
  createUser(input: CreateUserInput!): User! @auth
  updateUser(id: ID!, input: UpdateUserInput!): User! @auth
  deleteUser(id: ID!): Boolean! @auth
}

type Subscription {
  userCreated: User!
}

type User {
  id: ID!
  name: String!
  email: String!
  avatar: String
  posts(first: Int, after: String): PostConnection!
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  cursor: String!
  node: User!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

input CreateUserInput {
  name: String!
  email: String!
  avatar: String
}

input UpdateUserInput {
  name: String
  email: String
  avatar: String
}
```

### 1.3 Quickstart Guide (quickstart.md)

- Developer onboarding document:

- Installation instructions
- First query example
- Playground usage
- DataLoader patterns
- Authentication setup
- Testing examples
- Performance tips
- Common pitfalls

### 1.4 Agent Context Update

- Run `.specify/scripts/bash/update-agent-context.sh copilot` to add:

- Strawberry GraphQL
- GraphQL schema patterns
- DataLoader usage
- Pagination patterns

---

## Phase 2: Task Breakdown

**Not executed in `/speckit.plan` - requires separate `/speckit.tasks` command**

- Will decompose into:

- Template file creation
- Schema generation logic
- DataLoader implementation
- Authentication decorators
- Pagination utilities
- Testing infrastructure
- Documentation generation
- CI integration
- Sample project generation

---

## Next Steps

1. ✅ Complete this plan
2. → Generate research.md (Phase 0)
3. → Generate data-model.md (Phase 1)
4. → Generate contracts/schema.graphql (Phase 1)
5. → Generate quickstart.md (Phase 1)
6. → Update agent context
7. → Run `/speckit.tasks` for implementation breakdown

**Current Status**: Plan complete, ready for Phase 0 research
