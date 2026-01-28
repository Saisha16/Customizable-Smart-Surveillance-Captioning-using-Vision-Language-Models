# Rule Engine - Interview Cheat Sheet
## Quick Reference (Keep This Handy!)

---

## 🎯 30-Second Pitch

> "We built a **modular security alert system** that separates decision-making from integration. ISHA handles logic (zones, rules, cooldowns), ISHTA handles data flow (validation, formatting, feedback). Layered architecture, stateless functions, RLHF for continuous improvement."

---

## 🧠 ISHA's Brain Functions

### Zone Checker
- **What**: Point-in-Polygon algorithm
- **Why**: Determine location accuracy
- **How**: Ray casting - count edge crossings (O(n))
- **Real-world**: "Is person at coordinates (x,y) inside the restricted area?"

### Rule Evaluator
- **What**: IF-AND-THEN logic
- **Why**: Structured decision making
- **How**: All conditions must be true (AND logic)
- **Real-world**: "IF suspicious behavior AND in restricted zone AND confidence > 85% THEN alert"

### Cooldown Manager
- **What**: Alert throttling/deduplication
- **Why**: Prevent spam (100 alerts/second from same person)
- **How**: Track (person_id, zone_id, action_type) → block within 60s window
- **Real-world**: "Same person triggers 10 alerts in 1 second? Block them, wait 60s, allow new ones"

---

## 🔌 ISHTA's Glue Functions

### Input Handler
- **Validates**: JSON format, required fields, types, enums, timestamps
- **Returns**: Clean data or error
- **Real-world**: "Got messy JSON? Clean it or reject it"

### Alert Formatter
- **Takes**: ISHA's decision + original data
- **Creates**: Rich JSON with alert_id, metadata, processing time, rule results
- **Real-world**: "Make ISHA's decision pretty and trackable for downstream systems"

### Feedback Manager (RLHF)
- **Stores**: User feedback (VALID/INVALID)
- **Generates**: Learning signals (adjust weights by 5%)
- **Result**: System improves over time
- **Real-world**: "User says alert was wrong? Decrease that rule's weight. Next time, less likely to trigger"

### Logging System
- **Logs**: Every alert to JSONL (one JSON per line)
- **Queries**: By zone, time range, severity
- **Exports**: Audit trails
- **Real-world**: "Need to know what happened at 2:30pm in lab zone? Query logs."

---

## 📊 Data Flow (5 Steps)

```
Sensor Data
    ↓
ISHTA: Validate Input
    ↓ (clean data)
ISHA: Check Zone + Evaluate Rules + Cooldown
    ↓ (decision + reason)
ISHTA: Format Alert + Log
    ↓ (rich alert JSON)
Send to: UI, Captioning, Notifications
    ↓ (user reviews)
ISHTA: Collect Feedback → Learn
    ↓ (adjust weights)
Improved System
```

---

## 🎓 Why This Design Is Good

| Pattern | Benefit |
|---------|---------|
| **Separation of Concerns** | Test independently, change easily |
| **Three-Layer Architecture** | Input → Logic → Output (clean) |
| **Stateless Functions** | Scalable, predictable, testable |
| **RLHF Loop** | Self-improving, reduces false positives |
| **Audit Trail** | Compliant, debuggable, traceable |
| **Fail Fast** | Validate early, catch errors ASAP |

---

## 💬 Interview Q&A

### Q1: "Why separate ISHA and ISHTA?"
**A**: "Separation of concerns. Logic shouldn't know about I/O. ISHA is pure computation, ISHTA is pure integration. Makes testing, maintenance, and scaling easier."

### Q2: "What if ISHA is slow?"
**A**: "We measure processing_time_ms in every alert. If logic layer lags, ops get alerted. Can scale ISHA separately from ISHTA."

### Q3: "How does cooldown work?"
**A**: "Tracks (person_id, zone_id, action_type) tuple. If same tuple within 60 seconds, block alert. But different zone or action? Alert fires immediately."

### Q4: "What about false positives?"
**A**: "Three mechanisms: (1) AND logic in rules (multiple conditions needed), (2) Confidence threshold (only high-confidence triggers), (3) RLHF feedback adjusts weights down when users mark as invalid."

### Q5: "How is this scalable?"
**A**: "Stateless layers = easy load balancing. Can run ISHA on high-performance servers, ISHTA on standard servers. JSONL logging is append-only = fast writes. No locking needed (except cooldown cache)."

### Q6: "What's the latency?"
**A**: "Typical: Zone check ~1ms + Rule eval ~2ms + Formatting ~1ms = ~4ms end-to-end. Tracked in processing_time_ms field."

### Q7: "How does RLHF work?"
**A**: "User marks alert VALID → weight_factor = 1.05 (boost). User marks INVALID → weight_factor = 0.95 (reduce). Scaled by user confidence. Next rule evaluation uses updated weights."

### Q8: "What about conflicting feedback?"
**A**: "Good edge case. Solution: confidence_score is key. High-confidence feedback weighted more. Conflicting feedback with equal confidence → escalate to human or use majority voting."

---

## 🏆 Impressive Points to Mention

1. **Point-in-Polygon Algorithm**: Shows algorithm knowledge
2. **RLHF System**: Shows ML/AI awareness (popular in 2024-2025)
3. **Cooldown as Tuple**: Shows thoughtful edge-case handling
4. **Audit Trail**: Shows compliance awareness
5. **Stateless Design**: Shows scalability thinking
6. **Separation of Concerns**: Shows SOLID principles knowledge
7. **Three-Layer Architecture**: Shows clean architecture knowledge
8. **Processing Time Tracking**: Shows performance awareness

---

## 🚀 If Interviewer Asks About Extensions

### "How would you add X?"

**Add multi-person coordination**: Add rule like "IF 3+ people in restricted zone simultaneously THEN higher_priority_alert"

**Add time-of-day rules**: Rules could vary by time: "18:00-06:00 = strict rules, 09:00-17:00 = relaxed rules"

**Add ML/ML classification**: Replace point-in-polygon with deep learning object detection

**Add feedback consensus**: Multiple users feedback on same alert → consensus before learning signal

**Add anomaly detection**: Use historical data to identify unusual patterns (isolated from core logic)

**Add alert deduplication**: Multiple sensors, same event → detect and group related alerts

---

## 📚 Technical Terminology (Impress Them!)

- **Point-in-Polygon (PiP)**: O(n) algorithm to determine if point is inside polygon
- **Ray Casting**: Technique used for PiP - draw infinite ray, count intersections
- **Cooldown Window**: Time-based throttling to prevent duplicate alerts
- **RLHF**: Reinforcement Learning from Human Feedback
- **Weight Adjustment**: Multiplier applied to rule strength based on feedback
- **Tuple Tracking**: Using composite key (person, zone, action) for deduplication
- **JSONL Format**: JSON Lines - one JSON object per line for streaming/logging
- **Stateless**: Function produces same output for same input, no retained state
- **Audit Trail**: Complete log of all actions for compliance/debugging
- **End-to-End Latency**: Time from sensor input to alert output

---

## 🎬 How to Structure Your Explanation (3 Minutes)

**Minute 1**: "We built a modular security system. Two main components: ISHA handles logic (zones, rules, cooldowns), ISHTA handles integration (input, output, feedback). Three-layer architecture."

**Minute 2**: "Key innovation is cooldown manager - prevents alert spam from same person. Also RLHF - system learns from feedback, adjusts rule weights over time. Reduces false positives automatically."

**Minute 3**: "Why this matters: Separation of concerns makes it testable, maintainable, scalable. Stateless design allows horizontal scaling. Audit trail ensures compliance. Complete data flow is tracked."

**Wrap-up**: "Architecture follows SOLID principles, clean architecture, and industry best practices. Ready for production use."

---

## 📋 Files You Own (ISHTA)

- ✅ `io/input_handler.py` - Input validation
- ✅ `io/alert_formatter.py` - Alert generation  
- ✅ `feedback/feedback_manager.py` - RLHF system
- ✅ `logs/logging_system.py` - Audit trail

## Files ISHA Owns (Reference Only)

- `config/zones.json` - Zone definitions
- `core/zone_checker.py` - Point-in-polygon
- `core/rule_evaluator.py` - Rule logic
- `core/cooldown_manager.py` - Alert throttling

---

## ✨ Final Tip

When interviewer asks "Tell me about a project you're proud of", start with:

> "We designed a modular security alert system that demonstrates several architectural principles I'm passionate about: clean separation of concerns, scalability through stateless design, compliance through audit trails, and continuous improvement through RLHF. Here's what makes it special..."

[Then dive into whichever component fits the conversation]

---

**Good luck! 🚀**
