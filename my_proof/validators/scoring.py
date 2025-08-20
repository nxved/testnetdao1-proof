import logging
from typing import Dict, Any
from datetime import datetime

from .completeness import calculate_completeness_score
from .financial import validate_financial_integrity
from .fraud import detect_card_fraud
from .pii import scan_for_basic_pii


def calculate_credit_statement_score(data: Dict[str, Any], blockchain_client, owner_address: str) -> Dict[str, Any]:
    """Our sophisticated scoring converted to Vana format"""
    
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
    
    # STEP 2: Quality scoring (105-point system)
    
    # 1. BASE SCORE (60 points) - Core Data Completeness
    base_score = calculate_base_score(data)  # 0-60 points
    
    # 2. ENHANCEMENT BONUS (25 points) - Optional Field Richness  
    enhancement_score = calculate_enhancement_score(data)  # 0-25 points
    
    # 3. COMPUTED VALUE (15 points) - ML Feature Quality
    computed_score = calculate_computed_value_score(data)  # 0-15 points
    
    # 4. SMART RELIABILITY BONUSES (up to 5 points)
    bonus_score = calculate_reliability_bonuses(data)  # 0-5 points
    
    # Total our product score (0-105 points)
    total_points = base_score + enhancement_score + computed_score + bonus_score
    
    # Convert to Vana scale (0.0 to 1.0)
    vana_score = min(total_points / 100.0, 1.0)  # Cap at 1.0
    
    # Map to Vana's 4-component structure for compatibility
    quality = (base_score + enhancement_score) / 85.0  # 85 = 60+25
    authenticity = computed_score / 15.0
    uniqueness = 1.0  # Always 1.0 if we reach here
    ownership = 1.0 if owner_address else 0.0
    
    return {
        'score': vana_score,  # Final score for Vana (0.0-1.0)
        'total_points': total_points,  # Our internal scoring (0-105)
        'quality': quality,
        'authenticity': authenticity, 
        'uniqueness': uniqueness,
        'ownership': ownership,
        'valid': True,
        'breakdown': {
            'base_score': base_score,
            'enhancement_score': enhancement_score,
            'computed_score': computed_score,
            'bonus_score': bonus_score
        }
    }


def calculate_base_score(data: Dict[str, Any]) -> float:
    """Core required fields and smart extraction quality (60 points)"""
    
    # Required fields present (40 points)
    completeness = calculate_completeness_score(data)
    required_fields_score = completeness['tier1_score'] * 40
    
    # Smart extraction quality (20 points)  
    financial_integrity = validate_financial_integrity(data)
    extraction_quality = financial_integrity['balance_score'] * 20
    
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
    """Bonus points for exceptional data quality (up to 5 points)"""
    
    bonus = 0
    
    # High transaction volume (50+ txns): +2 points  
    transactions = data.get('transactions', [])
    if len(transactions) >= 50:
        bonus += 2
    
    # Complete merchant data: +2 points
    if transactions and all(t.get('merchant_name') for t in transactions):
        bonus += 2
    
    # Perfect financial integrity: +1 point
    financial_check = validate_financial_integrity(data)
    if financial_check['balance_score'] == 1.0 and financial_check['utilization_score'] == 1.0:
        bonus += 1
    
    return min(bonus, 5)  # Cap at 5 points


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
        'authenticity': 0.0,    # Zero authenticity  
        'uniqueness': 0.0,      # Zero uniqueness
        'ownership': 0.0,       # Zero ownership
        'valid': False,         # Invalid submission
        'rejected': True,
        'reason': reason,
        'details': details or {}
    }