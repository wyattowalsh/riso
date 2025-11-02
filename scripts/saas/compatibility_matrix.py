"""
Compatibility validation module for SaaS Starter enhancements.

This module validates technology combinations to ensure they are compatible
before generation. It implements a rule-based validation engine with error,
warning, and info severity levels.

Usage:
    from scripts.saas.compatibility_matrix import validate_compatibility
    
    selections = {
        'runtime': 'nextjs-16',
        'hosting': 'vercel',
        'database': 'neon',
        # ... other selections
    }
    
    result = validate_compatibility(selections)
    if not result['valid']:
        for error in result['errors']:
            print(f"ERROR: {error['message']}")
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Callable


@dataclass
class CompatibilityRule:
    """Represents a single compatibility rule."""
    
    id: str
    condition_type: str  # 'requires', 'conflicts_with', 'warns_with'
    severity: str  # 'error', 'warning', 'info'
    source_technology: str
    target_technologies: List[str]
    message: str
    suggestions: List[str]
    condition: Callable[[Dict[str, str]], bool] = None


# Define compatibility rules
COMPATIBILITY_RULES = [
    # Platform Incompatibilities
    CompatibilityRule(
        id="cloudflare-no-traditional-db",
        condition_type="conflicts_with",
        severity="error",
        source_technology="cloudflare",
        target_technologies=["neon", "planetscale", "cockroachdb"],
        message="Cloudflare Workers cannot use traditional database connections due to connection limits",
        suggestions=[
            "Use Cloudflare D1 database",
            "Switch to Vercel hosting",
            "Use Supabase with REST API mode"
        ]
    ),
    
    # Service Dependencies
    CompatibilityRule(
        id="supabase-auth-requires-db",
        condition_type="requires",
        severity="error",
        source_technology="supabase-auth",
        target_technologies=["supabase"],
        message="Supabase Auth requires Supabase database for user management",
        suggestions=[
            "Switch to Clerk or Auth.js for authentication",
            "Use Supabase database"
        ]
    ),
    
    CompatibilityRule(
        id="supabase-storage-recommends-db",
        condition_type="recommends",
        severity="warning",
        source_technology="supabase-storage",
        target_technologies=["supabase"],
        message="Supabase Storage works best with Supabase database for RLS policies",
        suggestions=[
            "Consider using Supabase database for tight integration",
            "Manually configure RLS policies if using different database"
        ]
    ),
    
    # Feature Conflicts
    CompatibilityRule(
        id="schema-per-tenant-requires-postgres",
        condition_type="requires",
        severity="error",
        source_technology="schema-per-tenant",
        target_technologies=["neon", "supabase", "cockroachdb"],
        message="Schema-per-tenant isolation requires PostgreSQL-compatible database",
        suggestions=[
            "Use row-level security (RLS) pattern instead",
            "Switch to PostgreSQL-compatible database (Neon, Supabase, CockroachDB)"
        ]
    ),
    
    CompatibilityRule(
        id="rls-requires-postgres",
        condition_type="requires",
        severity="error",
        source_technology="rls",
        target_technologies=["neon", "supabase", "cockroachdb"],
        message="Row-level security (RLS) requires PostgreSQL-compatible database",
        suggestions=[
            "Switch to PostgreSQL-compatible database (Neon, Supabase, CockroachDB)",
            "Use database-per-tenant pattern instead"
        ]
    ),
    
    # Performance Warnings
    CompatibilityRule(
        id="too-many-edge-services",
        condition_type="warns_with",
        severity="warning",
        source_technology="cloudflare",
        target_technologies=[],
        message="Using many integrations with edge deployment may increase cold start times",
        suggestions=[
            "Consider using Vercel or Railway for traditional deployment",
            "Use Cloudflare Workers for API only, host frontend separately"
        ],
        condition=lambda s: s.get('hosting') == 'cloudflare' and (
            s.get('search') != 'none' or
            s.get('cache') != 'none' or
            s.get('cms') != 'none'
        )
    ),
    
    # Cost Warnings
    CompatibilityRule(
        id="expensive-combination",
        condition_type="warns_with",
        severity="warning",
        source_technology="algolia",
        target_technologies=["launchdarkly"],
        message="Algolia + LaunchDarkly combination can be expensive at scale",
        suggestions=[
            "Consider Meilisearch (open-source) for search",
            "Consider PostHog or GrowthBook for feature flags"
        ]
    ),
    
    # ORM Compatibility
    CompatibilityRule(
        id="typeorm-mysql-planetscale",
        condition_type="recommends",
        severity="info",
        source_technology="typeorm",
        target_technologies=["planetscale"],
        message="TypeORM works well with PlanetScale MySQL",
        suggestions=[]
    ),
    
    # AI Provider Recommendations
    CompatibilityRule(
        id="ollama-local-only",
        condition_type="warns_with",
        severity="warning",
        source_technology="ollama",
        target_technologies=[],
        message="Ollama requires local GPU for reasonable performance. Not suitable for serverless.",
        suggestions=[
            "Use OpenAI, Anthropic, or Gemini for production",
            "Use Ollama only for development/testing"
        ]
    ),
    
    # Search Integration Recommendations
    CompatibilityRule(
        id="meilisearch-selfhosted",
        condition_type="warns_with",
        severity="info",
        source_technology="meilisearch",
        target_technologies=[],
        message="Meilisearch requires self-hosting or Meilisearch Cloud subscription",
        suggestions=[
            "Consider Algolia for fully managed solution",
            "Use Meilisearch Cloud for managed hosting"
        ]
    ),
]


def validate_compatibility(selections: Dict[str, str]) -> Dict[str, Any]:
    """
    Validate technology selections against compatibility rules.
    
    Args:
        selections: Dictionary of technology selections
            Example: {'runtime': 'nextjs-16', 'hosting': 'vercel', ...}
    
    Returns:
        Dictionary with validation results:
        {
            'valid': bool,  # True if no errors
            'errors': List[Dict],  # Blocking issues
            'warnings': List[Dict],  # Non-blocking concerns
            'info': List[Dict]  # Informational messages
        }
    """
    errors = []
    warnings = []
    info = []
    
    for rule in COMPATIBILITY_RULES:
        # Check if rule applies to current selections
        if rule.source_technology not in selections.values():
            continue
        
        # Evaluate custom condition if present
        if rule.condition:
            if not rule.condition(selections):
                continue
        
        # Check rule condition type
        if rule.condition_type == "conflicts_with":
            for target in rule.target_technologies:
                if target in selections.values():
                    item = {
                        'rule_id': rule.id,
                        'message': rule.message,
                        'suggestions': rule.suggestions
                    }
                    _add_to_severity_list(rule.severity, item, errors, warnings, info)
        
        elif rule.condition_type == "requires":
            # Check if any of the target technologies are present
            has_required = any(target in selections.values() 
                             for target in rule.target_technologies)
            if not has_required:
                item = {
                    'rule_id': rule.id,
                    'message': rule.message,
                    'suggestions': rule.suggestions
                }
                _add_to_severity_list(rule.severity, item, errors, warnings, info)
        
        elif rule.condition_type in ["recommends", "warns_with"]:
            # These always trigger if source technology is present
            if not rule.target_technologies or any(
                target in selections.values() 
                for target in rule.target_technologies
            ):
                item = {
                    'rule_id': rule.id,
                    'message': rule.message,
                    'suggestions': rule.suggestions
                }
                _add_to_severity_list(rule.severity, item, errors, warnings, info)
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'info': info
    }


def _add_to_severity_list(severity: str, item: Dict, errors: List, warnings: List, info: List):
    """Helper to add item to appropriate severity list."""
    if severity == 'error':
        errors.append(item)
    elif severity == 'warning':
        warnings.append(item)
    else:
        info.append(item)


def get_rule_count() -> int:
    """Return the total number of compatibility rules."""
    return len(COMPATIBILITY_RULES)


def get_rules_by_severity(severity: str) -> List[CompatibilityRule]:
    """Get all rules of a specific severity level."""
    return [rule for rule in COMPATIBILITY_RULES if rule.severity == severity]


if __name__ == "__main__":
    # Example usage
    import sys
    import json
    
    if len(sys.argv) > 1:
        # Accept selections as JSON argument
        selections = json.loads(sys.argv[1])
    else:
        # Test with default selections
        selections = {
            'runtime': 'nextjs-16',
            'hosting': 'cloudflare',
            'database': 'neon',
            'orm': 'prisma',
            'auth': 'clerk',
            'search': 'none',
            'cache': 'none'
        }
    
    result = validate_compatibility(selections)
    print(json.dumps(result, indent=2))
