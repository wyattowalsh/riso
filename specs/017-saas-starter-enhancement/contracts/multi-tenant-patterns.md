# Multi-Tenant Architecture Patterns

## Overview

Defines data models, API contracts, and implementation patterns for multi-tenant B2B SaaS architectures with three isolation levels.

## Isolation Levels

### 1. Row-Level Security (RLS)

**Use when**: Cost-efficient, 100s-1000s of tenants, PostgreSQL required

**Data Model**:
```sql
-- Add tenant_id to all tables
CREATE TABLE users (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  email TEXT NOT NULL,
  name TEXT,
  UNIQUE(tenant_id, email)
);

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their tenant's data
CREATE POLICY tenant_isolation ON users
  USING (tenant_id = current_setting('app.current_tenant_id')::UUID);
```

**Application Pattern**:
```typescript
// Set tenant context per request
async function withTenant<T>(
  tenantId: string,
  callback: () => Promise<T>
): Promise<T> {
  await db.$executeRaw`SELECT set_config('app.current_tenant_id', ${tenantId}, TRUE)`;
  return callback();
}

// Prisma middleware enforces tenant scoping
prisma.$use(async (params, next) => {
  if (params.model && !params.args.where?.tenant_id) {
    throw new Error('Tenant ID required for all queries');
  }
  return next(params);
});
```

### 2. Schema-per-Tenant

**Use when**: Medium isolation, schema customization needed, 10s-100s of tenants

**Data Model**:
```sql
-- Dynamic schema creation
CREATE SCHEMA tenant_abc123;
CREATE SCHEMA tenant_xyz789;

-- Standard tables in each schema
CREATE TABLE tenant_abc123.users (
  id UUID PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  name TEXT
);

CREATE TABLE tenant_xyz789.users (
  id UUID PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  name TEXT
);
```

**Application Pattern**:
```typescript
// Schema-aware connection
async function getTenantDB(tenantId: string) {
  const schemaName = `tenant_${tenantId}`;
  
  return new PrismaClient({
    datasources: {
      db: {
        url: `${process.env.DATABASE_URL}?schema=${schemaName}`
      }
    }
  });
}

// Usage
const tenantDB = await getTenantDB(tenant.id);
const users = await tenantDB.user.findMany();
```

### 3. Database-per-Tenant

**Use when**: Maximum isolation, compliance critical, enterprise customers

**Data Model**:
```sql
-- Separate database per tenant
-- Control plane database
CREATE TABLE tenants (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  database_host TEXT NOT NULL,
  database_name TEXT NOT NULL,
  connection_string TEXT NOT NULL ENCRYPTED,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Each tenant gets dedicated database
CREATE DATABASE tenant_abc123_prod;
CREATE DATABASE tenant_xyz789_prod;
```

**Application Pattern**:
```typescript
// Dynamic database connection
class TenantDatabaseManager {
  private connections = new Map<string, PrismaClient>();
  
  async getConnection(tenantId: string): Promise<PrismaClient> {
    if (this.connections.has(tenantId)) {
      return this.connections.get(tenantId)!;
    }
    
    const tenant = await controlPlane.tenant.findUnique({
      where: { id: tenantId }
    });
    
    const client = new PrismaClient({
      datasources: {
        db: { url: decrypt(tenant.connection_string) }
      }
    });
    
    this.connections.set(tenantId, client);
    return client;
  }
}
```

## Tenant Provisioning API

```typescript
interface TenantProvisioningRequest {
  name: string;
  subdomain: string;
  plan: 'starter' | 'professional' | 'enterprise';
  isolationLevel: 'rls' | 'schema' | 'database';
  owner: {
    email: string;
    name: string;
  };
  branding?: {
    primaryColor: string;
    logo: string;
    customDomain?: string;
  };
}

interface TenantProvisioningResponse {
  tenant: {
    id: string;
    name: string;
    subdomain: string;
    status: 'provisioning' | 'active' | 'suspended';
    urls: {
      app: string;
      admin: string;
      api: string;
    };
  };
  credentials: {
    adminApiKey: string;
    webhookSecret: string;
  };
  provisioning: {
    steps: Array<{
      name: string;
      status: 'completed' | 'in-progress' | 'pending';
      duration?: number;
    }>;
    estimatedCompletion: string;
  };
}
```

## Provisioning Workflow

```typescript
async function provisionTenant(req: TenantProvisioningRequest) {
  // 1. Validate subdomain availability
  await validateSubdomain(req.subdomain);
  
  // 2. Create tenant record (control plane)
  const tenant = await createTenantRecord(req);
  
  // 3. Initialize database/schema based on isolation level
  switch (req.isolationLevel) {
    case 'rls':
      // Just create tenant row, tables already exist
      break;
    case 'schema':
      await createTenantSchema(tenant.id);
      await runMigrations(tenant.id);
      break;
    case 'database':
      await createTenantDatabase(tenant.id);
      await runMigrations(tenant.id);
      await setupReplication(tenant.id);
      break;
  }
  
  // 4. Create admin user
  await createTenantAdmin(tenant.id, req.owner);
  
  // 5. Initialize default data
  await seedTenantDefaults(tenant.id, req.plan);
  
  // 6. Configure subdomain routing
  await configureDNS(req.subdomain, tenant.id);
  
  // 7. Setup monitoring and alerts
  await initializeTenantMonitoring(tenant.id);
  
  // 8. Mark as active
  await activateTenant(tenant.id);
  
  return tenant;
}
```

## Subdomain Routing

### Middleware Pattern

```typescript
// Next.js middleware for tenant resolution
export async function middleware(request: NextRequest) {
  const hostname = request.headers.get('host') || '';
  const subdomain = hostname.split('.')[0];
  
  // Skip for main app domain
  if (subdomain === 'app' || subdomain === 'www') {
    return NextResponse.next();
  }
  
  // Resolve tenant by subdomain
  const tenant = await resolveTenant(subdomain);
  
  if (!tenant) {
    return NextResponse.redirect(new URL('/not-found', request.url));
  }
  
  if (tenant.status !== 'active') {
    return NextResponse.redirect(new URL('/suspended', request.url));
  }
  
  // Set tenant context in headers
  const response = NextResponse.next();
  response.headers.set('x-tenant-id', tenant.id);
  response.headers.set('x-tenant-name', tenant.name);
  
  return response;
}
```

### Custom Domain Support

```typescript
interface CustomDomainConfig {
  tenantId: string;
  domain: string;
  verified: boolean;
  sslCertificate: {
    issued: boolean;
    expiresAt: string;
    autoRenew: boolean;
  };
  dnsRecords: Array<{
    type: 'CNAME' | 'A' | 'TXT';
    name: string;
    value: string;
    verified: boolean;
  }>;
}

async function setupCustomDomain(
  tenantId: string,
  domain: string
): Promise<CustomDomainConfig> {
  // 1. Validate domain not already in use
  await validateDomainAvailability(domain);
  
  // 2. Generate verification TXT record
  const verificationToken = generateVerificationToken();
  
  // 3. Configure hosting platform (Vercel/Cloudflare)
  await platform.addDomain(domain, {
    teamId: tenantId,
    redirectToHttps: true
  });
  
  // 4. Issue SSL certificate
  await platform.requestCertificate(domain);
  
  return {
    tenantId,
    domain,
    verified: false,
    dnsRecords: [
      {
        type: 'CNAME',
        name: domain,
        value: 'cname.vercel-dns.com',
        verified: false
      },
      {
        type: 'TXT',
        name: `_verification.${domain}`,
        value: verificationToken,
        verified: false
      }
    ]
  };
}
```

## Tenant Management API

### List Tenants

```typescript
GET /api/admin/tenants
Query params:
  - page: number
  - limit: number
  - status: 'active' | 'suspended' | 'trial'
  - sort: 'created_at' | 'name' | 'usage'

Response: {
  tenants: Array<{
    id: string;
    name: string;
    subdomain: string;
    plan: string;
    status: string;
    userCount: number;
    storageUsage: number;
    billingStatus: string;
    createdAt: string;
  }>;
  pagination: {
    total: number;
    page: number;
    pages: number;
  };
}
```

### Update Tenant

```typescript
PATCH /api/admin/tenants/:id

Body: {
  name?: string;
  plan?: 'starter' | 'professional' | 'enterprise';
  status?: 'active' | 'suspended';
  quotas?: {
    maxUsers: number;
    maxStorage: number;
    maxApiCalls: number;
  };
  features?: Record<string, boolean>;
}
```

### Suspend/Reactivate Tenant

```typescript
POST /api/admin/tenants/:id/suspend
Reason: 'billing' | 'abuse' | 'request'

POST /api/admin/tenants/:id/reactivate
```

## Feature Flags per Tenant

```typescript
interface TenantFeatureFlags {
  tenantId: string;
  flags: Record<string, {
    enabled: boolean;
    overrideReason?: string;
    enabledAt?: string;
  }>;
  defaults: Record<string, boolean>; // From plan
}

// Check feature access
async function hasFeature(
  tenantId: string,
  feature: string
): Promise<boolean> {
  const flags = await getTenantFeatureFlags(tenantId);
  
  // Check tenant-specific override
  if (flags.flags[feature] !== undefined) {
    return flags.flags[feature].enabled;
  }
  
  // Fall back to plan default
  return flags.defaults[feature] ?? false;
}

// Set feature flag for tenant
async function setTenantFeature(
  tenantId: string,
  feature: string,
  enabled: boolean,
  reason: string
) {
  await db.tenantFeatureFlag.upsert({
    where: {
      tenantId_feature: { tenantId, feature }
    },
    create: {
      tenantId,
      feature,
      enabled,
      overrideReason: reason,
      enabledAt: new Date()
    },
    update: {
      enabled,
      overrideReason: reason,
      enabledAt: enabled ? new Date() : undefined
    }
  });
  
  // Invalidate cache
  await cache.del(`tenant:${tenantId}:features`);
}
```

## Usage Tracking per Tenant

```typescript
interface TenantUsageMetrics {
  tenantId: string;
  period: {
    start: string;
    end: string;
  };
  metrics: {
    apiCalls: number;
    storageGB: number;
    activeUsers: number;
    emailsSent: number;
    computeHours: number;
  };
  quotas: {
    apiCalls: number;
    storageGB: number;
    activeUsers: number;
  };
  overages: {
    apiCalls?: number;
    storageGB?: number;
    activeUsers?: number;
  };
}

// Record usage event
async function recordUsage(
  tenantId: string,
  metric: string,
  amount: number = 1
) {
  await db.tenantUsage.upsert({
    where: {
      tenantId_metric_date: {
        tenantId,
        metric,
        date: new Date().toISOString().split('T')[0]
      }
    },
    create: {
      tenantId,
      metric,
      date: new Date(),
      amount
    },
    update: {
      amount: { increment: amount }
    }
  });
  
  // Check if over quota
  const usage = await getCurrentUsage(tenantId, metric);
  const quota = await getTenantQuota(tenantId, metric);
  
  if (usage > quota) {
    await notifyOverage(tenantId, metric, usage, quota);
  }
}
```

## Per-Tenant Branding

```typescript
interface TenantBranding {
  tenantId: string;
  theme: {
    primaryColor: string;
    secondaryColor: string;
    logo: {
      light: string;
      dark: string;
    };
    favicon: string;
  };
  customDomain?: string;
  emailTemplates?: {
    fromName: string;
    fromEmail: string;
    replyTo: string;
    headerHtml: string;
    footerHtml: string;
  };
  uiOverrides?: {
    hideProductBranding: boolean;
    customCss: string;
  };
}

// Apply branding to response
async function applyBranding(
  tenantId: string,
  html: string
): Promise<string> {
  const branding = await getTenantBranding(tenantId);
  
  return html
    .replace(/{{primary_color}}/g, branding.theme.primaryColor)
    .replace(/{{logo_url}}/g, branding.theme.logo.light)
    .replace(/{{company_name}}/g, branding.companyName);
}
```

## Data Isolation Testing

```typescript
// Security test: Ensure cross-tenant access is blocked
describe('Tenant Isolation', () => {
  it('prevents cross-tenant data access', async () => {
    const tenant1 = await createTestTenant();
    const tenant2 = await createTestTenant();
    
    const user1 = await createUser(tenant1.id, {
      email: 'user1@tenant1.com'
    });
    
    // Attempt to access tenant1 user from tenant2 context
    await withTenant(tenant2.id, async () => {
      const users = await db.user.findMany();
      expect(users).not.toContainEqual(
        expect.objectContaining({ id: user1.id })
      );
    });
  });
  
  it('blocks direct database queries bypassing RLS', async () => {
    const tenant1 = await createTestTenant();
    const tenant2 = await createTestTenant();
    
    await createUser(tenant1.id, { email: 'test@tenant1.com' });
    
    // Raw SQL without tenant context should fail
    await expect(
      db.$queryRaw`SELECT * FROM users WHERE email = 'test@tenant1.com'`
    ).rejects.toThrow('Tenant context required');
  });
});
```

## Migration Considerations

When migrating to multi-tenant:

```typescript
// Add tenant_id to existing tables
async function migrateToMultiTenant() {
  // 1. Add tenant_id column (nullable initially)
  await db.$executeRaw`
    ALTER TABLE users 
    ADD COLUMN tenant_id UUID NULL 
    REFERENCES tenants(id)
  `;
  
  // 2. Create default tenant for existing data
  const defaultTenant = await db.tenant.create({
    data: {
      name: 'Default Organization',
      subdomain: 'main'
    }
  });
  
  // 3. Assign all existing users to default tenant
  await db.$executeRaw`
    UPDATE users 
    SET tenant_id = ${defaultTenant.id}
    WHERE tenant_id IS NULL
  `;
  
  // 4. Make tenant_id non-nullable
  await db.$executeRaw`
    ALTER TABLE users 
    ALTER COLUMN tenant_id SET NOT NULL
  `;
  
  // 5. Enable RLS
  await db.$executeRaw`
    ALTER TABLE users ENABLE ROW LEVEL SECURITY
  `;
  
  await db.$executeRaw`
    CREATE POLICY tenant_isolation ON users
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID)
  `;
}
```
