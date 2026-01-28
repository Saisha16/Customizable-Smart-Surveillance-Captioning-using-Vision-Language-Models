from core.zone_checker import ZoneChecker
from core.rule_evaluator import RuleEvaluator
from core.cooldown_manager import CooldownManager

def main():
    # Initialize components
    zone_checker = ZoneChecker("config/zones.json")
    rule_eval = RuleEvaluator(confidence_threshold=0.8)
    cooldown = CooldownManager(cooldown_seconds=60)

    # Mock input (from detection/action modules)
    bbox = [120, 100, 200, 260]
    action = "climbing"
    confidence = 0.92
    person_detected = True

    # Zone detection
    zone = zone_checker.get_zone(bbox)

    # Rule evaluation
    alert, reason = rule_eval.evaluate(
        person_detected=person_detected,
        action=action,
        zone=zone,
        confidence=confidence
    )

    # Cooldown check
    cooldown_key = f"{zone}_{action}"

    if alert and cooldown.is_allowed(cooldown_key):
        print("🚨 ALERT TRIGGERED")
        print("Reason:", reason)
        print("Zone:", zone)
    else:
        print("✅ NO ALERT")

if __name__ == "__main__":
    main()
