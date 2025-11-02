"""
Cost estimation calculator for SaaS Starter configurations.

Estimates monthly costs for different technology combinations at various scales.
Pricing data is approximate and should be validated against current provider pricing.

Usage:
    from scripts.saas.cost_calculator import estimate_costs
    
    selections = {
        'runtime': 'nextjs-16',
        'hosting': 'vercel',
        'database': 'neon',
        'auth': 'clerk',
        # ... other selections
    }
    
    estimates = estimate_costs(selections)
    print(f"1K users: ${estimates['scale_1k']['total']}/month")
"""

from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class ServicePricing:
    """Pricing information for a service."""
    service_id: str
    service_name: str
    free_tier: Dict[str, Any]  # Limits and features
    paid_tiers: List[Dict[str, Any]]  # Pricing tiers
    usage_based: bool  # Whether pricing is usage-based
    base_cost: float  # Fixed monthly cost (if any)


# Pricing database (simplified - actual pricing may vary)
SERVICE_PRICING = {
    # Hosting
    'vercel': ServicePricing(
        service_id='vercel',
        service_name='Vercel',
        free_tier={'bandwidth_gb': 100, 'builds_hours': 6, 'cost': 0},
        paid_tiers=[
            {'name': 'Pro', 'cost': 20, 'bandwidth_gb': 1000, 'builds_hours': 24},
            {'name': 'Enterprise', 'cost': 'custom'}
        ],
        usage_based=True,
        base_cost=0
    ),
    'cloudflare': ServicePricing(
        service_id='cloudflare',
        service_name='Cloudflare Pages',
        free_tier={'requests': 100000, 'cost': 0},
        paid_tiers=[{'name': 'Pay-as-you-go', 'cost_per_million': 0.50}],
        usage_based=True,
        base_cost=0
    ),
    'netlify': ServicePricing(
        service_id='netlify',
        service_name='Netlify',
        free_tier={'bandwidth_gb': 100, 'builds_minutes': 300, 'cost': 0},
        paid_tiers=[{'name': 'Pro', 'cost': 19}],
        usage_based=False,
        base_cost=0
    ),
    'railway': ServicePricing(
        service_id='railway',
        service_name='Railway',
        free_tier={'hours': 500, 'cost': 0},
        paid_tiers=[{'name': 'Pay-as-you-go', 'cost_per_hour': 0.000231}],
        usage_based=True,
        base_cost=0
    ),
    
    # Database
    'neon': ServicePricing(
        service_id='neon',
        service_name='Neon',
        free_tier={'storage_gb': 0.5, 'active_time_hours': 191, 'cost': 0},
        paid_tiers=[
            {'name': 'Launch', 'cost': 19, 'storage_gb': 10},
            {'name': 'Scale', 'cost': 69, 'storage_gb': 50}
        ],
        usage_based=False,
        base_cost=0
    ),
    'supabase': ServicePricing(
        service_id='supabase',
        service_name='Supabase',
        free_tier={'storage_gb': 0.5, 'bandwidth_gb': 2, 'cost': 0},
        paid_tiers=[{'name': 'Pro', 'cost': 25}],
        usage_based=False,
        base_cost=0
    ),
    'planetscale': ServicePricing(
        service_id='planetscale',
        service_name='PlanetScale',
        free_tier={'storage_gb': 5, 'row_reads': 1000000000, 'cost': 0},
        paid_tiers=[{'name': 'Scaler Pro', 'cost': 39}],
        usage_based=False,
        base_cost=0
    ),
    'cockroachdb': ServicePricing(
        service_id='cockroachdb',
        service_name='CockroachDB',
        free_tier={'storage_gb': 5, 'request_units': 50000000, 'cost': 0},
        paid_tiers=[{'name': 'Serverless', 'cost_per_million_rus': 1}],
        usage_based=True,
        base_cost=0
    ),
    
    # Authentication
    'clerk': ServicePricing(
        service_id='clerk',
        service_name='Clerk',
        free_tier={'mau': 10000, 'cost': 0},
        paid_tiers=[{'name': 'Pro', 'cost': 25, 'cost_per_1k_mau': 0.02}],
        usage_based=True,
        base_cost=0
    ),
    'authjs': ServicePricing(
        service_id='authjs',
        service_name='Auth.js',
        free_tier={'cost': 0},  # Open source
        paid_tiers=[],
        usage_based=False,
        base_cost=0
    ),
    'workos': ServicePricing(
        service_id='workos',
        service_name='WorkOS',
        free_tier={'mau': 1000000, 'cost': 0},
        paid_tiers=[{'name': 'SSO', 'cost_per_connection': 125}],
        usage_based=True,
        base_cost=0
    ),
    'supabase-auth': ServicePricing(
        service_id='supabase-auth',
        service_name='Supabase Auth',
        free_tier={'cost': 0},  # Included with Supabase
        paid_tiers=[],
        usage_based=False,
        base_cost=0
    ),
    
    # Search
    'algolia': ServicePricing(
        service_id='algolia',
        service_name='Algolia',
        free_tier={'searches': 10000, 'records': 10000, 'cost': 0},
        paid_tiers=[{'name': 'Build', 'cost': 1, 'cost_per_100k_searches': 1.5}],
        usage_based=True,
        base_cost=0
    ),
    'meilisearch': ServicePricing(
        service_id='meilisearch',
        service_name='Meilisearch Cloud',
        free_tier={'cost': 0},  # Open source / self-hosted
        paid_tiers=[{'name': 'Cloud', 'cost': 30}],
        usage_based=False,
        base_cost=0
    ),
    'typesense': ServicePricing(
        service_id='typesense',
        service_name='Typesense Cloud',
        free_tier={'cost': 0},  # Open source / self-hosted
        paid_tiers=[{'name': 'Cloud', 'cost': 50}],
        usage_based=False,
        base_cost=0
    ),
    
    # Billing
    'stripe': ServicePricing(
        service_id='stripe',
        service_name='Stripe',
        free_tier={'cost': 0},
        paid_tiers=[],
        usage_based=True,  # 2.9% + $0.30 per transaction
        base_cost=0
    ),
}


def estimate_costs(
    selections: Dict[str, str],
    user_scales: List[int] = [1000, 10000, 100000]
) -> Dict[str, Any]:
    """
    Estimate monthly costs for the given technology selections at various scales.
    
    Args:
        selections: Dictionary of technology selections
        user_scales: List of user counts to estimate for (default: 1K, 10K, 100K)
    
    Returns:
        Dictionary with cost estimates per scale
    """
    estimates = {}
    
    for scale in user_scales:
        scale_key = f"scale_{scale // 1000}k"
        estimates[scale_key] = _estimate_for_scale(selections, scale)
    
    return estimates


def _estimate_for_scale(selections: Dict[str, str], user_count: int) -> Dict[str, Any]:
    """Estimate costs for a specific user scale."""
    total_cost = 0.0
    service_costs = {}
    assumptions = {
        'requests_per_user_per_month': 1000,
        'storage_per_user_mb': 100,
        'emails_per_user_per_month': 10,
        'ai_requests_per_user_per_month': 50,
        'searches_per_user_per_month': 100
    }
    
    # Calculate costs for each selected service
    for category, service in selections.items():
        if service == 'none' or service not in SERVICE_PRICING:
            continue
        
        pricing = SERVICE_PRICING[service]
        cost = _calculate_service_cost(pricing, user_count, assumptions)
        
        service_costs[service] = {
            'service_name': pricing.service_name,
            'cost': cost,
            'within_free_tier': cost == 0
        }
        
        total_cost += cost
    
    # Calculate percentages
    breakdown_percentages = {}
    if total_cost > 0:
        for service, data in service_costs.items():
            percentage = (data['cost'] / total_cost) * 100
            breakdown_percentages[service] = round(percentage, 1)
    
    return {
        'user_count': user_count,
        'total_monthly_cost': round(total_cost, 2),
        'service_costs': service_costs,
        'breakdown_percentages': breakdown_percentages,
        'assumptions': assumptions
    }


def _calculate_service_cost(
    pricing: ServicePricing,
    user_count: int,
    assumptions: Dict[str, int]
) -> float:
    """Calculate cost for a specific service."""
    # For free open-source services
    if not pricing.paid_tiers and pricing.base_cost == 0:
        return 0.0
    
    # Simple estimation logic (would be more sophisticated in production)
    if pricing.service_id == 'clerk':
        if user_count <= 10000:
            return 0.0
        else:
            overage = user_count - 10000
            return 25 + (overage / 1000 * 0.02)
    
    elif pricing.service_id == 'algolia':
        searches_per_month = user_count * assumptions['searches_per_user_per_month']
        if searches_per_month <= 10000:
            return 0.0
        else:
            return 1 + ((searches_per_month - 10000) / 100000 * 1.5)
    
    elif pricing.service_id in ['neon', 'supabase', 'planetscale']:
        # Estimate based on user count
        if user_count < 1000:
            return 0.0
        elif user_count < 10000:
            return pricing.paid_tiers[0]['cost'] if pricing.paid_tiers else 0
        else:
            return pricing.paid_tiers[-1]['cost'] if pricing.paid_tiers else 0
    
    elif pricing.service_id == 'vercel':
        # Vercel Pro starts at 20
        if user_count < 1000:
            return 0.0
        else:
            return 20.0
    
    # Default: return base cost for paid services
    return pricing.base_cost


def generate_cost_report(selections: Dict[str, str]) -> str:
    """Generate a human-readable cost report."""
    estimates = estimate_costs(selections)
    
    lines = ["# Cost Estimation Report\n"]
    lines.append("Based on selected technology stack:\n")
    
    for category, service in selections.items():
        if service != 'none':
            lines.append(f"- {category}: {service}")
    
    lines.append("\n## Estimated Monthly Costs\n")
    
    for scale_key, data in estimates.items():
        user_count = data['user_count']
        total = data['total_monthly_cost']
        lines.append(f"\n### {user_count:,} Users: ${total:.2f}/month\n")
        
        if data['service_costs']:
            lines.append("Breakdown:")
            for service, cost_data in data['service_costs'].items():
                service_name = cost_data['service_name']
                cost = cost_data['cost']
                percentage = data['breakdown_percentages'].get(service, 0)
                status = "(free tier)" if cost_data['within_free_tier'] else ""
                lines.append(f"- {service_name}: ${cost:.2f}/month ({percentage}%) {status}")
    
    lines.append("\n## Assumptions\n")
    for key, value in estimates['scale_1k']['assumptions'].items():
        lines.append(f"- {key.replace('_', ' ').title()}: {value}")
    
    lines.append("\n**Note**: These are estimates based on typical usage patterns.")
    lines.append("Actual costs may vary. Always verify with official pricing pages.\n")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Example usage
    import sys
    import json
    
    if len(sys.argv) > 1:
        selections = json.loads(sys.argv[1])
    else:
        selections = {
            'runtime': 'nextjs-16',
            'hosting': 'vercel',
            'database': 'neon',
            'auth': 'clerk',
            'search': 'algolia',
            'cache': 'none',
            'billing': 'stripe'
        }
    
    if '--json' in sys.argv:
        estimates = estimate_costs(selections)
        print(json.dumps(estimates, indent=2))
    else:
        report = generate_cost_report(selections)
        print(report)
