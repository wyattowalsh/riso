# Validation Rules Contract

**Feature**: 012-saas-starter  
**Date**: 2025-11-02  
**File**: `template/hooks/pre_gen_project.py`

## Overview

This document defines the validation rules, compatibility checks, and pre-generation logic for the SaaS Starter module. These rules ensure users don't select incompatible technology combinations and provide helpful guidance.

---

## Compatibility Matrix

### Error-Level Incompatibilities

These combinations BLOCK template generation:

```python
ERROR_INCOMPATIBILITIES = [
    {
        "combination": ["neon", "supabase-storage"],
        "message": (
            "Cannot use Neon database with Supabase Storage. "
            "Choose either:\n"
            "  1. Full Supabase (database + storage + auth)\n"
            "  2. Neon database + Cloudflare R2 storage"
        ),
        "fix_suggestions": [
            {"set": {"saas_database": "supabase", "saas_storage": "supabase-storage"}},
            {"set": {"saas_database": "neon", "saas_storage": "r2"}},
        ],
        "performance_impact": "None - both alternatives have similar performance characteristics",
        "cost_impact": "Supabase bundle: ~$25/mo base + usage; Neon + R2: ~$20/mo base + usage",
    },
    {
        "combination": ["cloudflare", "github-actions"],
        "when": {"saas_runtime": "remix-2"},
        "message": (
            "Remix on Cloudflare should use Cloudflare CI for optimal integration. "
            "GitHub Actions can work but requires manual Workers configuration."
        ),
        "severity": "error",
        "fix_suggestions": [
            {"set": {"saas_cicd": "cloudflare-ci"}},
        ],
        "performance_impact": "Cloudflare CI deploys directly to Workers with ~30s faster deployment time",
        "cost_impact": "Both free for small projects; GitHub Actions charges after 2000 min/mo, Cloudflare CI free unlimited",
    },
]
```

---

### Warning-Level Incompatibilities

These combinations ALLOW generation but show warnings:

```python
WARNING_INCOMPATIBILITIES = [
    {
        "combination": ["cloudflare", "prisma"],
        "message": (
            "⚠️  Prisma requires TCP connections, which Cloudflare Workers don't support.\n"
            "You'll need to use Prisma Data Proxy (adds latency and cost).\n"
            "Recommendation: Use Drizzle ORM for better edge compatibility."
        ),
        "documentation": "https://www.prisma.io/docs/data-platform/data-proxy",
        "alternative": {"saas_orm": "drizzle"},
        "performance_impact": "Data Proxy adds ~50-100ms latency per query; Drizzle native connection ~10ms",
        "cost_impact": "Prisma Data Proxy: $29/mo + $1.50 per 100k queries; Drizzle: no additional cost",
    },
    {
        "combination": ["vercel", "r2"],
        "message": (
            "⚠️  Cloudflare R2 works with Vercel but egress bandwidth charges apply.\n"
            "Consider Vercel Blob Storage for tighter integration and no egress fees."
        ),
        "cost_impact": "high",
        "alternative": None,  # No Vercel Blob in current options
        "performance_impact": "R2 cold start: ~200ms; Similar latency once warm",
        "cost_details": "R2 egress to Vercel: $0.09/GB after 10GB free; Vercel Blob: $0.15/GB included in plan",
    },
    {
        "combination": ["vercel", "cloudflare-ci"],
        "message": (
            "⚠️  Using Cloudflare CI with Vercel hosting is unusual.\n"
            "GitHub Actions integrates more naturally with Vercel deployments."
        ),
        "alternative": {"saas_cicd": "github-actions"},
        "performance_impact": "Both deploy in ~2-3 minutes; GitHub Actions has native Vercel CLI integration",
        "cost_impact": "Both free for small teams; GitHub Actions $0.008/min after quota, Cloudflare CI free unlimited",
    },
]
```

---

### Info-Level Notices

These combinations trigger informational messages:

```python
INFO_NOTICES = [
    {
        "combination": ["supabase", "clerk"],
        "message": (
            "ℹ️  You've selected both Supabase (includes auth) and Clerk.\n"
            "Supabase Auth will be disabled in favor of Clerk.\n"
            "You'll still use Supabase for database and storage."
        ),
        "action": "disable_supabase_auth",
    },
    {
        "combination": ["supabase", "r2"],
        "message": (
            "ℹ️  Using Supabase database with Cloudflare R2 storage.\n"
            "Consider Supabase Storage for unified platform and RLS policies."
        ),
        "alternative": {"saas_storage": "supabase-storage"},
    },
    {
        "combination": ["authjs", "workos"],
        "message": (
            "ℹ️  Using Auth.js with WorkOS.\n"
            "WorkOS handles enterprise SSO (Okta, Azure AD).\n"
            "Auth.js handles primary authentication (email, OAuth).\n"
            "This is a valid and common pattern."
        ),
    },
]
```

---

## Recommended Stacks

Pre-validated technology combinations for common use cases:

```python
RECOMMENDED_STACKS = {
    "vercel-starter": {
        "label": "Vercel Starter Stack",
        "description": "Best developer experience, fastest setup, Vercel ecosystem",
        "ideal_for": "Startups, MVPs, Next.js-first teams",
        "selections": {
            "saas_runtime": "nextjs-16",
            "saas_hosting": "vercel",
            "saas_database": "neon",
            "saas_orm": "prisma",
            "saas_auth": "clerk",
            "saas_enterprise_bridge": "none",
            "saas_billing": "stripe",
            "saas_jobs": "triggerdev",
            "saas_email": "resend",
            "saas_analytics": "posthog",
            "saas_ai": "openai",
            "saas_storage": "r2",
            "saas_cicd": "github-actions",
        },
        "estimated_cold_start": "300ms",
        "estimated_monthly_cost": "$200-500 (at 10k users)",
    },
    
    "edge-optimized": {
        "label": "Edge-Optimized Stack",
        "description": "Global edge deployment, low latency, cost-effective",
        "ideal_for": "Global SaaS, latency-sensitive apps, budget-conscious teams",
        "selections": {
            "saas_runtime": "remix-2",
            "saas_hosting": "cloudflare",
            "saas_database": "neon",
            "saas_orm": "drizzle",
            "saas_auth": "authjs",
            "saas_enterprise_bridge": "none",
            "saas_billing": "stripe",
            "saas_jobs": "inngest",
            "saas_email": "postmark",
            "saas_analytics": "posthog",
            "saas_ai": "anthropic",
            "saas_storage": "r2",
            "saas_cicd": "cloudflare-ci",
        },
        "estimated_cold_start": "50ms",
        "estimated_monthly_cost": "$100-300 (at 10k users)",
    },
    
    "all-in-one-platform": {
        "label": "All-in-One Platform Stack",
        "description": "Single vendor (Supabase + Vercel), simplified operations",
        "ideal_for": "Small teams, single-platform preference, moderate budget",
        "selections": {
            "saas_runtime": "nextjs-16",
            "saas_hosting": "vercel",
            "saas_database": "supabase",
            "saas_orm": "prisma",
            "saas_auth": "clerk",  # Overrides Supabase Auth for better DX
            "saas_enterprise_bridge": "none",
            "saas_billing": "stripe",
            "saas_jobs": "triggerdev",
            "saas_email": "resend",
            "saas_analytics": "posthog",
            "saas_ai": "openai",
            "saas_storage": "supabase-storage",
            "saas_cicd": "github-actions",
        },
        "estimated_cold_start": "250ms",
        "estimated_monthly_cost": "$150-400 (at 10k users)",
    },
    
    "enterprise-ready": {
        "label": "Enterprise-Ready Stack",
        "description": "SSO, SCIM, compliance-focused, mature services",
        "ideal_for": "B2B SaaS targeting enterprises, compliance requirements",
        "selections": {
            "saas_runtime": "nextjs-16",
            "saas_hosting": "vercel",
            "saas_database": "neon",
            "saas_orm": "prisma",
            "saas_auth": "clerk",
            "saas_enterprise_bridge": "workos",  # Key differentiator
            "saas_billing": "stripe",
            "saas_jobs": "inngest",
            "saas_email": "postmark",  # Better deliverability
            "saas_analytics": "amplitude",  # Enterprise analytics
            "saas_ai": "anthropic",  # Better safety/compliance
            "saas_storage": "r2",
            "saas_cicd": "github-actions",
        },
        "estimated_cold_start": "350ms",
        "estimated_monthly_cost": "$500-1500 (at 10k users)",
    },
}
```

---

## Validation Functions

### Check Compatibility

```python
def check_compatibility(selections: dict) -> list[ValidationIssue]:
    """
    Check all compatibility rules against user selections.
    
    Returns list of validation issues with severity levels.
    """
    issues = []
    
    # Check error-level incompatibilities
    for rule in ERROR_INCOMPATIBILITIES:
        if matches_combination(selections, rule):
            issues.append({
                "severity": "error",
                "message": rule["message"],
                "fix_suggestions": rule["fix_suggestions"],
            })
    
    # Check warning-level incompatibilities
    for rule in WARNING_INCOMPATIBILITIES:
        if matches_combination(selections, rule):
            issues.append({
                "severity": "warning",
                "message": rule["message"],
                "alternative": rule.get("alternative"),
                "documentation": rule.get("documentation"),
            })
    
    # Check info-level notices
    for rule in INFO_NOTICES:
        if matches_combination(selections, rule):
            issues.append({
                "severity": "info",
                "message": rule["message"],
            })
    
    return issues


def matches_combination(selections: dict, rule: dict) -> bool:
    """Check if user selections match a rule's combination."""
    combination = rule["combination"]
    selected_values = [selections.get(f"saas_{key}") for key in 
                       ["runtime", "hosting", "database", "orm", "auth", 
                        "enterprise_bridge", "billing", "jobs", "email", 
                        "analytics", "ai", "storage", "cicd"]]
    
    # Check if all items in combination are in selected values
    return all(item in selected_values for item in combination)
```

---

### Suggest Recommended Stack

```python
def suggest_recommended_stack(selections: dict) -> str | None:
    """
    Suggest a recommended stack if user's selections are close to one.
    
    Returns stack key if 80%+ match, None otherwise.
    """
    for stack_key, stack in RECOMMENDED_STACKS.items():
        matches = sum(
            1 for key, value in stack["selections"].items()
            if selections.get(key) == value
        )
        total = len(stack["selections"])
        
        if matches / total >= 0.8:
            return stack_key
    
    return None
```

---

### Performance Estimation

```python
def estimate_performance(selections: dict) -> dict:
    """
    Estimate performance characteristics based on stack choices.
    
    Returns estimated metrics for cold start, latency, cost.
    """
    # Base estimates
    estimates = {
        "cold_start_ms": 200,
        "request_latency_p95_ms": 100,
        "monthly_cost_usd": 100,
    }
    
    # Adjust based on selections
    if selections.get("saas_hosting") == "cloudflare":
        estimates["cold_start_ms"] -= 150  # Edge is faster
        estimates["monthly_cost_usd"] -= 50  # Lower egress
    
    if selections.get("saas_orm") == "drizzle":
        estimates["cold_start_ms"] -= 50  # Lighter runtime
    
    if selections.get("saas_database") == "neon":
        estimates["request_latency_p95_ms"] += 20  # Serverless overhead
    
    if selections.get("saas_observability_datadog"):
        estimates["monthly_cost_usd"] += 100  # APM costs
    
    return estimates
```

---

## Pre-Generation Hook

Implemented in `template/hooks/pre_gen_project.py`:

```python
#!/usr/bin/env python3
"""
Pre-generation hook for SaaS Starter module.

Validates technology selections, checks compatibility, suggests optimizations.
"""
import sys
from typing import Any

def main(copier_data: dict[str, Any]) -> None:
    """Execute pre-generation validation."""
    
    # Skip if module disabled
    if copier_data.get("saas_starter_module") != "enabled":
        return
    
    print("\n🔍 Validating SaaS Starter configuration...")
    
    # Check compatibility
    issues = check_compatibility(copier_data)
    
    # Report errors (blocking)
    errors = [i for i in issues if i["severity"] == "error"]
    if errors:
        print("\n❌ Configuration errors found:\n")
        for error in errors:
            print(f"  {error['message']}\n")
            if error.get("fix_suggestions"):
                print("  Suggested fixes:")
                for idx, fix in enumerate(error["fix_suggestions"], 1):
                    print(f"    {idx}. {fix}")
        sys.exit(1)
    
    # Report warnings (non-blocking)
    warnings = [i for i in issues if i["severity"] == "warning"]
    if warnings:
        print("\n⚠️  Configuration warnings:\n")
        for warning in warnings:
            print(f"  {warning['message']}")
            if warning.get("documentation"):
                print(f"    Learn more: {warning['documentation']}")
            print()
    
    # Report info notices
    infos = [i for i in issues if i["severity"] == "info"]
    if infos:
        print("\nℹ️  Configuration notes:\n")
        for info in infos:
            print(f"  {info['message']}\n")
    
    # Suggest optimized stack if close match
    suggested_stack = suggest_recommended_stack(copier_data)
    if suggested_stack:
        stack = RECOMMENDED_STACKS[suggested_stack]
        print(f"\n💡 Your selections are similar to our '{stack['label']}'")
        print(f"   {stack['description']}")
        print(f"   Ideal for: {stack['ideal_for']}")
        print()
    
    # Show performance estimates
    perf = estimate_performance(copier_data)
    print("\n📊 Estimated performance characteristics:")
    print(f"   Cold start: ~{perf['cold_start_ms']}ms")
    print(f"   Request latency (p95): ~{perf['request_latency_p95_ms']}ms")
    print(f"   Monthly cost (10k users): ~${perf['monthly_cost_usd']}")
    print()
    
    print("✅ Configuration validated successfully!\n")


if __name__ == "__main__":
    import json
    copier_data = json.loads(sys.stdin.read())
    main(copier_data)
```

---

## Post-Generation Hook

Implemented in `template/hooks/post_gen_project.py`:

```python
#!/usr/bin/env python3
"""
Post-generation hook for SaaS Starter module.

Records metadata, validates generated files, runs initial setup.
"""
import json
import subprocess
from pathlib import Path
from datetime import datetime

def main(copier_data: dict) -> None:
    """Execute post-generation setup."""
    
    # Skip if module disabled
    if copier_data.get("saas_starter_module") != "enabled":
        return
    
    print("\n🚀 Setting up SaaS Starter project...")
    
    # Record generation metadata
    metadata = {
        "generated_at": datetime.utcnow().isoformat(),
        "copier_version": copier_data.get("_copier_version"),
        "template_version": copier_data.get("_template_version"),
        "selections": {
            key: value
            for key, value in copier_data.items()
            if key.startswith("saas_")
        },
    }
    
    metadata_path = Path(".saas-starter") / "metadata.json"
    metadata_path.parent.mkdir(exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2))
    
    print("✓ Recorded generation metadata")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    subprocess.run(["pnpm", "install"], check=True)
    print("✓ Dependencies installed")
    
    # Run database setup if fixtures enabled
    if copier_data.get("saas_include_fixtures"):
        print("\n🗄️  Setting up database with fixtures...")
        subprocess.run(["pnpm", "db:push"], check=True)
        subprocess.run(["pnpm", "db:seed"], check=True)
        print("✓ Database initialized with seed data")
    
    # Generate types
    print("\n🔧 Generating TypeScript types...")
    subprocess.run(["pnpm", "generate"], check=True)
    print("✓ Types generated")
    
    # Run quality checks
    print("\n✨ Running quality checks...")
    subprocess.run(["pnpm", "lint"], check=True)
    subprocess.run(["pnpm", "typecheck"], check=True)
    print("✓ Quality checks passed")
    
    # Print next steps
    print("\n" + "=" * 60)
    print("🎉 SaaS Starter project generated successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Copy .env.example to .env and add your API keys")
    print("  2. Review saas-starter.config.ts for your technology selections")
    print("  3. Run 'pnpm dev' to start the development server")
    print("  4. Visit http://localhost:3000 to see your application")
    print("\nDocumentation:")
    print("  - README.md - Project overview and quickstart")
    print("  - docs/setup.md - Detailed setup instructions")
    print("  - docs/deployment.md - Deployment guide")
    print()


if __name__ == "__main__":
    import sys
    copier_data = json.loads(sys.stdin.read())
    main(copier_data)
```

---

## Environment Variable Validation

Generated file: `lib/env.ts`

```typescript
import { createEnv } from "@t3-oss/env-nextjs";
import { z } from "zod";

export const env = createEnv({
  server: {
    // Database
    DATABASE_URL: z.string().url(),
    
    // Auth (conditional based on selection)
    {% if saas_auth == "clerk" %}
    CLERK_SECRET_KEY: z.string().min(1),
    {% elif saas_auth == "authjs" %}
    NEXTAUTH_SECRET: z.string().min(32),
    NEXTAUTH_URL: z.string().url(),
    {% endif %}
    
    // Billing
    {% if saas_billing == "stripe" %}
    STRIPE_SECRET_KEY: z.string().startsWith("sk_"),
    STRIPE_WEBHOOK_SECRET: z.string().startsWith("whsec_"),
    {% elif saas_billing == "paddle" %}
    PADDLE_API_KEY: z.string().min(1),
    PADDLE_WEBHOOK_SECRET: z.string().min(1),
    {% endif %}
    
    // Observability
    {% if saas_observability_sentry %}
    SENTRY_DSN: z.string().url().optional(),
    {% endif %}
    {% if saas_observability_datadog %}
    DD_API_KEY: z.string().min(1).optional(),
    {% endif %}
    
    // Email
    {% if saas_email == "resend" %}
    RESEND_API_KEY: z.string().startsWith("re_"),
    {% elif saas_email == "postmark" %}
    POSTMARK_API_KEY: z.string().min(1),
    {% endif %}
    
    // Jobs
    {% if saas_jobs == "triggerdev" %}
    TRIGGER_API_KEY: z.string().min(1),
    {% elif saas_jobs == "inngest" %}
    INNGEST_SIGNING_KEY: z.string().min(1),
    INNGEST_EVENT_KEY: z.string().min(1),
    {% endif %}
    
    // AI
    {% if saas_ai == "openai" %}
    OPENAI_API_KEY: z.string().startsWith("sk-"),
    {% elif saas_ai == "anthropic" %}
    ANTHROPIC_API_KEY: z.string().startsWith("sk-ant-"),
    {% endif %}
  },
  
  client: {
    {% if saas_auth == "clerk" %}
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: z.string().min(1),
    {% endif %}
    
    {% if saas_analytics == "posthog" %}
    NEXT_PUBLIC_POSTHOG_KEY: z.string().min(1),
    NEXT_PUBLIC_POSTHOG_HOST: z.string().url(),
    {% elif saas_analytics == "amplitude" %}
    NEXT_PUBLIC_AMPLITUDE_API_KEY: z.string().min(1),
    {% endif %}
    
    {% if saas_observability_sentry %}
    NEXT_PUBLIC_SENTRY_DSN: z.string().url().optional(),
    {% endif %}
  },
  
  runtimeEnv: {
    DATABASE_URL: process.env.DATABASE_URL,
    // ... map all variables
  },
});
```

---

## Edge Deployment Constraints

### Cloudflare Workers Limitations

```python
EDGE_CONSTRAINTS = {
    "cloudflare_workers": {
        "bundle_size_limit": "1MB compressed",
        "cpu_time_limit": "10ms on free plan, 50ms on paid",
        "memory_limit": "128MB",
        "tcp_connections": False,  # No direct TCP, use HTTP/WebSocket only
        "prisma_requires": "Data Proxy (adds $29/mo + latency)",
        "cold_start": "~50ms globally distributed",
        "recommended_orms": ["drizzle", "kysely"],
        "database_compatibility": {
            "neon": "HTTP API only",
            "supabase": "RESTful PostgREST API",
        },
    },
    "vercel_edge": {
        "bundle_size_limit": "1MB for Edge Functions, 50MB for Serverless",
        "cpu_time_limit": "No hard limit, but billed by GB-seconds",
        "memory_limit": "1024MB Edge Runtime",
        "tcp_connections": True,  # Serverless Functions support TCP
        "prisma_compatible": True,
        "cold_start": "~200-300ms multi-region",
        "recommended_orms": ["prisma", "drizzle"],
    },
}
```

### ORM Compatibility Matrix

```python
ORM_EDGE_COMPATIBILITY = {
    "prisma": {
        "cloudflare_workers": "REQUIRES_DATA_PROXY",
        "vercel_edge": "NATIVE_SUPPORT",
        "tcp_required": True,
        "bundle_size": "~500KB",
        "cold_start_penalty": "+100ms",
    },
    "drizzle": {
        "cloudflare_workers": "NATIVE_SUPPORT",
        "vercel_edge": "NATIVE_SUPPORT",
        "tcp_required": False,  # Uses HTTP with Neon, Supabase
        "bundle_size": "~50KB",
        "cold_start_penalty": "+10ms",
    },
}
```

---

## Validation Determinism

### Ensuring Reproducible Validation

```python
def ensure_deterministic_validation():
    """
    Validation MUST be deterministic: same inputs → same results.
    
    Forbidden:
    - Random values in error messages
    - Timestamps in validation output
    - System-dependent paths
    - Network calls during validation
    - Non-deterministic ordering of error messages
    
    Required:
    - Stable sort order for validation issues (by severity, then alphabetically)
    - Reproducible error messages with fixed templates
    - Version-locked validation logic
    """
    pass


def validate_with_determinism(selections: dict) -> list[ValidationIssue]:
    """Validate selections with guaranteed determinism."""
    issues = check_compatibility(selections)
    
    # Sort deterministically: ERROR > WARNING > INFO, then alphabetically
    severity_order = {"error": 0, "warning": 1, "info": 2}
    issues.sort(key=lambda i: (severity_order[i["severity"]], i["message"]))
    
    return issues
```

---

## Conclusion

This validation contract ensures:

1. **Compatibility**: Prevents invalid technology combinations
2. **Guidance**: Suggests optimized stacks and alternatives
3. **Performance**: Estimates cold start, latency, and cost
4. **Safety**: Validates environment variables at build time
5. **Automation**: Hooks handle setup and validation automatically

Next: Create quickstart guide for developers using the generated SaaS application.
