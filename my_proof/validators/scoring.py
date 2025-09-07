import logging
from typing import Dict, Any
from datetime import datetime

from ..country_config import country_scoring


def calculate_credit_statement_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """Our sophisticated scoring converted to Vana format with country-based fair rewards"""
    
    # Extract country information for fair scoring
    country_code = data.get('statement_metadata', {}).get('country_code', 'US')
    country_info = country_scoring.get_country_info(country_code)
    
    logging.info(f"Processing statement from {country_info['country_name']} (Tier {country_info['tier']})")
    
    # Transaction-Heavy Quality Scoring (100-point system)
    transaction_volume = calculate_transaction_volume_score(data)
    transaction_diversity = calculate_transaction_diversity_score(data)
    transaction_detail = calculate_transaction_detail_score(data)
    
    core_statement = calculate_core_statement_score(data)
    account_completeness = calculate_account_completeness_score(data)
    financial_consistency = calculate_financial_consistency_score(data)
    
    # Total score (0-100 points) before country adjustment
    base_total_points = (transaction_volume + transaction_diversity + transaction_detail + 
                        core_statement + account_completeness + financial_consistency)
    
    country_adjusted = country_scoring.calculate_country_adjusted_score(base_total_points, country_code)
    
    # Use country-adjusted values for final response
    total_points = country_adjusted['final_score']
    vana_score = country_adjusted['vana_score']
    quality = vana_score  # Use comprehensive score as quality
    
    return {
        'score': vana_score,
        'total_points': total_points,
        'quality': quality,
        'valid': True,
        'country_info': country_adjusted['country_info'],
        'breakdown': {
            'transaction_volume': transaction_volume,
            'transaction_diversity': transaction_diversity,
            'transaction_detail': transaction_detail,
            'transaction_total': transaction_volume + transaction_diversity + transaction_detail,
            'core_statement': core_statement,
            'account_completeness': account_completeness,
            'financial_consistency': financial_consistency,
            'supporting_total': core_statement + account_completeness + financial_consistency,
            'raw_total': base_total_points,
            'country_multiplier': country_adjusted['country_multiplier'],
            'scarcity_bonus': country_adjusted['scarcity_bonus'],
            'country_adjusted_total': country_adjusted['adjusted_total']
        }
    }


def calculate_transaction_volume_score(data: Dict[str, Any]) -> float:
    """Transaction volume scoring based on user's actual transaction count"""
    
    transactions = data.get('transactions', [])
    count = len(transactions)
    
    if count >= 50:
        return 25
    elif count >= 30:
        return 22
    elif count >= 20:
        return 18
    elif count >= 10:
        return 12
    elif count >= 5:
        return 6
    elif count >= 1:
        return 2
    else:
        return 0


def calculate_transaction_diversity_score(data: Dict[str, Any]) -> float:
    """Transaction diversity based on unique merchants and spending patterns"""
    
    transactions = data.get('transactions', [])
    if not transactions:
        return 0
    
    # Extract unique merchants from raw descriptions (not AI-enhanced merchant names)
    unique_merchants = extract_unique_merchants_from_descriptions(transactions)
    diversity_ratio = unique_merchants / len(transactions)
    
    # Amount variety (shows real spending patterns)
    amounts = [abs(float(t.get('amount', 0))) for t in transactions]
    unique_amounts = len(set(round(amt, 2) for amt in amounts))
    amount_variety_score = min(unique_amounts / 10, 1.0)  # Normalize to 0-1
    
    # Date spread (shows consistent usage over time)
    try:
        from datetime import datetime
        dates = [datetime.fromisoformat(t.get('date', '').replace('Z', '+00:00')) for t in transactions if t.get('date')]
        if len(dates) > 1:
            date_range_days = (max(dates) - min(dates)).days
            date_consistency_score = min(date_range_days / 30, 1.0)  # Normalize to 0-1
        else:
            date_consistency_score = 0
    except (ValueError, TypeError):
        date_consistency_score = 0
    
    # Combined diversity score (20 points max)
    diversity_score = (
        (diversity_ratio * 8) +           # Merchant variety (8 pts)
        (amount_variety_score * 7) +      # Amount variety (7 pts)
        (date_consistency_score * 5)      # Time consistency (5 pts)
    )
    
    return min(20, diversity_score)


def calculate_transaction_detail_score(data: Dict[str, Any]) -> float:
    """Transaction detail quality based on raw bank descriptions (15 points)"""
    
    transactions = data.get('transactions', [])
    if not transactions:
        return 0
    
    # Rich description quality (what bank actually provided) - 10 points
    detailed_txns = sum(1 for t in transactions 
                       if len(t.get('description', '')) > 20)
    description_score = (detailed_txns / len(transactions)) * 10
    
    # Realistic amount distribution - 5 points
    amounts = [abs(float(t.get('amount', 0))) for t in transactions]
    realistic_amounts = sum(1 for amt in amounts if 1 <= amt <= 5000)
    realism_score = (realistic_amounts / len(transactions)) * 5
    
    return description_score + realism_score


def calculate_core_statement_score(data: Dict[str, Any]) -> float:
    """Simplified core statement scoring - processor ensures data quality (25 points)"""
    
    # Since credit-statement-processor already validates completeness and authenticity,
    # we can give near-full points for processed data reaching this stage
    
    # Basic existence checks for core fields (20 points)
    statement_metadata = data.get('statement_metadata', {})
    account_info = data.get('account_info', {})
    
    score = 0
    if statement_metadata.get('statement_date'):
        score += 5
    if account_info.get('account_number_masked'):
        score += 5  
    if account_info.get('credit_limit'):
        score += 5
    if len(data.get('transactions', [])) > 0:
        score += 5
    
    # Statement period and balance info (5 points)
    if statement_metadata.get('statement_period_start') and statement_metadata.get('statement_period_end'):
        score += 3
    if account_info.get('current_balance') is not None:
        score += 2
        
    return min(score, 25)


def calculate_account_completeness_score(data: Dict[str, Any]) -> float:
    """Simplified account completeness - processor ensures quality (10 points)"""
    
    # Since processor ensures data completeness, give points for basic account fields
    account_info = data.get('account_info', {})
    
    score = 0
    if account_info.get('card_brand'):
        score += 3
    if account_info.get('card_type'):
        score += 2
    if account_info.get('credit_limit'):
        score += 3
    if account_info.get('available_credit'):
        score += 2
        
    return min(score, 10)


def calculate_financial_consistency_score(data: Dict[str, Any]) -> float:
    """Simplified financial consistency - processor validates integrity (5 points)"""
    
    # Since credit-statement-processor already validates financial integrity,
    # give full points if basic balance info is present
    account_info = data.get('account_info', {})
    
    if (account_info.get('current_balance') is not None and 
        account_info.get('credit_limit') is not None):
        return 5
    elif account_info.get('current_balance') is not None:
        return 3
    else:
        return 1


def extract_unique_merchants_from_descriptions(transactions: list) -> int:
    """Extract unique merchants from raw bank descriptions (not AI-enhanced)"""
    
    unique_merchants = set()
    
    for transaction in transactions:
        raw_description = transaction.get('description', '').upper()
        
        # Clean up common bank prefixes/suffixes
        cleaned = clean_bank_description(raw_description)
        
        # Extract merchant identifier
        merchant_key = extract_merchant_key(cleaned)
        
        if merchant_key and len(merchant_key) >= 3:
            unique_merchants.add(merchant_key)
    
    return len(unique_merchants)


def clean_bank_description(description: str) -> str:
    """Remove common bank formatting from transaction descriptions"""
    import re
    
    # Remove common prefixes
    prefixes_to_remove = [
        'DEBIT CARD PURCHASE ',
        'ONLINE PAYMENT ',
        'RECURRING PAYMENT ',
        'ATM WITHDRAWAL ',
        'CHECK CARD PURCHASE '
    ]
    
    cleaned = description
    for prefix in prefixes_to_remove:
        cleaned = cleaned.replace(prefix, '')
    
    # Remove transaction IDs and reference numbers
    cleaned = re.sub(r'\*\w+\d+', '', cleaned)  # Remove *1X3456789
    cleaned = re.sub(r'\d{6,}', '', cleaned)    # Remove long numbers
    
    return cleaned.strip()


def extract_merchant_key(cleaned_description: str) -> str:
    """Extract merchant identifier from cleaned description"""
    
    if len(cleaned_description) < 3:
        return None
        
    # Take first meaningful part (usually merchant name)
    words = cleaned_description.split()
    if not words:
        return None
        
    # Use first 1-2 words as merchant key
    if len(words) == 1:
        return words[0][:15]  # First word, max 15 chars
    else:
        return f"{words[0]} {words[1]}"[:15]  # First two words, max 15 chars


def validate_spending_patterns(data: Dict[str, Any]) -> float:
    """Validate computed spending pattern accuracy"""
    
    patterns = data.get('spending_patterns', {})
    transactions = data.get('transactions', [])
    
    if not patterns or not transactions:
        return 0
    
    score = 0
    
    # Check total_transactions accuracy
    reported_count = patterns.get('total_transactions', 0)
    actual_count = len(transactions)
    if reported_count == actual_count:
        score += 0.25
    
    # Check average_transaction_amount accuracy
    if transactions:
        reported_avg = float(patterns.get('average_transaction_amount', 0))
        actual_avg = sum(float(t.get('amount', 0)) for t in transactions) / len(transactions)
        if abs(reported_avg - actual_avg) / max(abs(actual_avg), 0.01) < 0.01:
            score += 0.25
    
    # Check category distribution exists
    if patterns.get('category_distribution'):
        score += 0.25
    
    # Check temporal patterns exist
    if patterns.get('weekend_spending_ratio') is not None:
        score += 0.25
    
    return score


def validate_risk_metrics(data: Dict[str, Any]) -> float:
    """Validate risk metrics quality"""
    
    risk_metrics = data.get('risk_metrics', {})
    
    if not risk_metrics:
        return 0
    
    score = 0
    
    # Check if utilization ratio is reasonable
    utilization = risk_metrics.get('credit_utilization_ratio')
    if utilization is not None and 0 <= utilization <= 2.0:  # 0-200% is reasonable
        score += 0.5
    
    # Check if payment ratio exists
    if risk_metrics.get('payment_ratio') is not None:
        score += 0.5
    
    return score


def rejection_response(reason: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create rejection response with zero scores"""
    
    return {
        'score': 0.0,           # Zero for Vana
        'total_points': 0,      # Zero internal points
        'quality': 0.0,         # Zero quality
        'valid': False,         # Invalid submission
        'rejected': True,
        'reason': reason,
        'details': details or {}
    }