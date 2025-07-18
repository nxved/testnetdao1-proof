import re
import logging
from typing import Dict, Any


def scan_for_basic_pii(data: Dict[str, Any]) -> Dict[str, Any]:
    """Scan for obvious PII patterns that indicate a privacy issue"""
    
    # Simplified PII patterns - only the most obvious ones
    pii_patterns = {
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',  # Social Security Number
        'full_cc': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Full credit card
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone number
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
    }
    
    pii_found = []
    
    # Only scan transaction descriptions and merchant names
    transactions = data.get('transactions', [])
    for txn in transactions:
        description = str(txn.get('description', ''))
        merchant = str(txn.get('merchant_name', ''))
        
        for pii_type, pattern in pii_patterns.items():
            if re.search(pattern, description, re.IGNORECASE) or re.search(pattern, merchant, re.IGNORECASE):
                pii_found.append(pii_type)
                logging.warning(f"PII detected: {pii_type}")
                break  # One finding per transaction is enough
    
    return {
        'pii_detected': len(pii_found) > 0,
        'pii_types': list(set(pii_found)),
        'is_clean': len(pii_found) == 0,
        'pii_count': len(pii_found)
    }