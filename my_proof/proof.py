import json
import logging
import os
from datetime import datetime

from my_proof.models.proof_response import ProofResponse
from my_proof.utils.schema import validate_schema
from my_proof.config import settings
from my_proof.validators.scoring import calculate_credit_statement_score


class Proof:
    def __init__(self):
        self.proof_response = ProofResponse(dlp_id=settings.DLP_ID)

    def generate(self) -> ProofResponse:
        """Generate proof with comprehensive validation pipeline"""
        
        logging.info("Starting credit statement proof generation")
        
        input_data = self._load_input_data()
        if not input_data:
            return self._set_rejection_response("NO_INPUT_DATA")
        
        schema_type, schema_valid = validate_schema(input_data)
        if not schema_valid:
            return self._set_rejection_response("INVALID_SCHEMA")
        
        validation_result = calculate_credit_statement_score(input_data)
        
        if validation_result.get('rejected'):
            self.proof_response.valid = False
            self.proof_response.score = 0.0
            self.proof_response.quality = 0.0
            self.proof_response.authenticity = 0.0
            self.proof_response.uniqueness = 0.0
            self.proof_response.ownership = 0.0
            
            self.proof_response.attributes = {
                'rejected': True,
                'rejection_reason': validation_result['reason'],
                'details': validation_result.get('details', {}),
                'record_id': input_data.get('statement_metadata', {}).get('record_id')
            }
            
            logging.error(f"Data rejected: {validation_result['reason']}")
            return self.proof_response
        
        self.proof_response.valid = True
        self.proof_response.score = validation_result['score']
        self.proof_response.quality = validation_result['quality']
        self.proof_response.authenticity = 1.0
        self.proof_response.uniqueness = 1.0
        self.proof_response.ownership = 1.0
        self.proof_response.attributes = {
            'schema_type': schema_type,
            'record_id': input_data.get('statement_metadata', {}).get('record_id'),
            'statement_date': input_data.get('statement_metadata', {}).get('statement_date'),
            'card_brand': input_data.get('account_info', {}).get('card_brand'),
            'total_points': validation_result['total_points'],
            'score_breakdown': validation_result['breakdown'],
            'has_enriched_features': bool(input_data.get('engineered_features'))
        }
        self.proof_response.metadata = {
            'schema_type': schema_type,
            'validation_timestamp': datetime.now().isoformat(),
            'validation_version': '2.0'
        }
        
        logging.info(f"Validation successful: {validation_result['score']:.3f} ({validation_result['total_points']} points)")
        return self.proof_response
    
    def _load_input_data(self) -> dict:
        """Load and parse input JSON data"""
        
        try:
            input_files = [f for f in os.listdir(settings.INPUT_DIR) if f.endswith('.json')]
            if not input_files:
                logging.error("No JSON input files found")
                return None
            
            input_file = os.path.join(settings.INPUT_DIR, input_files[0])
            with open(input_file, 'r') as f:
                data = json.loads(f.read())
                logging.info(f"Loaded input file: {input_file}")
                return data
                
        except Exception as e:
            logging.error(f"Failed to load input data: {e}")
            return None
    
    def _set_rejection_response(self, reason: str):
        """Set complete rejection response with zero points"""
        
        self.proof_response.valid = False
        self.proof_response.score = 0.0
        self.proof_response.quality = 0.0
        self.proof_response.authenticity = 0.0
        self.proof_response.uniqueness = 0.0
        self.proof_response.ownership = 0.0
        
        self.proof_response.attributes = {
            'rejected': True,
            'rejection_reason': reason
        }
        
        logging.error(f"Proof rejected: {reason}")
        return self.proof_response

