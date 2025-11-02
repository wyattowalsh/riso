# Integration Guide: SaaS Starter Enhancement

**Feature**: 017-saas-starter-enhancement  
**Created**: 2025-11-02  
**Status**: Planning Phase

## Overview

This guide explains how the SaaS Starter Enhancement integrates with the existing Riso template system and 012-saas-starter baseline. It provides concrete examples of how each phase connects to existing code.

---

## Current State: 012-saas-starter Baseline

### Existing Structure

```text
template/
├── copier.yml                 # Current prompts (14 categories, 2 options each)
├── files/
│   └── node/saas/             # Existing SaaS templates
│       ├── runtime/
│       │   └── nextjs/        # Next.js only currently
│       ├── integrations/
│       │   ├── auth/          # Clerk, Auth.js
│       │   ├── database/      # Neon, Supabase
│       │   ├── billing/       # Stripe, Paddle
│       │   └── ...            # 14 categories × 2 options
│       └── tests/
└── hooks/
    └── pre_gen_project.py     # Basic validation

scripts/
└── ci/
    └── validate_saas.py       # Basic validation

samples/
└── saas-starter/              # Sample configurations
    ├── edge-optimized/
    └── all-in-one/
```

### Key Files to Understand

**copier.yml** (template/copier.yml)
```yaml
# Current structure (simplified)
saas_runtime:
  type: str
  choices:
    - nextjs-14
  help: "JavaScript runtime framework"

saas_database:
  type: str
  choices:
    - neon
    - supabase
  help: "Database provider"

# ... 14 categories total
```

**Validation Hook** (template/hooks/pre_gen_project.py)
```python
def validate_saas_selections(context):
    """Basic validation of SaaS selections"""
    runtime = context.get('saas_runtime')
    database = context.get('saas_database')
    # Simple validation logic
    return True
```

**Integration Template** (template/files/node/saas/integrations/database/neon/client.ts.jinja)
```typescript
{% if saas_database == 'neon' %}
import { neon } from '@neondatabase/serverless';

export const sql = neon(process.env.DATABASE_URL);
{% endif %}
```

---

## Phase 1-2: Foundation Integration

### How Foundation Integrates with Existing Code

#### T001: Enhanced copier.yml

**Before (012-saas-starter)**:
```yaml
# 14 categories with 2 options each
saas_runtime:
  type: str
  choices:
    - nextjs-14
  
saas_database:
  type: str
  choices:
    - neon
    - supabase
```

**After (017-saas-starter-enhancement)**:
```yaml
# 14 categories expanded to 4 options each
saas_runtime:
  type: str
  choices:
    - nextjs-16: "Next.js 16 (React Server Components, App Router)"
    - remix-2x: "Remix 2.x (Full-stack React framework)"
    - sveltekit-2x: "SvelteKit 2.x (Svelte framework)"
    - astro-4x: "Astro 4.x (Content-focused sites)"
  help: "JavaScript runtime framework"
  when: "{{ saas_starter_module }}"  # Only when SaaS module enabled

saas_database:
  type: str
  choices:
    - neon: "Neon (Serverless Postgres, best DX)"
    - supabase: "Supabase (Open-source, all-in-one)"
    - planetscale: "PlanetScale (MySQL, horizontal sharding)"
    - cockroachdb: "CockroachDB (Multi-region, strong consistency)"
  help: "Database provider"

# + 7 NEW categories
saas_search:
  type: str
  choices:
    - algolia: "Algolia (Premium, best UX)"
    - meilisearch: "Meilisearch (Open-source, self-hosted)"
    - typesense: "Typesense (Geo-search, vector search)"
    - none: "No search integration"
  default: none
  help: "Search provider (optional)"
```

**Integration Points**:
1. **Backward compatibility**: Existing 012 configurations still work
2. **Conditional prompts**: New categories only shown when relevant
3. **Default values**: Optional categories default to "none"
4. **Help text**: Expanded to include use-when guidance

#### T002: Enhanced Validation Hook

**Before (template/hooks/pre_gen_project.py)**:
```python
def validate_saas_selections(context):
    # Simple validation
    return True
```

**After (template/hooks/pre_gen_project.py)**:
```python
from compatibility_matrix import validate_compatibility

def validate_saas_selections(context):
    """Enhanced validation with compatibility rules"""
    selections = {
        'runtime': context.get('saas_runtime'),
        'hosting': context.get('saas_hosting'),
        'database': context.get('saas_database'),
        # ... all 21 categories
    }
    
    result = validate_compatibility(selections)
    
    if result['errors']:
        for error in result['errors']:
            print(f"ERROR: {error['message']}")
            print(f"Suggestions: {', '.join(error['suggestions'])}")
        raise ValueError("Invalid technology combination")
    
    if result['warnings']:
        for warning in result['warnings']:
            print(f"WARNING: {warning['message']}")
    
    return True
```

**Integration Points**:
1. **Imports new module**: Uses `compatibility_matrix.py`
2. **Collects all selections**: Gathers from context
3. **Validates rules**: Checks compatibility
4. **Reports issues**: Clear error/warning messages
5. **Backward compatible**: Existing validations still work

#### T003: Compatibility Validation Module

**New File (scripts/saas/compatibility_matrix.py)**:
```python
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class CompatibilityRule:
    id: str
    condition_type: str  # 'requires', 'conflicts_with', 'warns_with'
    severity: str  # 'error', 'warning', 'info'
    source_technology: str
    target_technologies: List[str]
    message: str
    suggestions: List[str]

# Define rules
COMPATIBILITY_RULES = [
    CompatibilityRule(
        id="cloudflare-no-traditional-db",
        condition_type="conflicts_with",
        severity="error",
        source_technology="cloudflare",
        target_technologies=["neon", "planetscale", "cockroachdb"],
        message="Cloudflare Workers cannot use traditional database connections",
        suggestions=["Use Cloudflare D1", "Switch to Vercel hosting", "Use Supabase REST API"]
    ),
    CompatibilityRule(
        id="supabase-auth-requires-db",
        condition_type="requires",
        severity="error",
        source_technology="supabase-auth",
        target_technologies=["supabase"],
        message="Supabase Auth requires Supabase database",
        suggestions=["Switch to Clerk/Auth.js", "Use Supabase database"]
    ),
    # ... 50+ more rules
]

def validate_compatibility(selections: Dict[str, str]) -> Dict[str, Any]:
    """Validate technology selections against compatibility rules"""
    errors = []
    warnings = []
    info = []
    
    for rule in COMPATIBILITY_RULES:
        if rule.source_technology in selections.values():
            # Check rule condition
            if rule.condition_type == "conflicts_with":
                for target in rule.target_technologies:
                    if target in selections.values():
                        item = {
                            'rule_id': rule.id,
                            'message': rule.message,
                            'suggestions': rule.suggestions
                        }
                        if rule.severity == 'error':
                            errors.append(item)
                        elif rule.severity == 'warning':
                            warnings.append(item)
                        else:
                            info.append(item)
            # ... handle other condition types
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'info': info
    }
```

**Integration Points**:
1. **Imported by validation hook**: Direct integration
2. **Called during prompt phase**: Real-time validation
3. **Used by config builder**: API endpoint validation
4. **Tested independently**: Unit tests in tests/

---

## Phase 3: Integration Template Pattern

### How New Integrations Integrate with Existing System

#### Example: PlanetScale Integration (T023)

**New Directory Structure**:
```text
template/files/node/saas/integrations/database/planetscale/
├── client.ts.jinja              # Database client initialization
├── config.ts.jinja              # Configuration
├── types.ts.jinja               # TypeScript types
├── middleware.ts.jinja          # Connection middleware
├── migrations/                  # Migration scripts
│   └── README.md.jinja
├── examples/                    # Usage examples
│   ├── basic-query.ts.jinja
│   └── transaction.ts.jinja
└── README.md.jinja             # Documentation
```

**Integration Template** (client.ts.jinja):
```typescript
{% if saas_database == 'planetscale' %}
import { connect } from '@planetscale/database';

// PlanetScale connection using DATABASE_URL from environment
export const db = connect({
  url: process.env.DATABASE_URL
});

// Connection helper with error handling
export async function getConnection() {
  try {
    return db;
  } catch (error) {
    console.error('PlanetScale connection failed:', error);
    throw new Error('Database connection unavailable');
  }
}
{% endif %}
```

**How It Works**:
1. **Conditional Rendering**: Only included when `saas_database == 'planetscale'`
2. **Environment Variables**: Uses standard `DATABASE_URL` pattern
3. **Error Handling**: Consistent with other integrations
4. **Export Pattern**: Standard `db` and `getConnection` exports

**Integration with ORM** (template/files/node/saas/integrations/orm/prisma/client.ts.jinja):
```typescript
{% if saas_orm == 'prisma' %}
import { PrismaClient } from '@prisma/client';

{% if saas_database == 'planetscale' %}
// PlanetScale-specific configuration for Prisma
const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL
    }
  },
  // Disable foreign key constraints for PlanetScale compatibility
  engineType: 'binary',
  foreignKeys: false
});
{% else %}
// Standard Prisma configuration
const prisma = new PrismaClient();
{% endif %}

export default prisma;
{% endif %}
```

**Integration Points**:
1. **Nested conditionals**: Prisma + PlanetScale specific config
2. **Database-aware**: Handles PlanetScale's no-foreign-keys requirement
3. **Maintains compatibility**: Works with other databases too
4. **Standard export**: Always exports `prisma` client

---

## Phase 4: New Category Integration

### How New Categories Integrate

#### Example: Search Category

**Copier Prompt** (template/copier.yml):
```yaml
saas_search:
  type: str
  choices:
    - algolia: "Algolia (Premium, analytics, merchandising)"
    - meilisearch: "Meilisearch (Open-source, self-hosted)"
    - typesense: "Typesense (Geo-search, vector search)"
    - none: "No search integration"
  default: none
  help: "Search provider for full-text search (optional)"
  when: "{{ saas_starter_module }}"
```

**Integration with Database** (template/files/node/saas/integrations/search/algolia/sync.ts.jinja):
```typescript
{% if saas_search == 'algolia' %}
import algoliasearch from 'algoliasearch';
{% if saas_database == 'neon' %}
import { sql } from '@/lib/database';
{% elif saas_database == 'supabase' %}
import { supabase } from '@/lib/database';
{% elif saas_database == 'planetscale' %}
import { db } from '@/lib/database';
{% endif %}

const client = algoliasearch(
  process.env.ALGOLIA_APP_ID!,
  process.env.ALGOLIA_ADMIN_KEY!
);
const index = client.initIndex('products');

// Database change listener (example with Supabase)
{% if saas_database == 'supabase' %}
export async function setupSearchSync() {
  // Listen to database changes
  const subscription = supabase
    .channel('product-changes')
    .on('postgres_changes', 
      { event: '*', schema: 'public', table: 'products' },
      async (payload) => {
        if (payload.eventType === 'INSERT' || payload.eventType === 'UPDATE') {
          // Index to Algolia
          await index.saveObject({
            objectID: payload.new.id,
            ...payload.new
          });
        } else if (payload.eventType === 'DELETE') {
          await index.deleteObject(payload.old.id);
        }
      }
    )
    .subscribe();
  
  return subscription;
}
{% endif %}
{% endif %}
```

**Integration Points**:
1. **Cross-category awareness**: Search integrates with selected database
2. **Database-specific patterns**: Uses Supabase realtime, Neon triggers, etc.
3. **Conditional logic**: Different sync patterns per database
4. **Environment variables**: Consistent naming (ALGOLIA_APP_ID, etc.)

**Documentation Generation** (docs/modules/saas-starter-enhanced.md.jinja):
```jinja2
## Search Integration

{% if saas_search != 'none' %}
### {{ saas_search | title }} Configuration

Your application is configured with {{ saas_search }} for full-text search.

**Environment Variables**:
{% if saas_search == 'algolia' %}
- `ALGOLIA_APP_ID`: Your Algolia application ID
- `ALGOLIA_ADMIN_KEY`: Your Algolia admin API key
- `ALGOLIA_SEARCH_KEY`: Your Algolia search-only API key
{% elif saas_search == 'meilisearch' %}
- `MEILISEARCH_HOST`: Your Meilisearch instance URL
- `MEILISEARCH_API_KEY`: Your Meilisearch API key
{% endif %}

**Database Integration**:
{% if saas_database == 'supabase' %}
Search indices are automatically synced with your Supabase database using realtime subscriptions.
{% elif saas_database == 'neon' or saas_database == 'planetscale' %}
Search indices can be synced using the provided webhook endpoints or scheduled jobs.
{% endif %}

{% else %}
No search integration configured. To add search later, refer to the migration guide.
{% endif %}
```

**Integration Points**:
1. **Conditional documentation**: Only shows if search enabled
2. **Service-specific guidance**: Tailored to selected search provider
3. **Cross-reference**: Mentions database integration patterns
4. **Migration guidance**: Points to upgrade path

---

## Phase 5: Configuration Builder Integration

### How Config Builder Uses Existing Infrastructure

**API Route** (config-builder/app/api/validate/route.ts):
```typescript
import { NextRequest, NextResponse } from 'next/server';
// Import from existing compatibility module
import { validateCompatibility } from '@/lib/compatibility';

export async function POST(req: NextRequest) {
  const selections = await req.json();
  
  // Use same validation logic as Copier hook
  const result = validateCompatibility(selections);
  
  return NextResponse.json({
    valid: result.valid,
    errors: result.errors,
    warnings: result.warnings,
    info: result.info
  });
}
```

**Shared Logic Library** (config-builder/lib/compatibility.ts):
```typescript
// This wraps the Python validation module for use in TypeScript
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function validateCompatibility(selections: Record<string, string>) {
  // Call Python validation module
  const { stdout } = await execAsync(
    `python scripts/saas/compatibility_matrix.py '${JSON.stringify(selections)}'`
  );
  
  return JSON.parse(stdout);
}
```

**Integration Points**:
1. **Reuses validation logic**: Same rules as Copier hook
2. **Python-TypeScript bridge**: Calls existing Python module
3. **Real-time in UI**: Provides instant feedback
4. **Consistent behavior**: Same validations across tools

---

## Phase 6: Migration Tool Integration

### How Migration Tool Uses Templates

**Migration Strategy** (cli/commands/migrate/strategies/database-migration.ts):
```typescript
import { MigrationStrategy } from './base-strategy';
import { readFile } from 'fs/promises';
import { glob } from 'glob';

export class DatabaseMigrationStrategy extends MigrationStrategy {
  async analyze() {
    // Find all database usage in project
    const files = await glob('**/*.{ts,tsx}', { ignore: 'node_modules/**' });
    const usages = [];
    
    for (const file of files) {
      const content = await readFile(file, 'utf-8');
      // Detect current database (e.g., import from '@neondatabase/serverless')
      if (content.includes('@neondatabase/serverless')) {
        usages.push({ file, technology: 'neon' });
      } else if (content.includes('@planetscale/database')) {
        usages.push({ file, technology: 'planetscale' });
      }
    }
    
    return { files: usages, currentTechnology: 'neon' };
  }
  
  async generatePlan(analysis, targetTechnology: string) {
    // Load new integration template
    const newTemplate = await readFile(
      `template/files/node/saas/integrations/database/${targetTechnology}/client.ts.jinja`,
      'utf-8'
    );
    
    // Generate transformation plan
    return {
      filesToModify: analysis.files.map(f => f.file),
      template: newTemplate,
      dependencies: {
        remove: ['@neondatabase/serverless'],
        add: ['@planetscale/database']
      }
    };
  }
}
```

**Integration Points**:
1. **Uses existing templates**: Reads from template/ directory
2. **Pattern detection**: Identifies current technology from code
3. **Template-driven transformation**: New code from integration templates
4. **Dependency management**: Updates package.json

---

## Backward Compatibility Strategy

### Ensuring 012-saas-starter Configs Still Work

**copier.yml Compatibility**:
```yaml
# Old prompt (012-saas-starter)
saas_runtime:
  type: str
  choices:
    - nextjs-14
  default: nextjs-14

# New prompt (017-saas-starter-enhancement) - Backward compatible
saas_runtime:
  type: str
  choices:
    - nextjs-16: "Next.js 16 (recommended)"
    - nextjs-14: "Next.js 14 (legacy, for compatibility)"
    - remix-2x: "Remix 2.x"
    - sveltekit-2x: "SvelteKit 2.x"
    - astro-4x: "Astro 4.x"
  default: nextjs-16  # Updated default, but nextjs-14 still works
```

**Template Compatibility**:
```jinja2
{% if saas_runtime == 'nextjs-14' or saas_runtime == 'nextjs-16' %}
{# Both versions supported #}
import { NextConfig } from 'next';

{% if saas_runtime == 'nextjs-14' %}
{# Legacy Next.js 14 configuration #}
const config: NextConfig = {
  // Next.js 14 specific settings
};
{% else %}
{# Next.js 16 configuration #}
const config: NextConfig = {
  // Next.js 16 specific settings
};
{% endif %}
{% endif %}
```

**Migration Path**:
1. **Existing users**: Can continue using 012 configurations
2. **Gradual adoption**: Can upgrade one category at a time
3. **Deprecation warnings**: Inform users of legacy options
4. **Migration tool**: Automated upgrade from 012 to 017

---

## Testing Integration

### How Tests Integrate with Existing CI

**Existing CI** (.github/workflows/riso-quality.yml):
```yaml
name: Quality Checks
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run quality checks
        run: make quality
```

**Enhanced CI** (.github/workflows/riso-saas-validation.yml):
```yaml
name: SaaS Validation
on: [push, pull_request]
jobs:
  validate-combinations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install copier jinja2 pyyaml
      
      - name: Validate compatibility rules
        run: |
          python scripts/ci/validate_saas_combinations.py
      
      - name: Render sample configurations
        run: |
          python scripts/ci/render_saas_samples.py
      
      - name: Run integration tests
        run: |
          pytest tests/saas_integrations/
```

**Integration Points**:
1. **Parallel workflows**: Runs alongside existing quality checks
2. **Shared setup**: Uses same Python/Node versions
3. **Separate concerns**: SaaS validation independent
4. **Fast feedback**: Fails early on incompatibilities

---

## Development Workflow

### How Developers Work with Enhancement

**Before (012-saas-starter)**:
```bash
# Generate a SaaS application
copier copy gh:wyattowalsh/riso my-saas-app

# Answer prompts (14 questions, 2 options each)
# Runtime: nextjs-14
# Database: neon
# Auth: clerk
# ...

cd my-saas-app
pnpm install
pnpm dev
```

**After (017-saas-starter-enhancement)**:
```bash
# Option 1: Use configuration builder
cd riso
pnpm config:builder  # Opens web UI at http://localhost:3000
# Visually select 21 categories × 4 options
# See real-time validation and cost estimates
# Export copier-answers.yml

# Option 2: Use CLI TUI
riso config --tui
# Terminal-based selection with arrow keys
# Export copier-answers.yml

# Option 3: Use Copier directly (backward compatible)
copier copy gh:wyattowalsh/riso my-saas-app --answers-file=copier-answers.yml

# Or answer prompts interactively (21 questions, up to 4 options each)

cd my-saas-app
pnpm install

# One-command setup (new feature)
pnpm dev:setup  # Starts all services, runs migrations, seeds fixtures

# Launch dev dashboard (new feature)
pnpm dev:dashboard  # Opens http://localhost:3001

# Start application
pnpm dev

# Later: Migrate technology
riso migrate --from=neon --to=planetscale --category=database
```

**Integration Points**:
1. **Multiple entry points**: Config builder, TUI, or direct Copier
2. **Backward compatible**: Old workflow still works
3. **Enhanced features**: Optional dev tools improve experience
4. **Migration path**: Change technologies post-generation

---

## Deployment Integration

### How Production Patterns Integrate

**Before (012-saas-starter)**:
```bash
# Basic Vercel deployment
vercel deploy
```

**After (017-saas-starter-enhancement with production patterns)**:
```bash
# Multi-region deployment with blue-green
cd infra/terraform
terraform init
terraform plan -var="regions=[\"us-east-1\", \"us-west-1\", \"eu-west-1\"]"
terraform apply

# Blue-green deployment
./scripts/deploy-blue-green.sh

# Verify health checks
curl https://api.example.com/health

# Monitor deployment
open https://dashboard.vercel.com/deployments
```

**Generated Infrastructure** (infra/terraform/main.tf.jinja):
```hcl
{% if saas_deployment_pattern == 'multi-region' %}
# Multi-region deployment for {{ project_name }}

variable "regions" {
  type    = list(string)
  default = ["us-east-1", "us-west-1", "eu-west-1"]
}

# Deploy to each region
resource "vercel_project" "app" {
  for_each = toset(var.regions)
  
  name      = "{{ project_name }}-${each.value}"
  framework = "{{ saas_runtime }}"
  
  environment_variables = {
    DATABASE_URL = var.database_url
    # ... other environment variables
  }
}

# Health checks and failover
resource "cloudflare_load_balancer" "app" {
  zone_id = var.cloudflare_zone_id
  name    = "{{ project_name }}.com"
  
  default_pool_ids = [
    for region in var.regions : 
      cloudflare_load_balancer_pool.app[region].id
  ]
  
  steering_policy = "geo"
  
  {% if saas_deployment_pattern contains 'blue-green' %}
  session_affinity = "cookie"
  {% endif %}
}
{% endif %}
```

**Integration Points**:
1. **Optional patterns**: Only included if selected
2. **Technology-aware**: Works with selected runtime/hosting
3. **Environment variables**: Consistent with other integrations
4. **Standard tools**: Uses Terraform/Pulumi (industry standard)

---

## Summary

### Key Integration Patterns

1. **Conditional Inclusion**: Templates only rendered when selected
2. **Cross-Category Awareness**: Integrations know about other selections
3. **Backward Compatibility**: Existing configurations still work
4. **Shared Logic**: Validation, cost estimation reused across tools
5. **Standard Exports**: Consistent naming across integrations
6. **Documentation Generation**: Automatic docs from selections
7. **Progressive Enhancement**: Optional features don't break basic workflow

### Integration Points Checklist

Before implementing each phase, verify:

- [ ] **Templates** integrate with `copier.yml` prompts
- [ ] **Validation** integrates with `pre_gen_project.py` hook
- [ ] **Documentation** auto-generates from selections
- [ ] **Tests** integrate with existing CI workflows
- [ ] **Samples** demonstrate new capabilities
- [ ] **Backward compatibility** maintained with 012-saas-starter
- [ ] **Cross-category** awareness works correctly

---

**Document Status**: Planning Phase  
**Next Review**: Before Phase 1 implementation  
**Owner**: Technical Architect  
**Last Updated**: 2025-11-02
