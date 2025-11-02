# Quickstart: GraphQL API Scaffold

This quickstart shows how to instantiate the scaffold and run a local development server.

## Prerequisites

- Python 3.11+
- Optional: Docker for containerized runs

## Install

1. Add the `graphql_api_module=enabled` option when rendering the Riso template (copier answers).
2. Install dependencies (example):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-graphql.txt
```

## Run dev server (example)

```bash
export DATABASE_URL=sqlite+aiosqlite:///./dev.db
uvicorn package_name.graphql_api.main:app --reload
```

## First query (using GraphQL playground)

Open `http://localhost:8000/graphql` and run:

```graphql
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
    posts(first: 5) {
      edges { node { id title } }
      pageInfo { hasNextPage }
    }
  }
}
```

## Testing

- Run pytest for GraphQL unit and integration tests:

```bash
pytest tests/graphql
```

## Notes

- See `data-model.md` for schema shapes.
- Configure `config.toml` to tune depth/complexity/pagination settings.

