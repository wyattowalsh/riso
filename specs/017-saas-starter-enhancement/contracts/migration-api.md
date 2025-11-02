# Migration Tool API Contract

## Overview

The migration tool enables swapping technologies post-generation with automated code analysis, diff generation, and rollback capability.

## CLI Interface

```bash
# Basic migration
riso migrate --from=clerk --to=workos --category=auth

# Dry run (show changes without applying)
riso migrate --from=neon --to=planetscale --category=database --dry-run

# Interactive mode (confirm each change)
riso migrate --from=prisma --to=drizzle --category=orm --interactive

# Rollback last migration
riso migrate --rollback

# List available migrations
riso migrate --list-available
```

## Migration Phases

### 1. Analysis Phase

```typescript
interface MigrationAnalysis {
  sourceInfo: {
    category: string;
    technology: string;
    version: string;
    files: string[];
    dependencies: Record<string, string>;
  };
  targetInfo: {
    category: string;
    technology: string;
    version: string;
    requiredFiles: string[];
    requiredDependencies: Record<string, string>;
  };
  compatibility: {
    compatible: boolean;
    warnings: string[];
    blockingIssues: string[];
  };
}
```

### 2. Planning Phase

```typescript
interface MigrationPlan {
  id: string;
  timestamp: string;
  from: string;
  to: string;
  category: string;
  changes: {
    filesToAdd: Array<{
      path: string;
      content: string;
      reason: string;
    }>;
    filesToModify: Array<{
      path: string;
      diff: string;
      reason: string;
    }>;
    filesToDelete: Array<{
      path: string;
      reason: string;
    }>;
    dependenciesToAdd: Record<string, string>;
    dependenciesToRemove: string[];
    envVarsToAdd: Array<{
      key: string;
      description: string;
      required: boolean;
    }>;
    envVarsToRemove: string[];
  };
  databaseChanges?: {
    requiresMigration: boolean;
    migrationSteps: string[];
    dataLoss: boolean;
    estimatedDuration: string;
  };
  testUpdates: {
    affectedTests: string[];
    requiredChanges: string;
  };
  estimatedDuration: string;
  riskLevel: 'low' | 'medium' | 'high';
}
```

### 3. Execution Phase

```typescript
interface MigrationExecution {
  planId: string;
  status: 'pending' | 'in-progress' | 'completed' | 'failed' | 'rolled-back';
  steps: Array<{
    name: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    startTime?: string;
    endTime?: string;
    error?: string;
  }>;
  backupPath: string; // For rollback
  logs: string[];
}
```

### 4. Validation Phase

```typescript
interface MigrationValidation {
  executionId: string;
  checks: Array<{
    name: string;
    passed: boolean;
    message: string;
    severity: 'error' | 'warning' | 'info';
  }>;
  testsRun: {
    total: number;
    passed: number;
    failed: number;
    skipped: number;
  };
  overall: 'success' | 'warnings' | 'failure';
}
```

## Migration Strategies by Category

### Authentication Migration

**Clerk → WorkOS**
- Update auth client initialization
- Migrate session handling
- Update middleware
- Transform user metadata schema
- Migrate organization/team data
- Update protected route patterns
- Regenerate API route handlers

**Auth.js → Clerk**
- Replace NextAuth configuration
- Migrate provider configs to Clerk dashboard setup
- Update session management
- Transform callbacks to Clerk webhooks
- Migrate user database schema
- Update UI components

### Database Migration

**Neon → PlanetScale**
- Export schema via Prisma/Drizzle
- Transform PostgreSQL-specific features to MySQL equivalents
- Update connection string format
- Migrate stored procedures/functions
- Export data (pg_dump → MySQL import)
- Update connection pooling configuration
- Test query compatibility

**Supabase → Neon**
- Export PostgreSQL schema
- Migrate RLS policies to application-level logic (if not using Supabase Auth)
- Update connection strings
- Export data
- Remove Supabase-specific extensions
- Update realtime subscriptions to alternative

### ORM Migration

**Prisma → Drizzle**
- Convert Prisma schema to Drizzle schema
- Regenerate migration files in Drizzle format
- Update query syntax throughout codebase
- Replace Prisma Client calls with Drizzle queries
- Update type imports
- Regenerate database client

**Drizzle → Prisma**
- Convert Drizzle schema to Prisma schema
- Generate Prisma migrations from current DB state
- Update query patterns to Prisma syntax
- Replace db.select() patterns with prisma.findMany()
- Update relation handling
- Regenerate Prisma Client

### Storage Migration

**R2 → S3**
- Update SDK imports (AWS SDK v3)
- Transform bucket configuration
- Update CORS policies
- Migrate presigned URL generation
- Update CDN integration (CloudFront)
- Batch migrate existing files
- Update access patterns

### Email Migration

**Resend → Postmark**
- Replace email client
- Convert React Email templates to Postmark templates
- Update email sending logic
- Migrate template variables
- Update webhook handling
- Test template rendering

## Rollback Mechanism

```typescript
interface RollbackProcedure {
  migrationId: string;
  backupLocation: string;
  steps: Array<{
    action: 'restore-file' | 'restore-db' | 'restore-env' | 'restore-deps';
    target: string;
    status: 'pending' | 'completed' | 'failed';
  }>;
  safetyChecks: {
    backupVerified: boolean;
    noDataLoss: boolean;
    testsPassedBefore: boolean;
  };
}
```

## Custom Code Handling

### Three-Way Merge Strategy

When encountering modified template files:

```typescript
interface MergeConflict {
  file: string;
  baseVersion: string;  // Original template
  ourVersion: string;    // Current modified file
  theirVersion: string;  // New template version
  conflicts: Array<{
    lineStart: number;
    lineEnd: number;
    type: 'modification' | 'deletion' | 'insertion';
    resolution: 'manual' | 'auto';
  }>;
}
```

Strategy:
1. Detect if file was modified from template
2. If unmodified: safe to replace
3. If modified: generate three-way merge
4. Auto-resolve non-conflicting changes
5. Mark conflicts for manual review
6. Show diff with conflict markers

## Database Migration Specifics

### Schema Export/Import

```bash
# PostgreSQL export
pg_dump --schema-only --no-owner --no-acl $SOURCE_URL > schema.sql

# MySQL export (for PlanetScale)
mysqldump --no-data --skip-add-drop-table $SOURCE_URL > schema.sql

# Data export (chunked for large tables)
pg_dump --data-only --table=users --inserts $SOURCE_URL > data.sql
```

### Migration Validation

Pre-migration checks:
- Connection to source and target databases
- Sufficient disk space for backups
- Schema compatibility verification
- Foreign key constraint validation
- Index compatibility check

Post-migration checks:
- Row counts match
- Primary keys preserved
- Foreign key integrity maintained
- Indexes created successfully
- Application queries execute without errors

## Progress Reporting

```typescript
interface MigrationProgress {
  phase: 'analysis' | 'planning' | 'backup' | 'execution' | 'validation';
  percentage: number;
  currentStep: string;
  estimatedTimeRemaining: string;
  canCancel: boolean;
}
```

Live progress output:
```
🔍 Analyzing current stack...
✓ Detected Clerk authentication with 47 integration points
✓ Found 12 API routes using Clerk middleware
✓ Identified 3 UI components with Clerk hooks

📋 Generating migration plan...
✓ Will modify 15 files
✓ Will add 2 new dependencies
✓ Will update 8 environment variables
✓ Will regenerate 12 test files

💾 Creating backup...
✓ Backed up to .riso/backups/migration-2025-11-02-abc123/

⚡ Executing migration...
[████████████████░░░░] 80% - Updating middleware patterns...

✅ Migration complete! Run tests to verify.
```

## Error Handling

```typescript
interface MigrationError {
  code: string;
  message: string;
  phase: 'analysis' | 'planning' | 'execution' | 'validation';
  recoverable: boolean;
  suggestedAction: string;
  rollbackAvailable: boolean;
}
```

Common errors:
- `INCOMPATIBLE_TECHNOLOGIES`: Source and target not compatible
- `CUSTOM_CODE_CONFLICTS`: Manual merge required
- `DATABASE_SCHEMA_MISMATCH`: Schema incompatibility
- `MISSING_CREDENTIALS`: Target service credentials not configured
- `TEST_FAILURES`: Post-migration tests failed
- `BACKUP_FAILED`: Could not create backup

## Testing Integration

Auto-generated test updates:

```typescript
// Before (Clerk)
import { auth } from '@clerk/nextjs';

test('protected route requires auth', async () => {
  const { userId } = auth();
  expect(userId).toBeDefined();
});

// After (WorkOS) - automatically transformed
import { getAuth } from '@workos-inc/authkit-nextjs';

test('protected route requires auth', async () => {
  const { user } = await getAuth();
  expect(user?.id).toBeDefined();
});
```

## Configuration File Updates

Migration tool updates `copier-answers.yml`:

```yaml
# Before migration
saas_auth: clerk

# After migration - preserves metadata
saas_auth: workos
_migration_history:
  - from: clerk
    to: workos
    date: 2025-11-02T10:30:00Z
    migrationId: mig_abc123
    reason: "Enterprise SSO requirement"
```
