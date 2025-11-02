# Quickstart: SaaS Starter Enhancement

**Feature**: 017-saas-starter-enhancement  
**Audience**: Developers implementing the enhanced SaaS starter  
**Prerequisites**: Completed Phase 0 research, understand data models and contracts

## Overview

This quickstart guides you through implementing the comprehensive SaaS starter enhancement, from expanded technology options to multi-tenant patterns and migration tools.

## Implementation Phases

### Phase 1: Expand Copier Configuration (Week 1-2)

**Goal**: Add new prompts and validation logic to `template/copier.yml`

```bash
# 1. Update copier.yml with expanded options
cd template/
vim copier.yml

# 2. Add validation logic for compatibility
# See: specs/017-saas-starter-enhancement/contracts/copier-prompts.yml

# 3. Test new prompts
copier copy . /tmp/test-render --vcs-ref=HEAD

# 4. Verify validation catches incompatibilities
copier copy . /tmp/test-render \
  --data saas_hosting=cloudflare \
  --data saas_database=planetscale
# Should show compatibility warning
```

**Key Files**:
- `template/copier.yml` - Add new prompts
- `template/hooks/pre_gen_project.py` - Add validation logic

**Validation**:
```bash
# Run validation script
uv run python scripts/ci/validate_saas_combinations.py

# Should report 100+ valid combinations
```

---

### Phase 2: Create Integration Templates (Week 3-6)

**Goal**: Build Jinja2 templates for all 80+ technology integrations

```bash
# Directory structure
mkdir -p template/files/node/saas/integrations/{database,auth,storage,email,ai}
mkdir -p template/files/node/saas/integrations/{search,cache,feature-flags,cms,metering}

# Example: PlanetScale database integration
cat > template/files/node/saas/integrations/database/planetscale/client.ts.jinja << 'EOF'
{% if saas_database == 'planetscale' %}
import { connect } from '@planetscale/database';

export const db = connect({
  host: process.env.DATABASE_HOST,
  username: process.env.DATABASE_USERNAME,
  password: process.env.DATABASE_PASSWORD,
});
{% endif %}
EOF
```

**Implementation Order** (by priority):
1. Expanded original categories (P1) - Weeks 3-4
   - Database: PlanetScale, CockroachDB
   - Auth: WorkOS, Supabase Auth
   - Storage: S3, UploadThing
   - Email: SendGrid, SES

2. New infrastructure categories (P1) - Week 5
   - Search: Algolia, Meilisearch, Typesense
   - Cache: Redis/Upstash, Cloudflare KV, Vercel KV

3. Additional categories (P2) - Week 6
   - Feature Flags: LaunchDarkly, PostHog, GrowthBook
   - CMS: Contentful, Sanity, Payload, Strapi

**Testing Each Integration**:
```bash
# Render with specific integration
copier copy . /tmp/test-{integration} \
  --data saas_database=planetscale

# Verify files generated
ls -la /tmp/test-planetscale/lib/database/

# Run integration tests
cd /tmp/test-planetscale
pnpm install
pnpm test:integration
```

---

### Phase 3: Configuration Builder UI (Week 7-8)

**Goal**: Build interactive web UI for configuration

```bash
# Create configuration builder app
mkdir -p config-builder/{app,components,lib}

# Next.js app for visual config
cat > config-builder/app/page.tsx << 'EOF'
import { CategoryGrid } from '@/components/category-grid';
import { CostEstimator } from '@/components/cost-estimator';
import { ArchitectureDiagram } from '@/components/diagram';

export default function ConfigBuilder() {
  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="col-span-2">
        <CategoryGrid />
      </div>
      <div>
        <CostEstimator />
        <ArchitectureDiagram />
      </div>
    </div>
  );
}
EOF

# Development server
cd config-builder
pnpm dev
# Visit http://localhost:3000
```

**Key Components**:
1. **CategoryGrid**: Display all infrastructure categories
2. **OptionCard**: Individual technology option with details
3. **ValidationPanel**: Real-time compatibility checking
4. **CostEstimator**: Calculate costs at different scales
5. **DiagramGenerator**: Mermaid/SVG architecture diagrams

**API Routes**:
```typescript
// config-builder/app/api/validate/route.ts
export async function POST(req: Request) {
  const selections = await req.json();
  const validation = await validateSelections(selections);
  return Response.json(validation);
}

// config-builder/app/api/estimate/route.ts
export async function POST(req: Request) {
  const selections = await req.json();
  const estimate = await calculateCosts(selections);
  return Response.json(estimate);
}
```

**Testing**:
```bash
# E2E tests with Playwright
pnpm test:e2e

# Should test:
# - Selecting options updates validation
# - Cost estimates update in real-time
# - Export generates valid copier-answers.yml
# - Import loads existing configurations
```

---

### Phase 4: Migration Tool CLI (Week 9-10)

**Goal**: Build tool for swapping technologies post-generation

```bash
# Create migration tool
mkdir -p cli/commands/migrate

# Basic structure
cat > cli/commands/migrate/index.ts << 'EOF'
import { Command } from 'commander';
import { analyzeCurrent } from './analyze';
import { generatePlan } from './plan';
import { executeMigration } from './execute';

export const migrateCommand = new Command('migrate')
  .option('--from <tech>', 'Source technology')
  .option('--to <tech>', 'Target technology')
  .option('--category <cat>', 'Category to migrate')
  .option('--dry-run', 'Show changes without applying')
  .action(async (options) => {
    const analysis = await analyzeCurrent();
    const plan = await generatePlan(analysis, options);
    
    if (options.dryRun) {
      console.log(plan);
      return;
    }
    
    await executeMigration(plan);
  });
EOF
```

**Migration Strategies** (see contracts/migration-api.md):
```typescript
// Strategy pattern for different migration types
interface MigrationStrategy {
  analyze(): Promise<AnalysisResult>;
  generatePlan(): Promise<MigrationPlan>;
  execute(plan: MigrationPlan): Promise<void>;
  rollback(): Promise<void>;
}

// Example: Auth migration
class AuthMigrationStrategy implements MigrationStrategy {
  async analyze() {
    // Find all Clerk usage
    const files = await glob('**/*.{ts,tsx}');
    const usages = files.filter(f => 
      /import.*@clerk/.test(fs.readFileSync(f, 'utf-8'))
    );
    return { files: usages, integrationPoints: usages.length };
  }
  
  async generatePlan() {
    // Generate file diffs Clerk → WorkOS
    return {
      filesToModify: [/* ... */],
      dependencyChanges: {
        remove: ['@clerk/nextjs'],
        add: ['@workos-inc/authkit-nextjs']
      }
    };
  }
}
```

**Testing Migration Tool**:
```bash
# Generate test app with Clerk
copier copy . /tmp/migration-test --data saas_auth=clerk

cd /tmp/migration-test
pnpm install

# Migrate to WorkOS
riso migrate --from=clerk --to=workos --category=auth

# Verify migration succeeded
pnpm build
pnpm test

# Test rollback
riso migrate --rollback
pnpm test
# Should pass with Clerk restored
```

---

### Phase 5: Multi-Tenant Patterns (Week 11-12)

**Goal**: Implement multi-tenant architecture templates

```bash
# Create multi-tenant templates
mkdir -p template/files/node/saas/multi-tenant/{rls,schema,database}

# RLS pattern
cat > template/files/node/saas/multi-tenant/rls/middleware.ts.jinja << 'EOF'
{% if saas_architecture == 'multi-tenant-rls' %}
import { db } from '@/lib/database';

export async function setTenantContext(tenantId: string) {
  await db.$executeRaw`
    SELECT set_config('app.current_tenant_id', ${tenantId}, TRUE)
  `;
}
{% endif %}
EOF
```

**Implementation Components**:
1. **Tenant Provisioning API** (contracts/multi-tenant-patterns.md)
2. **Subdomain Routing Middleware**
3. **RLS Policies** (for PostgreSQL databases)
4. **Tenant Admin Portal**
5. **Usage Tracking per Tenant**

**Testing Multi-Tenancy**:
```bash
# Generate multi-tenant app
copier copy . /tmp/multi-tenant-test \
  --data saas_architecture=multi-tenant-rls

cd /tmp/multi-tenant-test

# Run isolation tests
pnpm test:isolation
# Should verify cross-tenant access is blocked

# Load test with multiple tenants
pnpm test:load --tenants=10 --users-per-tenant=100
```

---

### Phase 6: Enhanced Development Tools (Week 13-14)

**Goal**: Build unified dev dashboard and one-command setup

```bash
# Dev dashboard
mkdir -p dev-tools/dashboard

# Dashboard shows status of all services
cat > dev-tools/dashboard/index.tsx << 'EOF'
export function DevDashboard() {
  return (
    <div>
      <ServiceStatus service="database" />
      <ServiceStatus service="cache" />
      <ServiceStatus service="search" />
      <ServiceStatus service="auth" />
      {/* ... */}
    </div>
  );
}
EOF

# One-command setup script
cat > scripts/dev-setup.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Setting up development environment..."

# Start docker services
docker-compose up -d

# Wait for services
./scripts/wait-for-services.sh

# Run migrations
pnpm db:migrate

# Seed fixtures
pnpm db:seed

# Validate env vars
pnpm env:validate

echo "✅ Development environment ready!"
echo "   Run 'pnpm dev' to start the application"
EOF
```

**Key Features**:
1. **Unified Dashboard**: Shows all service health
2. **One-Command Setup**: `pnpm dev:setup` initializes everything
3. **Offline Mode**: Mock external services
4. **Log Aggregation**: Unified view of all logs
5. **Fixture Management**: Quick data resets

---

### Phase 7: Production Patterns (Week 15-16)

**Goal**: Add multi-region, blue-green deployment templates

```bash
# Infrastructure as code
mkdir -p infra/{terraform,pulumi}

# Multi-region Terraform
cat > infra/terraform/multi-region.tf << 'EOF'
{% if saas_deployment_pattern == 'multi-region' %}
# Primary region
resource "vercel_project" "app_us_east" {
  name = "${var.project_name}-us-east"
  framework = "nextjs"
  region = "iad1"
}

# Secondary region
resource "vercel_project" "app_eu_west" {
  name = "${var.project_name}-eu-west"
  framework = "nextjs"
  region = "cdg1"
}

# Failover DNS
resource "cloudflare_load_balancer" "app" {
  zone_id = var.cloudflare_zone_id
  name = "${var.project_name}.com"
  default_pool_ids = [
    cloudflare_load_balancer_pool.us.id,
    cloudflare_load_balancer_pool.eu.id
  ]
  steering_policy = "geo"
}
{% endif %}
EOF
```

**Patterns to Implement**:
1. **Multi-Region**: Deploy to 3+ regions with DNS failover
2. **Blue-Green**: Zero-downtime deployments
3. **Read Replicas**: Database load balancing
4. **CDN Integration**: Static asset optimization
5. **Disaster Recovery**: Automated backups and restoration

---

## Validation Checklist

After each phase, verify:

### Configuration & Generation
- [ ] Config builder displays all categories correctly
- [ ] Real-time validation catches incompatibilities
- [ ] Cost estimates accurate within 25%
- [ ] Architecture diagrams generate successfully
- [ ] Export produces valid `copier-answers.yml`
- [ ] 100+ technology combinations supported

### Generated Applications
- [ ] All integrations initialize correctly
- [ ] Health checks pass for all services
- [ ] Authentication flows work end-to-end
- [ ] Database connections established
- [ ] Tests achieve 80%+ coverage
- [ ] Applications deploy successfully

### Migration Tools
- [ ] Migration analysis detects all affected files
- [ ] Generated plans show accurate diffs
- [ ] Migrations execute without errors
- [ ] Tests pass post-migration
- [ ] Rollback restores previous state
- [ ] Custom code preserved through merges

### Multi-Tenant
- [ ] Tenant provisioning completes in <30 seconds
- [ ] Data isolation tests pass (0 cross-tenant leaks)
- [ ] Subdomain routing works correctly
- [ ] Per-tenant feature flags function
- [ ] Usage tracking records accurately

### Development Tools
- [ ] One-command setup completes in <5 minutes
- [ ] Dev dashboard shows accurate service status
- [ ] Offline mode mocks all external services
- [ ] Fixture generation creates 1000+ records <15s
- [ ] Log aggregation displays all service logs

### Production Patterns
- [ ] Multi-region deployments succeed
- [ ] Blue-green deployments execute with zero downtime
- [ ] Automatic failover works within 60 seconds
- [ ] Backups complete and restore successfully
- [ ] Compliance controls (GDPR/SOC2/HIPAA) configured

## Performance Targets

- Template generation: <7 minutes (up from 5 min)
- Application startup: <3 minutes (up from 2 min)
- Deployment time: <12 minutes (up from 10 min)
- Config builder load: <2 seconds
- Migration tool analysis: <30 seconds
- Tenant provisioning: <30 seconds

## Success Metrics

Track these metrics throughout implementation:

1. **Technology Coverage**: 80+ integrations supported
2. **Valid Combinations**: 100+ working combinations
3. **Developer Satisfaction**: 92% setup without support
4. **Migration Success**: 95% successful swaps
5. **Multi-Tenant Isolation**: 100% zero cross-tenant leaks
6. **Test Coverage**: 80%+ across all templates
7. **Production Uptime**: 99.9% availability

## Troubleshooting

Common issues and solutions:

**Issue**: Copier validation fails with new prompts
**Solution**: Check `template/hooks/pre_gen_project.py` logic

**Issue**: Integration template not rendering
**Solution**: Verify Jinja2 conditionals match prompt IDs

**Issue**: Migration tool can't detect technology
**Solution**: Add detection pattern to analysis phase

**Issue**: Multi-tenant RLS not enforcing isolation
**Solution**: Verify PostgreSQL RLS policies enabled

**Issue**: Dev dashboard shows services as down
**Solution**: Check docker-compose and port conflicts

## Next Steps

After completing implementation:

1. Run full test suite: `pnpm test:all`
2. Generate all sample configurations: `./scripts/render-samples.sh`
3. Update documentation: `docs/modules/saas-starter-enhanced.md`
4. Create upgrade guide from 012-saas-starter
5. Submit PR with comprehensive test evidence

## Resources

- [Spec Document](./spec.md)
- [Data Models](./data-model.md)
- [API Contracts](./contracts/)
- [Research Notes](./research.md)
- [Implementation Plan](./plan.md)
