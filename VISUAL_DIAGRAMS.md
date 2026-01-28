# Rule Engine - Visual Diagrams & Examples
## Make It Stick: See It, Understand It

---

## 🎯 System Layers (Visual)

```
┌────────────────────────────────────────────────────────────────┐
│                      SENSOR INPUT                              │
│  Camera/IoT sends: {zone, person, action, confidence, time}   │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│               ISHTA INPUT LAYER                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Input Handler:                                           │  │
│  │  1. Validate JSON format                                 │  │
│  │  2. Check required fields: zone_id, severity, data       │  │
│  │  3. Validate field types                                 │  │
│  │  4. Validate enums (severity must be HIGH, LOW, etc)     │  │
│  │  5. Validate timestamp (ISO 8601)                        │  │
│  │  Result: CLEAN DATA ✓ or ERROR ✗                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│               ISHA LOGIC LAYER                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Zone Checker:                                            │  │
│  │ Is person at (x,y) in polygon?                           │  │
│  │ Algorithm: Ray Casting                                   │  │
│  │ Result: YES/NO with confidence                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│               ↓                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Rule Evaluator:                                          │  │
│  │ IF person_detected AND action==suspicious AND            │  │
│  │    zone==restricted AND confidence>threshold             │  │
│  │ THEN alert=true                                          │  │
│  │ Result: decision + reason                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│               ↓                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Cooldown Manager:                                        │  │
│  │ Has (person_id, zone_id, action) fired in last 60s?      │  │
│  │ YES → Block alert                                        │  │
│  │ NO → Allow alert                                         │  │
│  │ Result: final decision                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│               ISHTA OUTPUT LAYER                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Alert Formatter:                                         │  │
│  │  Create structured JSON with:                            │  │
│  │  - alert_id: "ALT-20260128173628-00001" (unique track)  │  │
│  │  - severity: "HIGH"                                      │  │
│  │  - reason: "Suspicious behavior in restricted zone"      │  │
│  │  - timestamp: "2026-01-28T17:36:28Z" (ISO 8601)         │  │
│  │  - metadata: processing_time, rules_evaluated, etc       │  │
│  │  - data: original sensor data                            │  │
│  │  - rule_results: {rule_1: true, rule_2: false, ...}      │  │
│  └──────────────────────────────────────────────────────────┘  │
│               ↓                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Logging System:                                          │  │
│  │  Write alert to alerts.log (JSONL format)                │  │
│  │  Each line = one JSON alert object                       │  │
│  │  Rotating files, searchable by zone/time/severity        │  │
│  └──────────────────────────────────────────────────────────┘  │
│               ↓                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Output Distribution:                                     │  │
│  │  ├─ Send to UI Dashboard                                 │  │
│  │  ├─ Send to Captioning Module                            │  │
│  │  └─ Send to Notification Service                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                      USER REVIEWS ALERT                        │
│  "This alert was CORRECT" → Feedback: VALID, confidence=0.95  │
│  "This alert was FALSE POSITIVE" → Feedback: INVALID, conf=0.9│
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│               ISHTA FEEDBACK LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Feedback Manager (RLHF):                                 │  │
│  │  1. Store feedback (alert_id, type, user_comment)        │  │
│  │  2. Generate learning signal:                            │  │
│  │     - VALID → weight_factor = 1.05 (boost)               │  │
│  │     - INVALID → weight_factor = 0.95 (reduce)            │  │
│  │     - Scale by user confidence                           │  │
│  │  3. Next rule evaluation uses updated weights             │  │
│  │  Result: System learns, improves over time               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## 🎬 Real Example: Person in Lab

### Scenario Setup
```
Time: 2026-01-28 14:30:00
Location: Restricted Lab (coordinates 45.2, 78.5)
Person ID: P_001
Action: Suspicious Loitering (>30 sec)
Confidence: 0.92
Last Alert from P_001: 5 minutes ago (cooldown expired)
```

### Step-by-Step Execution

```
┌─ STEP 1: INPUT ──────────────────────────────────────────┐
│ Raw JSON:                                                │
│ {                                                        │
│   "zone_id": "restricted_lab",                          │
│   "person_id": "P_001",                                 │
│   "action": "suspicious_loitering",                     │
│   "confidence": 0.92,                                   │
│   "timestamp": "2026-01-28T14:30:00Z",                  │
│   "data": {"duration_sec": 45}                          │
│ }                                                        │
└──────────────────────────────────────────────────────────┘
           │
           ▼
┌─ STEP 2: ISHTA INPUT VALIDATION ─────────────────────────┐
│ ✓ Valid JSON?                      YES                  │
│ ✓ Has zone_id?                     YES                  │
│ ✓ Has data?                        YES                  │
│ ✓ timestamp ISO 8601?              YES                  │
│ ✓ confidence in [0,1]?             YES (0.92)           │
│ Decision: PASS → Continue                                │
│ Clean Data Returned:               READY FOR LOGIC       │
└──────────────────────────────────────────────────────────┘
           │
           ▼
┌─ STEP 3: ISHA ZONE CHECKER ──────────────────────────────┐
│ Question: Is person at (45.2, 78.5) in lab polygon?      │
│ Zone Polygon: [(0,0), (100,0), (100,100), (0,100)]       │
│ Algorithm: Ray Casting                                   │
│  - Draw ray from (45.2, 78.5) to infinity (right)        │
│  - Count edge crossings: 1                               │
│  - Odd = inside ✓                                        │
│ Result: INSIDE RESTRICTED ZONE                          │
└──────────────────────────────────────────────────────────┘
           │
           ▼
┌─ STEP 4: ISHA RULE EVALUATION ───────────────────────────┐
│ Rule Set to Evaluate:                                    │
│ Rule #1: person_detected == true                         │
│          → YES (P_001 detected) ✓                        │
│ Rule #2: zone_type == "restricted"                       │
│          → YES (restricted_lab) ✓                        │
│ Rule #3: action in suspicious_list                       │
│          → YES (suspicious_loitering) ✓                 │
│ Rule #4: confidence > 0.85                               │
│          → YES (0.92 > 0.85) ✓                           │
│ Rule #5: duration_in_zone > 10_seconds                   │
│          → YES (45 > 10) ✓                               │
│                                                          │
│ All Rules PASSED: alert = TRUE                           │
└──────────────────────────────────────────────────────────┘
           │
           ▼
┌─ STEP 5: ISHA COOLDOWN CHECK ────────────────────────────┐
│ Query: Last alert from (P_001, restricted_lab, loiter)?  │
│ Result: 5 minutes ago                                    │
│ Cooldown Window: 60 seconds                              │
│ Decision: 5min > 60sec → COOLDOWN EXPIRED ✓              │
│ Action: ALLOW THIS ALERT                                 │
└──────────────────────────────────────────────────────────┘
           │
           ▼
┌─ STEP 6: ISHA FINAL DECISION ────────────────────────────┐
│ alert: true                                              │
│ reason: "Suspicious loitering in restricted lab > 10s"  │
│ confidence: 0.92                                         │
│ zone_id: "restricted_lab"                                │
│ rule_id: "rule_5_restricted"                             │
│ processing_time_ms: 2.3                                  │
│ rules_evaluated: 5                                       │
│ rules_passed: 5                                          │
│ cooldown_status: "passed"                                │
└──────────────────────────────────────────────────────────┘
           │
           ▼
┌─ STEP 7: ISHTA ALERT FORMATTING ─────────────────────────┐
│ {                                                        │
│   "alert_id": "ALT-20260128143000-00057",                │
│   "zone_id": "restricted_lab",                           │
│   "severity": "HIGH",                                    │
│   "reason": "Suspicious loitering in restricted area",  │
│   "timestamp": "2026-01-28T14:30:00Z",                   │
│   "received_at": "2026-01-28T14:30:00.100Z",             │
│   "metadata": {                                          │
│     "processing_time_ms": 2.3,                           │
│     "evaluated_rules": [                                 │
│       "rule_1_detect", "rule_2_zone", "rule_3_action",  │
│       "rule_4_confidence", "rule_5_restricted"           │
│     ],                                                   │
│     "source_zone": "restricted_lab"                      │
│   },                                                     │
│   "data": {                                              │
│     "person_id": "P_001",                                │
│     "duration_sec": 45,                                  │
│     "confidence": 0.92                                   │
│   },                                                     │
│   "rule_results": {                                      │
│     "person_detected": true,                             │
│     "zone_restricted": true,                             │
│     "action_suspicious": true,                           │
│     "confidence_high": true,                             │
│     "duration_exceed": true                              │
│   },                                                     │
│   "status": "GENERATED"                                  │
│ }                                                        │
└──────────────────────────────────────────────────────────┘
           │
           ▼
┌─ STEP 8: LOGGING ────────────────────────────────────────┐
│ Written to logs/alerts.log (append):                      │
│ {"alert_id":"ALT-...", "zone":"restricted_lab", ...}      │
│ (One JSON per line - JSONL format)                        │
└──────────────────────────────────────────────────────────┘
           │
           ▼
┌─ STEP 9: OUTPUT DISTRIBUTION ────────────────────────────┐
│ ├─ UI Dashboard: Display alert immediately               │
│ │  (Security team sees: "HIGH severity - Lab intrusion") │
│ ├─ Captioning: Overlay on video stream                   │
│ │  (Shows: "ALERT: Unauthorized in lab")                 │
│ └─ Notifications: Send alert (email/SMS)                 │
│    (Message: "Restricted zone breach - Lab")             │
└──────────────────────────────────────────────────────────┘
           │
           ▼
┌─ STEP 10: USER REVIEWS & FEEDBACK ───────────────────────┐
│ Security Officer reviews alert at 14:32 (2 min later)     │
│ Feedback: "VALID - This was correct, real threat"        │
│ User Confidence: 0.95 (95% sure)                          │
│                                                          │
│ Feedback Record Created:                                 │
│ {                                                        │
│   "feedback_id": "FB-20260128143200-00001",               │
│   "alert_id": "ALT-20260128143000-00057",                 │
│   "zone_id": "restricted_lab",                            │
│   "feedback_type": "VALID",                               │
│   "user_comment": "Real unauthorized access attempt",     │
│   "timestamp": "2026-01-28T14:32:00Z",                    │
│   "confidence_score": 0.95                                │
│ }                                                        │
└──────────────────────────────────────────────────────────┘
           │
           ▼
┌─ STEP 11: RLHF LEARNING SIGNAL ──────────────────────────┐
│ Feedback Manager Analysis:                               │
│ - Feedback Type: VALID (user says alert was correct)     │
│ - Base Factor: 1.05 (boost valid rules)                  │
│ - User Confidence: 0.95 (95% sure)                       │
│ - Final Factor: 1.0 + (1.05-1.0)*0.95 = 1.0475          │
│                                                          │
│ Learning Signal:                                         │
│ {                                                        │
│   "alert_id": "ALT-20260128143000-00057",                 │
│   "weight_adjustment": 1.0475,   ← Boost by 4.75%        │
│   "threshold_adjustment": "lower", ← More sensitive      │
│   "affected_rules": [                                     │
│     "rule_5_restricted"  ← This rule gets boosted        │
│   ]                                                      │
│ }                                                        │
│                                                          │
│ Result: Next time "suspicious_loitering in lab"          │
│ is 4.75% more likely to trigger alert                    │
└──────────────────────────────────────────────────────────┘
```

---

## 🔄 Comparison: With vs Without Each Component

### Without Input Validation (ISHTA Input Handler)
```
Sensor sends: {"zone": "lab"}  ← Missing required fields!
System crashes: KeyError: 'severity'
No error message, just broken
```

### With Input Validation
```
Sensor sends: {"zone": "lab"}  ← Missing required fields!
Handler checks: ✓ Checks all fields
Returns: {"error": "Missing required fields: severity, timestamp, data"}
System continues gracefully, logs error, operator sees issue
```

---

### Without Cooldown (ISHA Cooldown Manager)
```
Person P_001 walks into lab
t=0.0s: Alert #1 ✓
t=0.1s: Alert #2 ✓
t=0.2s: Alert #3 ✓
...
t=60.0s: Alert #600 ✓
Security team gets 600 identical alerts
Alert fatigue → ignore all of them
Actual threat when P_001 does something worse: MISSED
```

### With Cooldown
```
Person P_001 walks into lab
t=0.0s: Alert #1 ✓ (Logged, sent to UI)
t=0.1s: Alert #2 ✗ (Blocked - cooldown active)
t=0.2s: Alert #3 ✗ (Blocked - cooldown active)
...
t=60.0s: Alert #2 ✓ (Cooldown expired, alert allowed)
Security team gets 1-2 alerts, focused
When P_001 does something worse: ALERT FIRES IMMEDIATELY (context change)
```

---

### Without RLHF (ISHTA Feedback Manager)
```
Day 1: System has false positive rate of 40%
Day 30: System still has 40% false positive rate
System never improves
```

### With RLHF
```
Day 1: System has false positive rate of 40%
Day 5: Users mark false alerts, rules adjust down
Day 10: False positive rate down to 25%
Day 20: False positive rate down to 15%
Day 30: False positive rate down to 8%
System continuously improves with real-world feedback
```

---

## 📊 Processing Pipeline Diagram

```
Input Validation        Logic Layer             Output Layer
┌──────────────┐       ┌────────────┐          ┌────────────┐
│              │       │            │          │            │
│  JSON?  ────→│       │ Zone Check │          │ Format     │
│              │       │    ↓       │          │    ↓       │
│  Fields? ────→│       │ Rules     │          │ Log        │
│              │       │    ↓       │          │    ↓       │
│  Types?  ────→│       │ Cooldown  │          │ Distribute │
│              │       │    ↓       │          │            │
│  Values? ────→│       │ Result    │          │ Feedback   │
│              │       │            │          │    ↓       │
└──────────────┘       └────────────┘          └────────────┘
      ↓                      ↓                        ↓
   2ms                    4ms                      2ms
   
   TOTAL LATENCY: ~8ms (can handle 125 alerts/sec per server)
```

---

## 🎯 Why It Matters: Before & After

### BEFORE (Monolithic Approach)
```
One big file: alert_system.py (3000 lines)
├─ Input handling mixed with logic
├─ Validation mixed with rules
├─ Logging mixed with decisions
├─ Feedback mixed with calculations
└─ Result: 
   - Hard to test individual parts
   - One bug breaks everything
   - Can't scale components independently
   - Scary to make changes
```

### AFTER (Modular Approach)
```
Separate modules (ISHA + ISHTA)
├─ ISHA: Pure logic (750 lines)
├─ ISHTA Input: Validation (400 lines)
├─ ISHTA Output: Formatting (300 lines)
├─ ISHTA Feedback: Learning (450 lines)
├─ ISHTA Logging: Storage (350 lines)
└─ Result:
   - Test zone_checker independently
   - Test rule_evaluator independently
   - Test input validation independently
   - Change one module without breaking others
   - Scale components separately
   - Easy to maintain and extend
```

---

## 🚀 Scalability Example

### Processing 1000 alerts/second

```
With monolithic system:
└─ Single server needed for all 1000 alerts/sec
   (Can't split - all mixed together)
   Must buy BIG expensive server

With modular system:
├─ Input validation layer:
│  └─ 8 cheap servers (125 alerts/sec each)
│
├─ Logic layer (ISHA):
│  └─ 4 medium servers (250 alerts/sec each)
│
└─ Output layer:
   └─ 2 cheap servers (500 alerts/sec each)

Total cost: Many cheap servers < One huge server
Benefit: One layer overloaded? Just add more servers to that layer
```

---

**Visual thinking makes it stick! Show these diagrams to interviewer and walk through them.**
