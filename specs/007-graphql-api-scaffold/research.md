# Research: GraphQL API Scaffold (Strawberry)

**Feature**: GraphQL API Scaffold (Strawberry)
**Branch**: 007-graphql-api-scaffold
**Date**: 2025-11-01

## Goals

- Validate technology choices (Strawberry + FastAPI) and alternative tradeoffs
- Define best practices for DataLoader batching and caching
- Define security posture: per-field auth, query depth (15), complexity (5000)
- Define pagination approach (cursor + offset) and defaults (20/100)
- Define subscription infrastructure (WebSocket + event bus)
- Produce actionable patterns to implement in template files

## 1. Strawberry vs Alternatives

Summary:

- Strawberry: modern, type-first GraphQL for Python, excellent FastAPI integration, good typing and developer ergonomics.
- Ariadne: schema-first approach, flexible but less type-safe.
- Graphene: older, community still active but less type-safety and slower evolution.

Recommendation: Strawberry (type-first, great dev DX, integrates with FastAPI ASGI, aligns with Riso Python baseline).

Risks:

- New dependency in template; mitigate by making module opt-in and documenting upgrade path.

## 2. DataLoader Patterns

- Use DataLoader pattern (batch function per resource) to prevent N+1 queries.
- Strategy: per-request DataLoader instances created in GraphQL context (request-scoped); keys normalized (primary keys), batching window single tick (event loop microtask), optional caching for request duration.
- Implementation notes: Provide an async DataLoader helper (wraps promise/await) compatible with Strawberry resolvers.
- Tests: measure DB query counts for list + nested queries; assert batching reduces queries.

## 3. Authentication & Authorization

- Per-field auth via resolver decorators or custom Strawberry directive (@auth).
- Authentication performed in FastAPI dependencies; user identity injected into GraphQL context.
- Mutation fields must require auth by default; queries may be public unless annotated.
- Support roles/permissions via simple permission functions that can be composed.

## 4. Query Validation (Depth & Complexity)

- Depth limiting: traverse incoming selection AST and compute depth; reject queries >15.
- Complexity: compute score by counting fields, multiply by child counts and list multipliers; reject >5000.
- Provide hooks/config for projects to tune thresholds.

## 5. Pagination

- Implement Relay-style cursor connections as primary approach; also provide offset-based helpers for simple cases.
- Cursor encoding: base64 encoded stable cursor (e.g., `<type>:<pk>:<sort-value>`).
- Default page size: 20, configurable max: 100.

## 6. Subscriptions

- Use WebSocket (ASGI) with Strawberry's subscription support or alternative (graphql-ws protocol).
- For broadcasting, optionally integrate with an event broker (Redis pub/sub) for multi-instance support.
- Connection management: authenticate on connect, store subscription state in memory (single instance) or via broker (multi-instance).

## 7. Testing & CI

- Unit tests: resolver logic, DataLoader batching, auth decorators, pagination utilities.
- Integration tests: Spin up FastAPI app, run sample queries against test DB (sqlite/postgres), run subscription integration tests using test client.
- CI: add a job to run schema validation (ensures generated schema.graphql matches runtime schema) and run GraphQL contract tests.

## 8. Performance

- Benchmarks: measure basic query latency (simple object), nested queries with and without DataLoader, subscription end-to-end latency.
- Target: <100ms for simple queries in dev profile; real-world infra required for scale.

## 9. Security

- Sanitize error messages for production (no stack traces returned).  
- Rate limiting and complexity/depth checks to prevent abuse.  
- Ensure subscriptions enforce same auth rules as queries/mutations.

## 10. Data Source Integration Patterns

### REST API Adapter Pattern

Integrate external REST APIs as GraphQL data sources:

```python
import httpx

async def resolve_external_user(user_id: str, info: Info) -> User:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
        response.raise_for_status()
        data = response.json()
        return User(id=data["id"], name=data["name"], email=data["email"])
```

Key considerations:

- Use async HTTP clients (httpx, aiohttp) for non-blocking calls
- Implement timeout and retry logic for resilience
- Cache responses when appropriate (DataLoaders can wrap HTTP calls)
- Handle HTTP errors gracefully (404 → None, 500 → GraphQL error)

### Multi-Source Resolver Pattern

Combine data from multiple sources in a single resolver:

```python
async def resolve_user_with_posts(user_id: str, info: Info) -> User:
    # Fetch user from database
    db_user = await info.context.db.get_user(user_id)
    
    # Fetch posts from external API
    async with httpx.AsyncClient() as client:
        posts_response = await client.get(f"https://blog-api.example.com/posts?author={user_id}")
        posts_data = posts_response.json()
    
    # Combine into single GraphQL response
    return User(
        id=db_user.id,
        name=db_user.name,
        email=db_user.email,
        posts=[Post(**post) for post in posts_data]
    )
```

### Error Handling for External Services

```python
from typing import Optional

async def resolve_with_fallback(user_id: str, info: Info) -> Optional[User]:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"https://api.example.com/users/{user_id}")
            response.raise_for_status()
            return User(**response.json())
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None  # User not found
        raise  # Re-raise for 500, etc.
    except httpx.TimeoutException:
        # Log timeout, return fallback
        info.context.logger.warning(f"Timeout fetching user {user_id}")
        return None
```

### DataLoader for External APIs

Batch external API calls using DataLoaders:

```python
from strawberry.dataloader import DataLoader

async def batch_load_users_from_api(user_ids: list[str]) -> list[User]:
    async with httpx.AsyncClient() as client:
        # Single batched request instead of N individual requests
        response = await client.post(
            "https://api.example.com/users/batch",
            json={"ids": user_ids}
        )
        users_data = response.json()
        # Return in same order as user_ids
        user_map = {u["id"]: User(**u) for u in users_data}
        return [user_map.get(uid) for uid in user_ids]

# In context setup:
user_api_loader = DataLoader(load_fn=batch_load_users_from_api)
```

## Deliverables from Research

- Technology selection rationale (this document)  
- Sample DataLoader implementation and patterns  
- Complexity/depth validation approach and pseudocode  
- Subscription architecture options (single instance vs brokered)
- Testing checklist and CI additions
- Data source integration patterns (database, REST API, multi-source)


