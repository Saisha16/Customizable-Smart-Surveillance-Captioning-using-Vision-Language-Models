<img width="941" height="627" alt="image" src="https://github.com/user-attachments/assets/a606bf6e-3a46-4934-9a1c-1eee8148b376" /># Customizable Smart Surveillance Captioning using Vision–Language Models

## Project Overview

This project focuses on building an **intelligent and customizable CCTV surveillance system** that can understand what is happening in a camera feed and generate meaningful alerts. Instead of only detecting motion, the system is designed to:

* Detect people in live video streams
* Apply rule-based logic to decide whether an event is important
* Prepare the foundation for future action understanding and caption generation

At the current stage, the project is structured in a **clear, modular manner** so that each part can be independently developed and tested before full integration.

---

## What We Have Implemented So Far

At present, the project includes the following **working and partially implemented components**:

### 1. Object Detection and Tracking (YOLO Service)

**Location**: `yolo_service/`

This module is responsible for detecting people in video frames using YOLO.

**Implemented Features**:

* YOLO-based object detection
* Frame-by-frame processing
* Object tracking to maintain consistency across frames
* Separation of detection logic (`track.py`) and service interface (`app.py`)

**Purpose**:
This module acts as the *eyes* of the system, providing reliable person detection data to downstream components.

---

### 2. Rule Engine (Logic Layer)

**Location**: `rule_engine/`

The rule engine processes detection inputs and decides whether an alert should be generated based on predefined rules.

**Implemented Features**:

* Zone-based logic using coordinate data (`zones.json`)
* Rule evaluation for detecting violations
* Cooldown mechanism to prevent repeated alerts for the same event
* Modular separation of logic, configuration, and input/output handling

**Purpose**:
This module acts as the *decision maker*, ensuring that alerts are meaningful and not redundant.

---

### 3. Logging and Feedback Storage

**Location**: `logs/`

This component stores system outputs and user feedback for later analysis.

**Implemented Features**:

* Timestamped logging system
* Storage of alert feedback in JSON Lines format (`feedback.jsonl`)

**Purpose**:
Logs allow us to trace events and will later support system improvement using user feedback.

---

## Current Repository Structure

```
.
├── logs/
│   ├── feedback.jsonl
│   └── logging_system.py
├── rule_engine/
│   ├── config/
│   │   └── zones.json
│   ├── core/
│   │   ├── cooldown_manager.py
│   │   ├── rule_evaluator.py
│   │   └── zone_checker.py
│   ├── feedback/
│   │   └── feedback_manager.py
│   ├── io/
│   │   ├── alert_formatter.py
│   │   └── input_handler.py
│   └── main.py
├── yolo_service/
│   ├── app.py
│   └── track.py
└── README.md
```

---

## System Design (Current Stage)

At this stage, the system works as follows:

1. CCTV frames are passed to the YOLO service.
2. Detected objects (currently people) are tracked across frames.
3. Detection data is sent to the rule engine.
4. The rule engine checks zone rules and cooldown conditions.
5. Alerts and logs are generated when conditions are satisfied.

---

## What We Plan to Do Next (Future Work)

The following modules are **planned but not yet fully implemented**:

### 1. Action Recognition

* Integrate X3D / SlowFast models
* Analyze sequences of frames to identify actions such as running or loitering
* Trigger action analysis only when a person is detected in restricted zones

### 2. Caption Generation

* Use BLIP-2 or Qwen-VL for vision–language captioning
* Generate short, formal text descriptions of detected anomalies
* Ensure captions are grounded in detected objects and actions

### 3. User Feedback Loop

* Allow users to mark alerts as valid or invalid
* Use stored feedback to refine rule logic
* Reduce false positives over time

### 4. User Interface

* Develop a simple Streamlit dashboard
* Display alerts, zones, and generated captions
* Allow users to customize zones and sensitivity levels

---

## Academic Information

**Project Title**: Customizable Smart Surveillance Captioning using Vision–Language Models
**Department**: Information Science and Engineering

**Team Members**:

* Isha Sahay (1NT23IS085)
* Ishta Sharma (1NT23IS086)
* Himanshu Singh (1NT23IS084)
* Aditya Kumar (1NT23IS010)

**Project Guide**: Mrs. Subashree D, Assistant Professor

---

## Summary

This project is currently focused on building a **strong and clean foundation** consisting of object detection, rule-based decision making, and logging. Advanced AI modules such as action recognition and caption generation will be integrated in the next phases.

The modular structure ensures clarity, scalability, and ease of future development.
