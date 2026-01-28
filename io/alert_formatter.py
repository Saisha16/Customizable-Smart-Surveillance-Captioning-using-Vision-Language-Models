"""
Alert Formatter Module - ISHTA
Creates structured alert JSON with severity, reason, timestamp, and rule evaluation results.
"""

import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """Alert severity enumeration."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AlertMetadata:
    """Metadata for alert context and traceability."""
    alert_id: str
    created_at: str
    received_at: str
    processing_time_ms: float
    source_zone: str
    evaluated_rules: List[str]


@dataclass
class AlertContent:
    """Core alert content structure."""
    zone_id: str
    severity: str
    reason: str
    timestamp: str
    metadata: Dict[str, Any]
    rule_results: Dict[str, Any]


class AlertFormatter:
    """Formats validated input into structured alert JSON."""
    
    def __init__(self):
        self.alert_counter = 0
    
    def create_alert_id(self) -> str:
        """Generate unique alert ID."""
        self.alert_counter += 1
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"ALT-{timestamp}-{self.alert_counter:05d}"
    
    def format_alert(
        self,
        zone_id: str,
        severity: str,
        reason: str,
        original_data: Dict[str, Any],
        rule_results: Dict[str, Any],
        received_at: str,
        evaluated_rules: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create structured alert JSON.
        
        Args:
            zone_id: Zone identifier
            severity: Alert severity level
            reason: Human-readable reason for alert
            original_data: Original input data
            rule_results: Results from rule evaluation (from Isha's evaluator)
            received_at: Timestamp when input was received
            evaluated_rules: List of rule IDs that were evaluated
            
        Returns:
            Formatted alert dictionary
        """
        alert_id = self.create_alert_id()
        created_at = datetime.utcnow().isoformat() + "Z"
        
        # Calculate processing time
        try:
            received_dt = datetime.fromisoformat(received_at.replace('Z', '+00:00'))
            created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            processing_time_ms = (created_dt - received_dt).total_seconds() * 1000
        except Exception:
            processing_time_ms = 0.0
        
        # Construct alert
        alert = {
            "alert_id": alert_id,
            "zone_id": zone_id,
            "severity": self._normalize_severity(severity),
            "reason": reason,
            "timestamp": created_at,
            "received_at": received_at,
            "metadata": {
                "processing_time_ms": round(processing_time_ms, 2),
                "evaluated_rules": evaluated_rules or [],
                "source_zone": zone_id
            },
            "data": original_data,
            "rule_results": rule_results,
            "status": "GENERATED"
        }
        
        logger.info(f"Alert created: {alert_id} (Zone: {zone_id}, Severity: {severity})")
        return alert
    
    @staticmethod
    def _normalize_severity(severity: str) -> str:
        """Normalize severity to valid level."""
        valid_severities = {'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'}
        normalized = severity.upper()
        return normalized if normalized in valid_severities else 'MEDIUM'
    
    def format_batch_alerts(
        self,
        alerts_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Format multiple alerts as a batch.
        
        Args:
            alerts_data: List of alert data dictionaries
            
        Returns:
            Batch alert structure
        """
        alerts = [
            self.format_alert(
                zone_id=alert['zone_id'],
                severity=alert['severity'],
                reason=alert['reason'],
                original_data=alert['data'],
                rule_results=alert.get('rule_results', {}),
                received_at=alert.get('received_at', datetime.utcnow().isoformat())
            )
            for alert in alerts_data
        ]
        
        return {
            "batch_id": f"BATCH-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "alert_count": len(alerts),
            "alerts": alerts
        }
    
    def format_for_output(self, alert: Dict[str, Any]) -> str:
        """
        Format alert for downstream output (UI, captioning, etc).
        
        Args:
            alert: Alert dictionary
            
        Returns:
            JSON string representation
        """
        return json.dumps(alert, indent=2, default=str)


class AlertValidator:
    """Validates formatted alerts for integrity."""
    
    REQUIRED_ALERT_FIELDS = {
        'alert_id', 'zone_id', 'severity', 'reason',
        'timestamp', 'metadata', 'rule_results', 'status'
    }
    
    @staticmethod
    def validate_alert(alert: Dict[str, Any]) -> 'Tuple[bool, str]':
        """
        Validate formatted alert structure.
        
        Args:
            alert: Alert dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        missing_fields = AlertValidator.REQUIRED_ALERT_FIELDS - set(alert.keys())
        
        if missing_fields:
            error_msg = f"Alert missing required fields: {missing_fields}"
            logger.error(error_msg)
            return False, error_msg
        
        if alert['severity'] not in {'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'}:
            error_msg = f"Invalid severity: {alert['severity']}"
            logger.error(error_msg)
            return False, error_msg
        
        logger.info(f"Alert {alert['alert_id']} validation successful")
        return True, ""


# Import TYPE_CHECKING to avoid circular imports
from typing import Tuple
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    formatter = AlertFormatter()
    
    alert = formatter.format_alert(
        zone_id="ZONE_A",
        severity="HIGH",
        reason="Temperature threshold exceeded (45.5°C > 40°C)",
        original_data={"temp": 45.5, "humidity": 60},
        rule_results={"rule_1": True, "rule_2": False},
        received_at="2026-01-28T10:30:00Z",
        evaluated_rules=["rule_1", "rule_2"]
    )
    
    print("✓ Formatted Alert:")
    print(json.dumps(alert, indent=2))
    
    # Validate
    is_valid, error = AlertValidator.validate_alert(alert)
    print(f"\n✓ Alert validation: {'PASSED' if is_valid else f'FAILED - {error}'}")
