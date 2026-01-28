class RuleEvaluator:
    def __init__(self, confidence_threshold=0.8):
        self.confidence_threshold = confidence_threshold
        self.suspicious_actions = ["climbing", "intrusion", "jumping"]

    def evaluate(self, person_detected, action, zone, confidence):
        if not person_detected:
            return False, "No person detected"

        if confidence < self.confidence_threshold:
            return False, "Low confidence detection"

        if action not in self.suspicious_actions:
            return False, f"Action '{action}' is not suspicious"

        if zone != "restricted":
            return False, f"Action in {zone} zone"

        return True, "Suspicious action in restricted zone"
