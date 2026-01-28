"""
Feedback Manager Module - ISHTA (RLHF Component)
Handles user feedback, stores validation results, and manages weight/threshold adjustments.
"""

import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of user feedback."""
    VALID = "VALID"           # Alert was correct/useful
    INVALID = "INVALID"       # Alert was incorrect/false positive
    PARTIAL = "PARTIAL"       # Alert was partially correct
    DUPLICATE = "DUPLICATE"   # Alert is duplicate
    LATE = "LATE"             # Alert was too late
    NOT_NEEDED = "NOT_NEEDED" # Alert was unnecessary


@dataclass
class FeedbackRecord:
    """Single feedback record structure."""
    feedback_id: str
    alert_id: str
    zone_id: str
    feedback_type: str
    user_comment: str
    timestamp: str
    rule_id: str
    confidence_score: float  # User confidence (0-1)


class FeedbackStore:
    """Persistent feedback storage and retrieval."""
    
    def __init__(self, logs_dir: str = "./logs"):
        self.logs_dir = logs_dir
        self.feedback_file = f"{logs_dir}/feedback.jsonl"
        self.counter = 0
    
    def store_feedback(self, feedback: Dict[str, Any]) -> bool:
        """
        Store feedback record persistently.
        
        Args:
            feedback: Feedback dictionary
            
        Returns:
            Success flag
        """
        try:
            # Append to JSONL file (one JSON per line)
            with open(self.feedback_file, 'a') as f:
                f.write(json.dumps(feedback) + '\n')
            
            logger.info(f"Feedback stored: {feedback.get('feedback_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to store feedback: {str(e)}")
            return False
    
    def retrieve_feedback(self, alert_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all feedback for an alert.
        
        Args:
            alert_id: Alert ID to query
            
        Returns:
            List of feedback records
        """
        feedback_records = []
        try:
            with open(self.feedback_file, 'r') as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        if record.get('alert_id') == alert_id:
                            feedback_records.append(record)
        except FileNotFoundError:
            logger.warning(f"Feedback file not found: {self.feedback_file}")
        except Exception as e:
            logger.error(f"Error retrieving feedback: {str(e)}")
        
        return feedback_records
    
    def get_zone_feedback_stats(self, zone_id: str) -> Dict[str, Any]:
        """
        Get feedback statistics for a zone.
        
        Args:
            zone_id: Zone identifier
            
        Returns:
            Statistics dictionary
        """
        stats = {
            'total_feedback': 0,
            'valid': 0,
            'invalid': 0,
            'partial': 0,
            'accuracy_rate': 0.0
        }
        
        try:
            with open(self.feedback_file, 'r') as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        if record.get('zone_id') == zone_id:
                            stats['total_feedback'] += 1
                            feedback_type = record.get('feedback_type')
                            
                            if feedback_type == 'VALID':
                                stats['valid'] += 1
                            elif feedback_type == 'INVALID':
                                stats['invalid'] += 1
                            elif feedback_type == 'PARTIAL':
                                stats['partial'] += 1
            
            # Calculate accuracy rate
            if stats['total_feedback'] > 0:
                stats['accuracy_rate'] = round(
                    stats['valid'] / stats['total_feedback'], 3
                )
        except Exception as e:
            logger.error(f"Error calculating feedback stats: {str(e)}")
        
        return stats


class FeedbackProcessor:
    """Processes feedback and generates learning signals for weight adjustment."""
    
    def __init__(self, logs_dir: str = "./logs"):
        self.store = FeedbackStore(logs_dir)
        self.feedback_counter = 0
    
    def create_feedback_id(self) -> str:
        """Generate unique feedback ID."""
        self.feedback_counter += 1
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"FB-{timestamp}-{self.feedback_counter:05d}"
    
    def process_user_feedback(
        self,
        alert_id: str,
        zone_id: str,
        feedback_type: str,
        user_comment: str = "",
        rule_id: str = "",
        confidence_score: float = 0.5
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Process and store user feedback.
        
        Args:
            alert_id: Alert being reviewed
            zone_id: Zone identifier
            feedback_type: Type of feedback (VALID, INVALID, etc.)
            user_comment: Optional user comment
            rule_id: Rule that generated the alert
            confidence_score: User's confidence in feedback (0-1)
            
        Returns:
            Tuple of (success, feedback_record)
        """
        # Validate feedback type
        valid_types = {member.value for member in FeedbackType}
        if feedback_type not in valid_types:
            error_msg = f"Invalid feedback type: {feedback_type}"
            logger.error(error_msg)
            return False, {"error": error_msg}
        
        # Validate confidence score
        if not 0.0 <= confidence_score <= 1.0:
            confidence_score = max(0.0, min(1.0, confidence_score))
        
        # Create feedback record
        feedback = {
            'feedback_id': self.create_feedback_id(),
            'alert_id': alert_id,
            'zone_id': zone_id,
            'feedback_type': feedback_type,
            'user_comment': user_comment,
            'timestamp': datetime.utcnow().isoformat() + "Z",
            'rule_id': rule_id,
            'confidence_score': confidence_score
        }
        
        # Store feedback
        success = self.store.store_feedback(feedback)
        
        if success:
            logger.info(f"Feedback processed: {feedback['feedback_id']} ({feedback_type})")
        
        return success, feedback
    
    def generate_learning_signal(
        self,
        alert_id: str,
        feedback_type: str,
        confidence_score: float
    ) -> Dict[str, Any]:
        """
        Generate learning signal for weight/threshold adjustment.
        
        Args:
            alert_id: Alert ID
            feedback_type: Type of feedback
            confidence_score: User confidence
            
        Returns:
            Learning signal dictionary
        """
        # Weight adjustment multiplier based on feedback type
        weight_adjustments = {
            'VALID': 1.05,        # Increase weight by 5%
            'INVALID': 0.95,      # Decrease weight by 5%
            'PARTIAL': 1.00,      # No change
            'DUPLICATE': 0.90,    # Decrease (less sensitive needed)
            'LATE': 0.98,         # Slight decrease
            'NOT_NEEDED': 0.85    # Significant decrease
        }
        
        adjustment_factor = weight_adjustments.get(feedback_type, 1.0)
        
        # Scale by user confidence
        final_adjustment = 1.0 + (adjustment_factor - 1.0) * confidence_score
        
        learning_signal = {
            'alert_id': alert_id,
            'feedback_type': feedback_type,
            'confidence_score': confidence_score,
            'weight_adjustment_factor': round(final_adjustment, 4),
            'threshold_adjustment_direction': self._get_threshold_direction(feedback_type),
            'timestamp': datetime.utcnow().isoformat() + "Z"
        }
        
        logger.info(f"Learning signal generated for {alert_id}: adjustment={final_adjustment:.4f}")
        return learning_signal
    
    @staticmethod
    def _get_threshold_direction(feedback_type: str) -> str:
        """Determine threshold adjustment direction."""
        directions = {
            'VALID': 'lower',       # Lower threshold (more sensitive)
            'INVALID': 'raise',     # Raise threshold (less sensitive)
            'PARTIAL': 'maintain',
            'DUPLICATE': 'raise',
            'LATE': 'lower',        # Earlier detection
            'NOT_NEEDED': 'raise'
        }
        return directions.get(feedback_type, 'maintain')
    
    def get_zone_insights(self, zone_id: str) -> Dict[str, Any]:
        """
        Get learning insights for a zone.
        
        Args:
            zone_id: Zone identifier
            
        Returns:
            Insights dictionary
        """
        stats = self.store.get_zone_feedback_stats(zone_id)
        
        insights = {
            'zone_id': zone_id,
            'statistics': stats,
            'timestamp': datetime.utcnow().isoformat() + "Z",
            'recommendations': self._generate_recommendations(stats)
        }
        
        return insights
    
    @staticmethod
    def _generate_recommendations(stats: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on feedback stats."""
        recommendations = []
        
        if stats['total_feedback'] == 0:
            recommendations.append("Insufficient feedback to generate insights")
        elif stats['accuracy_rate'] > 0.9:
            recommendations.append("High accuracy - consider more aggressive rule settings")
        elif stats['accuracy_rate'] < 0.5:
            recommendations.append("Low accuracy - consider reviewing rule logic")
        
        if stats['invalid'] > stats['valid']:
            recommendations.append("High false positive rate - raise thresholds")
        
        return recommendations


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    processor = FeedbackProcessor(logs_dir="./logs")
    
    # Simulate user feedback
    success, feedback = processor.process_user_feedback(
        alert_id="ALT-20260128103000-00001",
        zone_id="ZONE_A",
        feedback_type="VALID",
        user_comment="Alert correctly identified temperature anomaly",
        rule_id="rule_1",
        confidence_score=0.95
    )
    
    if success:
        print("✓ Feedback processed successfully")
        print(json.dumps(feedback, indent=2))
        
        # Generate learning signal
        signal = processor.generate_learning_signal(
            alert_id=feedback['alert_id'],
            feedback_type=feedback['feedback_type'],
            confidence_score=feedback['confidence_score']
        )
        print("\n✓ Learning Signal:")
        print(json.dumps(signal, indent=2))
    
    # Get insights
    insights = processor.get_zone_insights("ZONE_A")
    print("\n✓ Zone Insights:")
    print(json.dumps(insights, indent=2))
