import logging
from typing import Dict, Any
from datetime import datetime

from .completeness import calculate_completeness_score
from .financial import validate_financial_integrity
from .fraud import detect_card_fraud
from .pii import scan_for_basic_pii
from ..country_config import country_scoring


def calculate_credit_statement_score(data: Dict[str, Any], blockchain_client, owner_address: str) -> Dict[str, Any]:
    """Our sophisticated scoring converted to Vana format with country-based fair rewards"""
    
    # Extract country information for fair scoring
    country_code = data.get('statement_metadata', {}).get('country_code', 'US')
    country_info = country_scoring.get_country_info(country_code)
    
    logging.info(f"Processing statement from {country_info['country_name']} (Tier {country_info['tier']})")
    
    # STEP 1: Hard gates (immediate rejection if failed)
    
    # Gate 1: Uniqueness
    #TODO: Implement uniqueness check
    
    # Gate 2: Card fraud detection
    card_fraud = detect_card_fraud(data)
    if card_fraud['is_fraudulent']:
        return rejection_response("FAKE_CARD_DETECTED", card_fraud)
    
    # Gate 3: PII security
    pii_scan = scan_for_basic_pii(data)
    if pii_scan['pii_detected']:
        return rejection_response("PII_DETECTED", pii_scan)
    
    # STEP 2: Quality scoring (100-point system)
    
    # 1. BASE SCORE (50 points) - Core Data Completeness
    base_score = calculate_base_score(data)  # 0-50 points
    
    # 2. ENHANCEMENT SCORE (25 points) - Optional Field Richness  
    enhancement_score = calculate_enhancement_score(data)  # 0-25 points
    
    # 3. COMPUTED VALUE (15 points) - ML Feature Quality
    computed_score = calculate_computed_value_score(data)  # 0-15 points
    
    # 4. RELIABILITY SCORE (10 points) - Data Quality Excellence
    reliability_score = calculate_reliability_bonuses(data)  # 0-10 points
    
    # Total our product score (0-100 points) before country adjustment
    base_total_points = base_score + enhancement_score + computed_score + reliability_score
    
    # STEP 3: Apply country-based fair scoring
    country_adjusted = country_scoring.calculate_country_adjusted_score(base_total_points, country_code)
    
    # Use country-adjusted values for final response
    total_points = country_adjusted['final_score']
    vana_score = country_adjusted['vana_score']
    quality = vana_score  # Use comprehensive score as quality
    
    return {
        'score': vana_score,  # Final score for Vana (0.0-1.0) 
        'total_points': total_points,  # Country-adjusted scoring
        'quality': quality,
        'valid': True,
        'country_info': country_adjusted['country_info'],  # Include country details
        'breakdown': {
            'base_score': base_score,
            'enhancement_score': enhancement_score, 
            'computed_score': computed_score,
            'reliability_score': reliability_score,
            'raw_total': base_total_points,  # Pre-country adjustment
            'country_multiplier': country_adjusted['country_multiplier'],
            'scarcity_bonus': country_adjusted['scarcity_bonus'],
            'country_adjusted_total': country_adjusted['adjusted_total']
        }
    }


def calculate_base_score(data: Dict[str, Any]) -> float:
    """Core required fields and smart extraction quality (50 points)"""
    
    # Required fields present (35 points)
    completeness = calculate_completeness_score(data)
    required_fields_score = completeness['tier1_score'] * 35
    
    # Smart extraction quality (15 points)  
    financial_integrity = validate_financial_integrity(data)
    extraction_quality = financial_integrity['balance_score'] * 15
    
    return required_fields_score + extraction_quality


def calculate_enhancement_score(data: Dict[str, Any]) -> float:
    """Optional fields that add significant value (25 points)"""
    
    completeness = calculate_completeness_score(data)
    
    # Account info completeness (10 points)
    account_score = completeness['tier2_score'] * 10
    
    # Financial detail depth (10 points) - based on presence of optional financial fields
    financial_fields = ['fees_charged', 'interest_charged', 'available_credit', 'cash_advances']
    financial_present = sum(1 for field in financial_fields 
                           if data.get('financial_summary', {}).get(field) is not None)
    financial_score = (financial_present / len(financial_fields)) * 10
    
    # Transaction enhancement (5 points) - based on enriched transaction data
    transactions = data.get('transactions', [])
    if transactions:
        enhanced_count = sum(1 for t in transactions 
                           if t.get('merchant_name') and t.get('category_primary'))
        transaction_score = min(5.0, (enhanced_count / len(transactions)) * 5)
    else:
        transaction_score = 0
    
    return account_score + financial_score + transaction_score


def calculate_computed_value_score(data: Dict[str, Any]) -> float:
    """ML-generated features and their quality (15 points)"""
    
    completeness = calculate_completeness_score(data)
    
    # Pattern accuracy (5 points)
    pattern_score = validate_spending_patterns(data) * 5
    
    # Risk metric reliability (5 points) 
    risk_score = validate_risk_metrics(data) * 5
    
    # Behavioral scores (5 points) - based on tier3 completeness
    behavioral_score = completeness['tier3_score'] * 5
    
    return pattern_score + risk_score + behavioral_score


def calculate_reliability_bonuses(data: Dict[str, Any]) -> float:
    """Reliability points for data quality excellence (up to 10 points)"""
    
    score = 0
    
    # Transaction volume scoring (4 points)
    transactions = data.get('transactions', [])
    if len(transactions) >= 50:
        score += 4
    elif len(transactions) >= 25:
        score += 3
    elif len(transactions) >= 10:
        score += 2
    elif len(transactions) >= 5:
        score += 1
    
    # Complete merchant data: +3 points
    if transactions and all(t.get('merchant_name') for t in transactions):
        score += 3
    
    # Perfect financial integrity: +3 points
    financial_check = validate_financial_integrity(data)
    if financial_check['balance_score'] == 1.0 and financial_check['utilization_score'] == 1.0:
        score += 3
    
    return min(score, 10)  # Cap at 10 points


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