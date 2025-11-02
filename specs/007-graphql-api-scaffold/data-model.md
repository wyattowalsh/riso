# Data Model: GraphQL API Scaffold

**Purpose**: capture core types, pagination shapes, and context model for the scaffold.

## Core Types

- User
  - id: ID!
  - name: String!
  - email: String!
  - avatar: String
  - posts: [Post]

- Post
  - id: ID!
  - authorId: ID!
  - title: String!
  - body: String
  - createdAt: DateTime

## Pagination Types

- PageInfo
  - hasNextPage: Boolean!
  - hasPreviousPage: Boolean!
  - startCursor: String
  - endCursor: String

- Connection / Edge pattern for each listable type (Relay)

## Context Shape

The GraphQL context object (request-scoped) should include:

- request: FastAPI Request
- current_user: Optional[User]
- db: Async DB session/connection
- dataloaders: container with per-request DataLoader instances
- config: GraphQL runtime config (depth/complexity limits, pagination defaults)

## DataLoader Signatures

- user_loader: async def load_many(user_ids: List[ID]) -> List[User]
- posts_by_author_loader: async def load_many(author_ids: List[ID]) -> List[List[Post]]

Notes:

- DataLoaders should be created on each request and stored on the context to avoid cross-request caching.

