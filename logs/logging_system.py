"""
Logging System Module - ISHTA
Maintains alert history with structured timestamps and persistence.
"""

import logging
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from logging.handlers import RotatingFileHandler


class AlertLogger:
    """Structured logging system for alert history and audit trail."""
    
    def __init__(self, logs_dir: str = "./logs"):
        """
        Initialize alert logger.
        
        Args:
            logs_dir: Directory for log files
        """
        self.logs_dir = logs_dir
        self.alerts_log = f"{logs_dir}/alerts.log"
        self.errors_log = f"{logs_dir}/errors.log"
        
        # Create logs directory if it doesn't exist
        os.makedirs(logs_dir, exist_ok=True)
        
        # Setup loggers
        self.alert_logger = self._setup_logger("alerts", self.alerts_log)
        self.error_logger = self._setup_logger("errors", self.errors_log)
        self.system_logger = logging.getLogger(__name__)
    
    @staticmethod
    def _setup_logger(name: str, log_file: str) -> logging.Logger:
        """
        Setup a rotating file logger.
        
        Args:
            name: Logger name
            log_file: Log file path
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # Rotating file handler (5MB per file, keep 10 backups)
        handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=10
        )
        
        # JSON formatter for structured logging
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def log_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Log alert to alerts.log with structured format.
        
        Args:
            alert: Alert dictionary
            
        Returns:
            Success flag
        """
        try:
            alert_entry = {
                'alert_id': alert.get('alert_id'),
                'zone_id': alert.get('zone_id'),
                'severity': alert.get('severity'),
                'timestamp': alert.get('timestamp'),
                'rule_results': alert.get('rule_results', {}),
                'status': 'LOGGED'
            }
            
            self.alert_logger.info(json.dumps(alert_entry))
            return True
        except Exception as e:
            self.error_logger.error(f"Failed to log alert: {str(e)}")
            return False
    
    def log_error(self, error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Log error with context.
        
        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional context dictionary
            
        Returns:
            Success flag
        """
        try:
            error_entry = {
                'error_type': error_type,
                'message': error_message,
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'context': context or {}
            }
            
            self.error_logger.error(json.dumps(error_entry))
            return True
        except Exception as e:
            self.system_logger.error(f"Failed to log error: {str(e)}")
            return False
    
    def log_feedback(self, feedback: Dict[str, Any]) -> bool:
        """
        Log user feedback action.
        
        Args:
            feedback: Feedback dictionary
            
        Returns:
            Success flag
        """
        try:
            feedback_entry = {
                'feedback_id': feedback.get('feedback_id'),
                'alert_id': feedback.get('alert_id'),
                'zone_id': feedback.get('zone_id'),
                'feedback_type': feedback.get('feedback_type'),
                'timestamp': feedback.get('timestamp'),
                'action': 'FEEDBACK_RECORDED'
            }
            
            self.alert_logger.info(json.dumps(feedback_entry))
            return True
        except Exception as e:
            self.error_logger.error(f"Failed to log feedback: {str(e)}")
            return False
    
    def retrieve_alerts_by_zone(self, zone_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all alerts for a zone from logs.
        
        Args:
            zone_id: Zone identifier
            
        Returns:
            List of alert records
        """
        alerts = []
        try:
            if not os.path.exists(self.alerts_log):
                return alerts
            
            with open(self.alerts_log, 'r') as f:
                for line in f:
                    try:
                        # Parse JSON from log line (after timestamp and level)
                        if ' - INFO - ' in line:
                            json_part = line.split(' - INFO - ', 1)[1]
                            alert = json.loads(json_part)
                            if alert.get('zone_id') == zone_id:
                                alerts.append(alert)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            self.error_logger.error(f"Error retrieving alerts: {str(e)}")
        
        return alerts
    
    def retrieve_alerts_by_time_range(
        self,
        start_time: str,
        end_time: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve alerts within time range.
        
        Args:
            start_time: ISO format start time
            end_time: ISO format end time
            
        Returns:
            List of alert records
        """
        alerts = []
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            if not os.path.exists(self.alerts_log):
                return alerts
            
            with open(self.alerts_log, 'r') as f:
                for line in f:
                    try:
                        if ' - INFO - ' in line:
                            json_part = line.split(' - INFO - ', 1)[1]
                            alert = json.loads(json_part)
                            alert_time = datetime.fromisoformat(
                                alert.get('timestamp', '').replace('Z', '+00:00')
                            )
                            
                            if start_dt <= alert_time <= end_dt:
                                alerts.append(alert)
                    except (json.JSONDecodeError, ValueError):
                        continue
        except Exception as e:
            self.error_logger.error(f"Error in time range query: {str(e)}")
        
        return alerts
    
    def get_alert_count_by_severity(self, zone_id: str) -> Dict[str, int]:
        """
        Get alert count breakdown by severity.
        
        Args:
            zone_id: Zone identifier
            
        Returns:
            Dictionary with severity counts
        """
        counts = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
        
        for alert in self.retrieve_alerts_by_zone(zone_id):
            severity = alert.get('severity', 'MEDIUM')
            if severity in counts:
                counts[severity] += 1
        
        return counts
    
    def export_audit_trail(self, output_file: str, zone_id: Optional[str] = None) -> bool:
        """
        Export audit trail (alerts + feedback) to JSON file.
        
        Args:
            output_file: Output file path
            zone_id: Optional zone filter
            
        Returns:
            Success flag
        """
        try:
            audit_data = {
                'exported_at': datetime.utcnow().isoformat() + "Z",
                'zone_id': zone_id,
                'alerts': [],
                'feedback': []
            }
            
            # Add alerts
            if zone_id:
                audit_data['alerts'] = self.retrieve_alerts_by_zone(zone_id)
            
            # Write export
            with open(output_file, 'w') as f:
                json.dump(audit_data, f, indent=2, default=str)
            
            self.system_logger.info(f"Audit trail exported to {output_file}")
            return True
        except Exception as e:
            self.error_logger.error(f"Failed to export audit trail: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    # Setup logging for this script
    logging.basicConfig(level=logging.INFO)
    
    logger_system = AlertLogger(logs_dir="./logs")
    
    # Log sample alert
    sample_alert = {
        'alert_id': 'ALT-20260128103000-00001',
        'zone_id': 'ZONE_A',
        'severity': 'HIGH',
        'timestamp': '2026-01-28T10:30:00Z',
        'rule_results': {'rule_1': True, 'rule_2': False},
        'status': 'GENERATED'
    }
    
    success = logger_system.log_alert(sample_alert)
    print(f"✓ Alert logged: {success}")
    
    # Log error
    logger_system.log_error(
        error_type="VALIDATION_ERROR",
        error_message="Invalid threshold value",
        context={'zone_id': 'ZONE_A', 'threshold': -5}
    )
    print("✓ Error logged")
    
    # Retrieve and display
    alerts = logger_system.retrieve_alerts_by_zone('ZONE_A')
    print(f"\n✓ Retrieved {len(alerts)} alert(s) for ZONE_A")
    
    # Get severity breakdown
    counts = logger_system.get_alert_count_by_severity('ZONE_A')
    print(f"✓ Severity breakdown: {counts}")
