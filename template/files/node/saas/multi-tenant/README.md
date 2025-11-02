# Multi-Tenant Architecture Patterns

This directory contains templates for multi-tenant B2B SaaS architectures with three isolation levels.

## Isolation Levels

### 1. Row-Level Security (RLS) - `rls/`

**Best for**: Startups, <10K tenants, cost-optimization

PostgreSQL row-level security with `tenant_id` column. All tenants share same schema.

**Files**:
- `policies.sql.jinja` - RLS policies
- `middleware.ts.jinja` - Tenant context middleware
- `queries.ts.jinja` - Tenant-scoped query helpers

**Pros**:
- Simple to implement
- Cost-effective
- Minimal performance overhead (<5%)

**Cons**:
- Shared schema (less customization)
- Application bugs risk isolation
- All tenants in same database

### 2. Schema-Per-Tenant - `schema-per-tenant/`

**Best for**: Growth stage, 100-10K tenants, B2B SaaS

Separate PostgreSQL schema per tenant with dynamic connection routing.

**Files**:
- `provisioning.ts.jinja` - Tenant provisioning API
- `routing.ts.jinja` - Connection routing logic
- `migrations.ts.jinja` - Multi-tenant migration runner

**Pros**:
- Better isolation than RLS
- Per-tenant schema customization
- Moderate complexity

**Cons**:
- Schema limits (~10K per DB)
- More complex migrations
- Connection pool management

### 3. Database-Per-Tenant - `db-per-tenant/`

**Best for**: Enterprise, <1K tenants, regulatory compliance

Separate database instance per tenant with isolated connection pools.

**Files**:
- `provisioning.ts.jinja` - Database provisioning workflow
- `connection-pool.ts.jinja` - Per-tenant connection management
- `backup.ts.jinja` - Per-tenant backup automation

**Pros**:
- Strongest isolation
- Complete customization
- Easy per-tenant backups
- Regulatory compliance ready

**Cons**:
- Highest cost
- Complex connection management
- Harder cross-tenant queries

## Common Components

All isolation levels include:

- **Tenant Provisioning API**: Automated tenant setup
- **Subdomain Routing**: Maps subdomains to tenant context
- **Admin Portal**: Tenant management UI
- **Per-Tenant Features**: Feature flags, usage tracking, billing
- **Security Tests**: Isolation validation

## Usage

Select multi-tenant pattern in copier prompts:

```yaml
saas_architecture: multi-tenant
saas_multi_tenant_isolation: rls  # or schema-per-tenant, db-per-tenant
```

## Status

- **Phase 7**: Multi-tenant patterns (Planned)

Last Updated: 2025-11-02
