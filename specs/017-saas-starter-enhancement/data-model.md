# Data Model: SaaS Starter Comprehensive Enhancement

**Feature**: 017-saas-starter-enhancement  
**Date**: 2025-11-02  
**Phase**: Phase 1 - Design

## Overview

This document defines the data structures for the SaaS Starter enhancement, including configuration schemas, migration metadata, multi-tenant models, and production deployment configurations. All entities are technology-agnostic and represent what data the system needs, not how it's stored.

## Core Configuration Entities

### EnhancedSaaSConfiguration

Represents the complete user configuration for a SaaS application generation.

```yaml
EnhancedSaaSConfiguration:
  fields:
    - config_version: string # Semantic version (e.g., "2.0.0")
    - created_at: timestamp
    - updated_at: timestamp
    - project_metadata:
        - project_name: string
        - project_slug: string
        - description: string
        - repository_url: string (optional)
    
    # Original 14 categories (enhanced from 2 to 4 options)
    - runtime: RuntimeOption  # nextjs-16 | remix-2x
    - hosting: HostingOption # vercel | cloudflare
    - database: DatabaseOption # neon | supabase | planetscale | cockroachdb
    - orm: ORMOption # prisma | drizzle
    - auth: AuthOption # clerk | authjs | workos | supabase-auth
    - enterprise_bridge: EnterpriseBridgeOption # workos | none
    - billing: BillingOption # stripe | paddle
    - jobs: JobsOption # triggerdev | inngest
    - email: EmailOption # resend | postmark | sendgrid | ses
    - analytics: AnalyticsOption # posthog | amplitude
    - ai: AIOption # openai | anthropic | gemini | ollama
    - storage: StorageOption # r2 | supabase-storage | s3 | uploadthing
    - cicd: CICDOption # github-actions | cloudflare-ci
    
    # NEW: 7 additional categories
    - search: SearchOption (optional) # algolia | meilisearch | typesense | none
    - cache: CacheOption (optional) # redis | cloudflare-kv | vercel-kv | none
    - feature_flags: FeatureFlagsOption (optional) # launchdarkly | posthog-flags | growthbook | none
    - cms: CMSOption (optional) # contentful | sanity | payload | strapi | none
    - usage_metering: UsageMeteringOption (optional) # stripe-metering | moesif | amberflo | none
    - secrets_management: SecretsOption (optional) # infisical | doppler | aws-secrets | none
    - error_tracking: ErrorTrackingOption # sentry | rollbar | bugsnag
    
    # Architecture patterns
    - architecture_pattern: ArchitecturePattern # single-tenant | multi-tenant
    - multi_tenant_isolation: IsolationLevel (optional) # rls | schema-per-tenant | db-per-tenant
    
    # Production patterns
    - deployment_pattern: DeploymentPattern # single-region | multi-region | blue-green
    - compliance_requirements: list[ComplianceFramework] # soc2, hipaa, gdpr
    
    # Developer experience
    - enable_dev_dashboard: boolean
    - enable_offline_mode: boolean
    - enable_unified_logs: boolean
    
  relationships:
    - has_many compatibility_validations: CompatibilityValidation[]
    - has_one cost_estimate: CostEstimate
    - has_one architecture_diagram: ArchitectureDiagram
    
  validation_rules:
    - config_version must match supported versions (2.x.x)
    - At least one option must be selected for each category
    - Optional categories can be "none"
    - Multi-tenant options only valid when architecture_pattern = multi-tenant
    - Compliance requirements must be compatible with selected hosting/database
```

### TechnologyOption

Base entity for all technology selections.

```yaml
TechnologyOption:
  fields:
    - id: string # Unique identifier (e.g., "neon", "planetscale")
    - label: string # Human-readable name
    - category: string # Category this option belongs to
    - use_when: string # Guidance on when to use this option
    - pricing_tier: PricingTier # free | starter | growth | enterprise
    - integration_complexity: ComplexityLevel # simple | moderate | complex
    - documentation_url: string
    - sdk_versions: map[string, string] # Language -> version
    
  relationships:
    - belongs_to category: InfrastructureCategory
    - has_many incompatibilities: CompatibilityRule[]
    - has_one pricing_info: PricingInformation
```

### InfrastructureCategory

Represents one of the 21 infrastructure decision points.

```yaml
InfrastructureCategory:
  fields:
    - id: string # Unique identifier (e.g., "database", "search")
    - label: string # Human-readable name
    - description: string # What this category controls
    - is_required: boolean # Whether a selection must be made
    - display_order: integer # Order in UI
    - options_count: integer # Number of available options (3-4)
    
  relationships:
    - has_many options: TechnologyOption[]
    - has_many compatibility_rules: CompatibilityRule[]
    
  validation_rules:
    - options_count must be between 2 and 4
    - At least one option must be marked as default
    - Required categories must have a selection (not "none")
```

## Compatibility & Validation Entities

### CompatibilityRule

Defines relationships between technology selections.

```yaml
CompatibilityRule:
  fields:
    - id: string # Unique identifier
    - condition_type: ConditionType # requires | conflicts_with | warns_with
    - severity: SeverityLevel # error | warning | info
    - source_technology: string # Technology ID that triggers this rule
    - target_technologies: list[string] # Technologies affected
    - message: string # User-facing explanation
    - suggestions: list[string] # Alternative recommendations
    - documentation_url: string (optional)
    
  validation_rules:
    - severity=error rules must block generation
    - severity=warning rules allow user override
    - severity=info rules are informational only
    
  examples:
    - id: "cloudflare-workers-no-traditional-db"
      condition_type: conflicts_with
      severity: error
      source_technology: "cloudflare"
      target_technologies: ["neon", "planetscale"]
      message: "Cloudflare Workers cannot use traditional database connections due to connection limits"
      suggestions: ["Use Cloudflare D1", "Switch to Vercel hosting", "Use Supabase with REST API"]
    
    - id: "supabase-auth-requires-supabase-db"
      condition_type: requires
      severity: error
      source_technology: "supabase-auth"
      target_technologies: ["supabase"]
      message: "Supabase Auth requires Supabase database for user management"
      suggestions: ["Switch to Clerk/Auth.js", "Use Supabase database"]
```

### CompatibilityValidation

Result of validating a specific configuration.

```yaml
CompatibilityValidation:
  fields:
    - configuration_id: string
    - validated_at: timestamp
    - is_valid: boolean # Can this configuration be generated?
    - errors: list[ValidationError] # Blocking issues
    - warnings: list[ValidationWarning] # Non-blocking concerns
    - info_messages: list[ValidationInfo] # Helpful information
    - suggestions: list[string] # Recommendations for improvement
    
  relationships:
    - belongs_to configuration: EnhancedSaaSConfiguration
    - has_many triggered_rules: CompatibilityRule[]
```

## Cost Estimation Entities

### CostEstimate

Projected monthly costs for a configuration at various scales.

```yaml
CostEstimate:
  fields:
    - configuration_id: string
    - estimated_at: timestamp
    - estimates_by_scale:
        - scale_1k: ScaleCostBreakdown # 1,000 users
        - scale_10k: ScaleCostBreakdown # 10,000 users
        - scale_100k: ScaleCostBreakdown # 100,000 users
    - cost_optimization_suggestions: list[string]
    - total_estimated_range:
        - minimum: decimal # Best case (free tiers, low usage)
        - maximum: decimal # Worst case (high usage, paid tiers)
    
  relationships:
    - belongs_to configuration: EnhancedSaaSConfiguration
    - has_many service_costs: ServiceCostBreakdown[]
```

### ScaleCostBreakdown

Cost breakdown for a specific user scale.

```yaml
ScaleCostBreakdown:
  fields:
    - user_count: integer
    - estimated_monthly_cost: decimal
    - service_costs: map[string, ServiceCost] # service_id -> cost details
    - usage_assumptions:
        - requests_per_user_per_month: integer
        - storage_per_user_mb: integer
        - email_per_user_per_month: integer
        - ai_requests_per_user_per_month: integer
    - breakdown_percentages:
        - hosting: decimal # Percentage of total cost
        - database: decimal
        - auth: decimal
        - storage: decimal
        - other: decimal
```

### ServiceCost

Cost details for a specific service integration.

```yaml
ServiceCost:
  fields:
    - service_id: string
    - service_name: string
    - pricing_tier: string # free | paid | enterprise
    - base_cost: decimal # Fixed monthly cost
    - usage_cost: decimal # Variable cost based on usage
    - cost_factors:
        - api_calls: integer
        - storage_gb: decimal
        - bandwidth_gb: decimal
        - users: integer
    - is_within_free_tier: boolean
    - overage_estimate: decimal # Cost beyond free tier
```

## Migration Tool Entities

### MigrationPlan

Planned migration from one technology to another.

```yaml
MigrationPlan:
  fields:
    - id: string
    - created_at: timestamp
    - status: MigrationStatus # draft | ready | executing | completed | failed | rolled_back
    - source_configuration: EnhancedSaaSConfiguration
    - target_configuration: EnhancedSaaSConfiguration
    - migration_type: MigrationType # auth | database | storage | search | full_stack
    - affected_categories: list[string] # Which categories are changing
    - complexity_score: integer # 1-10 scale
    - estimated_duration: integer # Minutes
    - risk_level: RiskLevel # low | medium | high
    - backup_created: boolean
    - backup_location: string
    
  relationships:
    - has_many affected_files: FileChange[]
    - has_many database_migrations: DatabaseMigration[]
    - has_one rollback_plan: RollbackPlan
    - has_many validation_results: PostMigrationValidation[]
```

### FileChange

Represents a change to a source file during migration.

```yaml
FileChange:
  fields:
    - file_path: string # Relative to project root
    - change_type: ChangeType # modify | add | delete | rename
    - diff: string # Unified diff format
    - original_content: string (optional) # For rollback
    - new_content: string # For modify/add
    - conflict_detected: boolean
    - conflict_resolution: ConflictResolution (optional) # manual | auto | skip
    - applied: boolean
    - applied_at: timestamp (optional)
    
  relationships:
    - belongs_to migration_plan: MigrationPlan
    - has_many code_transformations: CodeTransformation[]
```

### DatabaseMigration

Database schema changes required for a migration.

```yaml
DatabaseMigration:
  fields:
    - id: string
    - migration_name: string
    - up_script: string # SQL or ORM migration code
    - down_script: string # Rollback SQL
    - estimated_duration: integer # Seconds
    - requires_downtime: boolean
    - data_migration_required: boolean
    - data_migration_script: string (optional)
    - executed: boolean
    - executed_at: timestamp (optional)
    - execution_result: string (optional) # Success message or error
    
  relationships:
    - belongs_to migration_plan: MigrationPlan
```

### RollbackPlan

Procedures for rolling back a failed migration.

```yaml
RollbackPlan:
  fields:
    - migration_plan_id: string
    - rollback_steps: list[RollbackStep]
    - estimated_duration: integer # Minutes
    - data_loss_possible: boolean
    - manual_steps_required: boolean
    - manual_instructions: string (optional)
    
  relationships:
    - belongs_to migration_plan: MigrationPlan
```

### RollbackStep

Individual step in a rollback procedure.

```yaml
RollbackStep:
  fields:
    - step_number: integer
    - description: string
    - action_type: ActionType # restore_file | restore_database | revert_config | manual
    - automated: boolean
    - command: string (optional) # Command to execute
    - verification: string # How to verify this step succeeded
```

## Multi-Tenant Entities

### TenantConfiguration

Settings for multi-tenant architecture.

```yaml
TenantConfiguration:
  fields:
    - isolation_level: IsolationLevel # rls | schema-per-tenant | db-per-tenant
    - subdomain_routing_enabled: boolean
    - tenant_provisioning_workflow: ProvisioningWorkflow # automatic | manual | approval_required
    - max_tenants: integer (optional) # Limit based on plan
    - tenant_customization_options:
        - custom_branding: boolean
        - custom_domain: boolean
        - custom_features: boolean
    - resource_limits_per_tenant:
        - max_users: integer
        - max_storage_gb: integer
        - max_api_calls_per_month: integer
    
  relationships:
    - has_many tenant_instances: Tenant[]
    - has_one billing_configuration: TenantBillingConfiguration
```

### Tenant

Represents an individual tenant/organization in a multi-tenant application.

```yaml
Tenant:
  fields:
    - id: string # UUID
    - name: string # Organization name
    - slug: string # URL-safe identifier
    - subdomain: string (optional) # Subdomain for routing
    - custom_domain: string (optional)
    - created_at: timestamp
    - status: TenantStatus # active | suspended | deleted
    - isolation_scope: string # Schema name or database identifier
    - feature_flags: map[string, boolean] # Per-tenant flag overrides
    - resource_usage:
        - user_count: integer
        - storage_used_gb: decimal
        - api_calls_this_month: integer
    - quotas:
        - max_users: integer
        - max_storage_gb: integer
        - max_api_calls_per_month: integer
    - branding:
        - primary_color: string
        - logo_url: string
        - custom_css_url: string (optional)
    
  relationships:
    - belongs_to configuration: TenantConfiguration
    - has_many users: TenantUser[]
    - has_one subscription: TenantSubscription
    - has_many usage_records: UsageRecord[]
```

### TenantBillingConfiguration

Billing settings for multi-tenant architecture.

```yaml
TenantBillingConfiguration:
  fields:
    - billing_model: BillingModel # per-tenant | aggregate | tiered
    - pricing_structure: PricingStructure # flat-rate | usage-based | hybrid
    - invoice_aggregation: AggregationLevel # per-tenant | per-organization | combined
    - quota_enforcement: QuotaEnforcement # block | throttle | allow_overage
    - overage_pricing:
        - additional_user_cost: decimal
        - additional_gb_cost: decimal
        - additional_api_call_cost: decimal
    
  relationships:
    - has_many tenant_subscriptions: TenantSubscription[]
```

## Production Deployment Entities

### DeploymentConfiguration

Production deployment settings.

```yaml
DeploymentConfiguration:
  fields:
    - deployment_pattern: DeploymentPattern # single-region | multi-region | blue-green
    - regions: list[Region] # Geographic regions for deployment
    - failover_strategy: FailoverStrategy # dns-based | load-balancer | manual
    - health_check_config:
        - endpoint: string
        - interval_seconds: integer
        - timeout_seconds: integer
        - healthy_threshold: integer
        - unhealthy_threshold: integer
    - blue_green_config (optional):
        - traffic_shift_strategy: TrafficShiftStrategy # immediate | gradual
        - gradual_shift_steps: list[integer] # [1, 10, 50, 100] percentages
        - rollback_triggers:
            - error_rate_threshold: decimal # 0.02 = 2%
            - latency_threshold_ms: integer
            - failed_health_checks: integer
    
  relationships:
    - has_many region_deployments: RegionDeployment[]
    - has_one backup_configuration: BackupConfiguration
    - has_one disaster_recovery_plan: DisasterRecoveryPlan
```

### RegionDeployment

Deployment in a specific geographic region.

```yaml
RegionDeployment:
  fields:
    - region_id: string # us-east-1, eu-west-1, etc.
    - is_primary: boolean
    - deployed_at: timestamp
    - application_url: string
    - database_endpoints:
        - primary: string
        - replicas: list[string]
    - cdn_endpoint: string
    - health_status: HealthStatus # healthy | degraded | unhealthy
    - latency_p95_ms: integer
    - error_rate: decimal
    
  relationships:
    - belongs_to deployment: DeploymentConfiguration
```

### ComplianceConfiguration

Compliance and regulatory settings.

```yaml
ComplianceConfiguration:
  fields:
    - frameworks: list[ComplianceFramework] # soc2, hipaa, gdpr
    - data_residency_requirements:
        - allowed_regions: list[string]
        - prohibited_regions: list[string]
    - encryption_requirements:
        - at_rest: boolean
        - in_transit: boolean
        - key_management: KeyManagement # platform-managed | customer-managed
    - audit_logging:
        - enabled: boolean
        - retention_days: integer
        - log_types: list[string] # access, data_changes, admin_actions
    - gdpr_specific (optional):
        - right_to_deletion_automated: boolean
        - consent_management_enabled: boolean
        - data_export_format: string # json | csv
    - hipaa_specific (optional):
        - baa_signed: boolean
        - phi_encryption: boolean
        - access_controls_enforced: boolean
    
  relationships:
    - has_many audit_logs: AuditLog[]
    - has_many compliance_reports: ComplianceReport[]
```

## Developer Tools Entities

### DevDashboardConfiguration

Settings for local development dashboard.

```yaml
DevDashboardConfiguration:
  fields:
    - enabled: boolean
    - port: integer # Dashboard port (default 3001)
    - auto_launch: boolean # Open browser on start
    - monitored_services: list[ServiceMonitor]
    - log_aggregation_config:
        - correlation_id_header: string
        - log_format: LogFormat # json | pretty
        - retention_hours: integer
    - quick_actions: list[QuickAction]
    
  relationships:
    - has_many service_health_checks: ServiceHealthCheck[]
```

### ServiceHealthCheck

Health monitoring for a local service.

```yaml
ServiceHealthCheck:
  fields:
    - service_id: string # database, cache, auth, etc.
    - service_name: string
    - health_endpoint: string
    - check_interval_seconds: integer
    - last_check_at: timestamp
    - status: HealthStatus # healthy | unhealthy | unknown
    - last_error: string (optional)
    - uptime_percentage: decimal
    
  validation_rules:
    - check_interval_seconds must be >= 5
    - health_endpoint must return 200 for healthy status
```

### OfflineModeConfiguration

Settings for offline development with service mocking.

```yaml
OfflineModeConfiguration:
  fields:
    - enabled: boolean
    - mock_services: list[string] # Which services to mock
    - mock_data_source: MockDataSource # canned | generated | recorded
    - ai_mock_behavior: AIMockBehavior # canned_responses | local_llm
    - local_llm_model: string (optional) # llama3-8b, mistral-7b
    - recorded_responses_path: string (optional)
    
  relationships:
    - has_many mock_responses: MockResponse[]
```

## Enumerations

```yaml
Enumerations:
  MigrationStatus:
    - draft # Migration plan created but not ready
    - ready # Plan validated, ready to execute
    - executing # Migration in progress
    - completed # Migration finished successfully
    - failed # Migration failed, rollback may be needed
    - rolled_back # Migration rolled back to original state
  
  IsolationLevel:
    - rls # Row-level security (PostgreSQL RLS)
    - schema-per-tenant # Separate schema per tenant
    - db-per-tenant # Separate database per tenant
  
  DeploymentPattern:
    - single-region # Deploy to one geographic region
    - multi-region # Deploy to multiple regions
    - blue-green # Zero-downtime deployment with environment switching
  
  ComplianceFramework:
    - soc2 # SOC 2 Type II compliance
    - hipaa # Health Insurance Portability and Accountability Act
    - gdpr # General Data Protection Regulation
  
  HealthStatus:
    - healthy # Service operational
    - degraded # Service operational but with issues
    - unhealthy # Service not operational
    - unknown # Status cannot be determined
  
  SeverityLevel:
    - error # Blocks generation, must be resolved
    - warning # Non-blocking, user can proceed with caution
    - info # Informational, no action needed
  
  RiskLevel:
    - low # Migration unlikely to cause issues
    - medium # Some risk, testing recommended
    - high # Significant risk, careful validation required
```

## Relationships Summary

- **EnhancedSaaSConfiguration** is the root entity
- **TechnologyOption** instances are selected for each **InfrastructureCategory**
- **CompatibilityRule** instances validate **TechnologyOption** combinations
- **CostEstimate** provides financial projections for a configuration
- **MigrationPlan** enables technology swaps post-generation
- **TenantConfiguration** defines multi-tenant architecture
- **DeploymentConfiguration** defines production patterns
- **ComplianceConfiguration** enforces regulatory requirements
- **DevDashboardConfiguration** enhances local development

All entities are implementation-agnostic and can be persisted in JSON, YAML, database, or any storage system.
