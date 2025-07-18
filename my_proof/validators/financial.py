import logging
from typing import Dict, Any


def validate_financial_integrity(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate financial calculations are mathematically correct"""
    
    financial = data.get('financial_summary', {})
    
    # Extract values with defaults
    previous = float(financial.get('previous_balance', 0))
    purchases = float(financial.get('purchases', 0))
    payments = float(financial.get('payments_credits', 0))
    fees = float(financial.get('fees_charged', 0))
    interest = float(financial.get('interest_charged', 0))
    closing = float(financial.get('closing_balance', 0))
    
    # Calculate expected closing balance
    expected_closing = previous + purchases + fees + interest - payments
    balance_diff = abs(expected_closing - closing)
    
    # Score based on accuracy (allow small rounding differences)
    if balance_diff <= 0.01:
        balance_score = 1.0
    elif balance_diff <= 0.10:
        balance_score = 0.9
    elif balance_diff <= 1.00:
        balance_score = 0.7
    else:
        balance_score = 0.0
    
    # Credit utilization validation
    credit_limit = float(data.get('account_info', {}).get('credit_limit', 0))
    utilization = float(data.get('risk_metrics', {}).get('credit_utilization_ratio', 0))
    
    utilization_score = 0.8  # Default if no credit limit
    if credit_limit > 0:
        expected_utilization = closing / credit_limit
        utilization_diff = abs(expected_utilization - utilization)
        utilization_score = 1.0 if utilization_diff <= 0.05 else 0.5
    
    return {
        'balance_score': balance_score,
        'utilization_score': utilization_score,
        'is_valid': balance_score >= 0.7 and utilization_score >= 0.5,
        'balance_difference': balance_diff,
        'expected_closing': expected_closing,
        'actual_closing': closing
    }


def validate_transaction_consistency(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate transactions align with financial summary"""
    
    transactions = data.get('transactions', [])
    financial = data.get('financial_summary', {})
    
    if not transactions:
        return {'consistency_score': 0.0, 'is_valid': False}
    
    # Calculate totals from transactions
    calculated_purchases = sum(
        float(t.get('amount', 0)) for t in transactions 
        if t.get('transaction_type', '').upper() == 'PURCHASE' and float(t.get('amount', 0)) > 0
    )
    calculated_payments = sum(
        abs(float(t.get('amount', 0))) for t in transactions 
        if t.get('transaction_type', '').upper() == 'PAYMENT' and float(t.get('amount', 0)) < 0
    )
    calculated_fees = sum(
        float(t.get('amount', 0)) for t in transactions 
        if t.get('transaction_type', '').upper() == 'FEE'
    )
    
    # Compare with financial summary
    summary_purchases = float(financial.get('purchases', 0))
    summary_payments = float(financial.get('payments_credits', 0))
    summary_fees = float(financial.get('fees_charged', 0))
    
    # Calculate consistency scores
    tolerance = 0.02  # 2 cent tolerance
    
    purchase_match = abs(calculated_purchases - summary_purchases) <= tolerance
    payment_match = abs(calculated_payments - summary_payments) <= tolerance
    fee_match = abs(calculated_fees - summary_fees) <= tolerance if summary_fees > 0 else True
    
    consistency_score = sum([purchase_match, payment_match, fee_match]) / 3.0
    
    return {
        'consistency_score': consistency_score,
        'is_valid': consistency_score >= 0.8,
        'purchase_match': purchase_match,
        'payment_match': payment_match,
        'fee_match': fee_match,
        'calculated_totals': {
            'purchases': calculated_purchases,
            'payments': calculated_payments,
            'fees': calculated_fees
        },
        'summary_totals': {
            'purchases': summary_purchases,
            'payments': summary_payments,
            'fees': summary_fees
        }
    }