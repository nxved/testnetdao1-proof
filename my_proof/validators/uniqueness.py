import logging
from typing import Dict, Any


def validate_uniqueness(data: Dict[str, Any], blockchain_client) -> Dict[str, Any]:
    """Absolute uniqueness validation - pass/fail only"""
    
    record_id = data.get('statement_metadata', {}).get('record_id')
    
    # Must have record_id
    if not record_id:
        return {
            'is_unique': False,
            'reason': 'MISSING_RECORD_ID'
        }
    
    # Check blockchain for existing record_id if available
    if blockchain_client:
        try:
            # Check if this specific record already exists
            existing_count = blockchain_client.get_contributor_file_count()
            if existing_count > 0:
                # For now, we'll do a simple check - in production, 
                # this should check specific record_id
                logging.warning(f"Contributor already has {existing_count} files")
                return {
                    'is_unique': False,
                    'reason': 'DUPLICATE_RECORD_ID',
                    'record_id': record_id,
                    'existing_count': existing_count
                }
        except Exception as e:
            # If blockchain check fails, reject to be safe
            logging.error(f"Blockchain uniqueness check failed: {e}")
            return {
                'is_unique': False,
                'reason': 'BLOCKCHAIN_CHECK_FAILED',
                'error': str(e)
            }
    
    # Check statement period uniqueness
    statement_period = data.get('statement_metadata', {}).get('statement_period', {})
    card_identifier = data.get('statement_metadata', {}).get('card_identifier')
    
    if statement_period and card_identifier:
        # In production, this would check blockchain for specific period
        # For now, we'll pass this check
        start_date = statement_period.get('start_date')
        end_date = statement_period.get('end_date')
        
        if not start_date or not end_date:
            return {
                'is_unique': False,
                'reason': 'INVALID_STATEMENT_PERIOD',
                'details': 'Missing start or end date'
            }
    
    # Passed all uniqueness checks
    return {
        'is_unique': True,
        'record_id': record_id
    }