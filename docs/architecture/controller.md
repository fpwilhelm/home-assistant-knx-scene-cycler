# Controller

Part of the KNX Scene Cycler Architecture Documentation.

Related documents:

- Architecture Overview
- Scene Mapping
- Runtime
- Config Flow

---

# Purpose

The Controller contains the complete business logic of KNX Scene Cycler.

It is the only component responsible for making operational decisions.

The Controller processes incoming events, evaluates the configured Scene Mappings and updates the Runtime accordingly.

---

# Responsibilities

The Controller is responsible for:

- Processing KNX events
- Evaluating trigger modes
- Selecting the appropriate Scene Mapping
- Activating Home Assistant scenes
- Updating the Runtime
- Coordinating optional status LED updates

The Controller is not responsible for:

- Persistent configuration
- Runtime storage
- KNX communication infrastructure
- User configuration

Those responsibilities belong to other components of the architecture.

---

# Event Processing

Every user interaction follows the same logical sequence.

```text
KNX Event
      │
      ▼
Controller
      │
      ▼
Evaluate Trigger Mode
      │
      ▼
Select Scene Mapping
      │
      ▼
Activate Home Assistant Scene
      │
      ▼
Update Runtime
      │
      ▼
Update Status LED (optional)
```

This sequence guarantees that all operational decisions pass through a single component.

---

# Business Logic

The Controller evaluates the current Runtime together with the configured Scene Mappings.

Based on the configured Trigger Mode it decides which Scene Mapping should become active.

The Runtime is updated only after successful scene activation.

---

# Runtime Ownership

The Runtime is owned by the Controller.

Other components may read Runtime information but do not modify it directly.

This guarantees consistent state transitions throughout the integration.

---

# Scene Activation

The Controller activates Home Assistant scenes through the Home Assistant service layer.

The Controller never manipulates Scene Mappings during normal operation.

Scene Mappings remain persistent configuration.

---

# Error Handling

The Controller validates incoming events before processing them.

Unexpected or invalid events are ignored without affecting the current Runtime.

Failures during scene activation do not modify the Runtime state.

---

# Design Principles

The Controller follows several architectural principles.

## Single Responsibility

All business decisions are implemented in one place.

---

## Stateless Logic

Business decisions are derived from the current Runtime and Scene Mappings.

The Controller itself stores no persistent state.

---

## Clear Separation

Configuration, Runtime and business logic remain independent.

---

# Future Extensions

The current Controller architecture allows future enhancements including:

- Additional trigger modes
- Extended LED behaviour
- Diagnostics
- Additional validation
- Advanced scene activation strategies

---

# Summary

The Controller is the central decision-making component of KNX Scene Cycler.

It coordinates Scene Mappings, Runtime updates and Home Assistant scene activation while keeping business logic separate from configuration and runtime state.
