"""
Input Handler Module - ISHTA
Validates incoming JSON, extracts required fields, handles missing/invalid data.
"""

import json
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class InputValidator:
    """Validates incoming alert data and enforces schema compliance."""
    
    # Required fields for valid alert input
    REQUIRED_FIELDS = {
        'zone_id': str,
        'severity': str,
        'timestamp': str,
        'data': dict
    }
    
    # Valid severity levels
    VALID_SEVERITIES = {'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'}
    
    @staticmethod
    def validate_json(raw_input: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Validate JSON format.
        
        Args:
            raw_input: Raw JSON string from input
            
        Returns:
            Tuple of (is_valid, parsed_dict, error_message)
        """
        try:
            data = json.loads(raw_input)
            return True, data, ""
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    @staticmethod
    def validate_schema(data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate required fields and data types.
        
        Args:
            data: Parsed JSON data
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for required fields
        missing_fields = [field for field in InputValidator.REQUIRED_FIELDS 
                         if field not in data]
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            logger.error(error_msg)
            return False, error_msg
        
        # Validate field types
        for field, expected_type in InputValidator.REQUIRED_FIELDS.items():
            if not isinstance(data[field], expected_type):
                error_msg = f"Field '{field}' must be {expected_type.__name__}, got {type(data[field]).__name__}"
                logger.error(error_msg)
                return False, error_msg
        
        # Validate severity
        if data['severity'].upper() not in InputValidator.VALID_SEVERITIES:
            error_msg = f"Invalid severity: {data['severity']}. Must be one of {InputValidator.VALID_SEVERITIES}"
            logger.error(error_msg)
            return False, error_msg
        
        # Validate timestamp format
        try:
            datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        except ValueError:
            error_msg = f"Invalid timestamp format: {data['timestamp']}. Use ISO 8601 format"
            logger.error(error_msg)
            return False, error_msg
        
        return True, ""
    
    @staticmethod
    def validate_input(raw_input: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Complete validation pipeline: JSON format → schema.
        
        Args:
            raw_input: Raw input string
            
        Returns:
            Tuple of (is_valid, parsed_data, error_message)
        """
        # Step 1: Validate JSON format
        is_valid_json, parsed_data, json_error = InputValidator.validate_json(raw_input)
        if not is_valid_json:
            return False, None, json_error
        
        # Step 2: Validate schema
        is_valid_schema, schema_error = InputValidator.validate_schema(parsed_data)
        if not is_valid_schema:
            return False, parsed_data, schema_error
        
        logger.info(f"Input validation successful for zone: {parsed_data.get('zone_id')}")
        return True, parsed_data, ""


class InputHandler:
    """Main input handler coordinating validation and field extraction."""
    
    def __init__(self):
        self.validator = InputValidator()
    
    def handle_input(self, raw_input: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Process incoming input through complete validation pipeline.
        
        Args:
            raw_input: Raw input data
            
        Returns:
            Tuple of (is_valid, extracted_data, error_message)
        """
        return self.validator.validate_input(raw_input)
    
    def extract_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and normalize required fields from validated data.
        
        Args:
            data: Validated input data
            
        Returns:
            Dictionary with extracted and normalized fields
        """
        return {
            'zone_id': str(data['zone_id']).strip().upper(),
            'severity': data['severity'].upper(),
            'timestamp': data['timestamp'],
            'data': data['data'],
            'received_at': datetime.utcnow().isoformat()
        }


# Example usage
if __name__ == "__main__":
    # Configure root logger
    logging.basicConfig(level=logging.INFO)
    
    # Test valid input
    valid_input = json.dumps({
        "zone_id": "zone_a",
        "severity": "HIGH",
        "timestamp": "2026-01-28T10:30:00Z",
        "data": {"temp": 45.5, "humidity": 60}
    })
    
    handler = InputHandler()
    is_valid, parsed_data, error = handler.handle_input(valid_input)
    
    if is_valid:
        extracted = handler.extract_fields(parsed_data)
        print("✓ Input validated successfully")
        print(json.dumps(extracted, indent=2))
    else:
        print(f"✗ Validation failed: {error}")
    
    # Test invalid input
    invalid_input = '{"zone_id": "zone_a"}'  # Missing required fields
    is_valid, _, error = handler.handle_input(invalid_input)
    if not is_valid:
        print(f"\n✓ Invalid input correctly rejected: {error}")
