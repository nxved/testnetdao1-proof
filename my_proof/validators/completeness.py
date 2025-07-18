import logging
from typing import Dict, Any, List


def calculate_completeness_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate completeness based on credit statement tiers (from GOAL.md)"""
    
    # Tier 1: Required fields (60% of completeness score)
    tier1_fields = [
        'statement_metadata.record_id',
        'statement_metadata.statement_date',
        'statement_metadata.statement_period.start_date',
        'statement_metadata.statement_period.end_date',
        'financial_summary.previous_balance',
        'financial_summary.closing_balance',
        'financial_summary.purchases',
        'financial_summary.payments_credits',
        'transactions'
    ]
    
    # Tier 2: Enhanced fields (25% of completeness score)
    tier2_fields = [
        'account_info.card_brand',
        'account_info.credit_limit',
        'financial_summary.fees_charged',
        'financial_summary.interest_charged',
        'financial_summary.available_credit'
    ]
    
    # Tier 3: ML features (15% of completeness score)
    tier3_fields = [
        'spending_patterns.total_transactions',
        'spending_patterns.average_transaction_amount',
        'risk_metrics.credit_utilization_ratio',
        'engineered_features.spending_trend',
        'engineered_features.merchant_diversity_score'
    ]
    
    tier1_score = calculate_tier_score(data, tier1_fields)
    tier2_score = calculate_tier_score(data, tier2_fields)
    tier3_score = calculate_tier_score(data, tier3_fields)
    
    overall_score = (0.60 * tier1_score + 0.25 * tier2_score + 0.15 * tier3_score)
    
    return {
        'completeness_score': overall_score,
        'tier1_score': tier1_score,
        'tier2_score': tier2_score,
        'tier3_score': tier3_score,
        'is_complete': overall_score >= 0.8,
        'missing_tier1': get_missing_fields(data, tier1_fields),
        'missing_tier2': get_missing_fields(data, tier2_fields),
        'missing_tier3': get_missing_fields(data, tier3_fields)
    }


def calculate_tier_score(data: Dict[str, Any], fields: List[str]) -> float:
    """Calculate score for a specific tier of fields"""
    
    if not fields:
        return 1.0
    
    present_count = 0
    for field_path in fields:
        if has_field(data, field_path):
            present_count += 1
    
    return present_count / len(fields)


def has_field(data: Dict[str, Any], field_path: str) -> bool:
    """Check if nested field exists and has value"""
    
    keys = field_path.split('.')
    current = data
    
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return False
        current = current[key]
    
    # Special handling for transactions (must be non-empty list)
    if field_path == 'transactions':
        return isinstance(current, list) and len(current) > 0
    
    return current is not None


def get_missing_fields(data: Dict[str, Any], fields: List[str]) -> List[str]:
    """Get list of missing fields"""
    
    missing = []
    for field_path in fields:
        if not has_field(data, field_path):
            missing.append(field_path)
    
    return missing