import logging
from typing import Dict, Any


def detect_card_fraud(data: Dict[str, Any]) -> Dict[str, Any]:
    """Use Luhn algorithm to detect fake card numbers"""
    
    card_identifier = data.get('statement_metadata', {}).get('card_identifier', '')
    
    fraud_indicators = []
    
    # Check if we have a full card number (privacy violation)
    clean_card = card_identifier.replace('*', '').replace('-', '').replace(' ', '')
    
    if len(card_identifier) >= 13 and clean_card.isdigit():
        
        if '*' not in card_identifier:
            # Full card number present - privacy violation
            fraud_indicators.append({
                'type': 'PRIVACY_VIOLATION',
                'details': 'Full card number should be masked'
            })
            
            # Validate with Luhn
            if not luhn_validate(card_identifier):
                fraud_indicators.append({
                    'type': 'INVALID_CARD_NUMBER',
                    'details': 'Card number fails Luhn validation'
                })
        
        else:
            # Partially masked - validate brand consistency
            brand_check = validate_card_brand_consistency(card_identifier, data)
            if not brand_check['consistent']:
                fraud_indicators.append({
                    'type': 'BRAND_MISMATCH',
                    'details': brand_check
                })
    
    return {
        'is_fraudulent': len(fraud_indicators) > 0,
        'fraud_indicators': fraud_indicators
    }


def luhn_validate(card_number: str) -> bool:
    """Implement Luhn algorithm validation"""
    
    # Remove spaces and dashes
    card_number = card_number.replace(' ', '').replace('-', '')
    
    if not card_number.isdigit():
        return False
    
    def luhn_checksum(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10
    
    return luhn_checksum(card_number) == 0


def validate_card_brand_consistency(masked_number: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate card brand consistency with visible digits"""
    
    # Extract brand from card number pattern
    if masked_number.startswith('4'):
        expected_brand = 'VISA'
    elif masked_number.startswith('5') or masked_number.startswith('2'):
        expected_brand = 'MASTERCARD'
    elif masked_number.startswith('3'):
        if len(masked_number) >= 2:
            if masked_number[1] in ['4', '7']:
                expected_brand = 'AMEX'
            else:
                expected_brand = 'DINERS'
        else:
            expected_brand = 'AMEX'
    elif masked_number.startswith('6'):
        expected_brand = 'DISCOVER'
    else:
        expected_brand = 'UNKNOWN'
    
    # Check against reported card brand
    reported_brand = data.get('account_info', {}).get('card_brand', '').upper()
    
    # Allow some flexibility in matching
    brand_matches = (
        expected_brand == reported_brand or 
        reported_brand in ['UNKNOWN', 'OTHER', ''] or
        expected_brand == 'UNKNOWN'
    )
    
    return {
        'consistent': brand_matches,
        'expected_brand': expected_brand,
        'reported_brand': reported_brand
    }