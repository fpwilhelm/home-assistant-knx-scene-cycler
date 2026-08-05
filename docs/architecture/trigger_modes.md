# Trigger Modes

Part of the KNX Scene Cycler Architecture Documentation.

Related documents:

- Architecture Overview
- Scene Mapping
- Runtime
- Controller

---

# Purpose

Trigger Modes define how user interactions are interpreted by the Controller.

They determine how incoming KNX events are translated into Scene Mapping activations.

By separating trigger behaviour from Scene Mappings, the architecture allows different interaction models while keeping the configuration model unchanged.

---

# Design Principle

A Trigger Mode defines **when** a Scene Mapping is activated.

A Scene Mapping defines **what** is activated.

This separation keeps interaction logic independent from configuration.

---

# Current Trigger Modes

The current implementation supports two trigger modes.

## Separate Toggle

The scene selection group address is used exclusively for selecting regular scenes.

A dedicated toggle group address switches between the currently active regular scene and the configured neutral scene.

The Neutral Mapping has no KNX scene number in this mode. Regular Scene
Mappings may use the complete supported range from 1 through 64.

This mode provides the clearest separation between scene selection and toggle behaviour.

---

## Neutral Scene

The neutral scene is represented by a dedicated Scene Mapping with KNX scene
number 1. This value is fixed by the integration and is not configured by the
user.

KNX scene number 1 is reserved for the Neutral Mapping in this mode. Regular
Scene Mappings therefore use scene numbers 2 through 64.

Scene number 1 acts as a toggle:

- If a regular scene is active, scene number 1 activates the Neutral Mapping.
- If the Neutral Mapping is already active, scene number 1 restores the last
  active regular Scene Mapping.
- If no event has established the Runtime state after startup, the first scene
  number 1 telegram activates the Neutral Mapping.

While the Neutral Mapping is active, the first received regular scene telegram
also restores the last active regular Scene Mapping instead of activating the
received mapping. This makes a short physical button press behave like
"resume": it returns from neutral to the previous scene. The integration then
sends the restored KNX scene number as feedback so that a compatible physical
button continues its cycle after that scene.

The currently active regular Scene Mapping is preserved by the Runtime while
neutral is active.

After restoring the last regular scene, the integration sends that scene
number to the configured scene selection group address. Physical KNX buttons
with a status object on that address can use the feedback to synchronize their
internal scene cycle.

The integration ignores its own outgoing feedback event. Only incoming
GroupValueWrite telegrams are interpreted as physical button input.

The Neutral Mapping therefore behaves as a temporary toggle state rather than
a regular selectable scene.

---

# Controller Interaction

Incoming KNX events are processed by the Controller.

The Controller evaluates the configured Trigger Mode before selecting the appropriate Scene Mapping.

This keeps all interaction logic centralized in a single component.

---

# Extensibility

Trigger Modes are intentionally independent from Scene Mappings.

Additional interaction models can therefore be introduced without changing the configuration model or Runtime architecture.

Possible future Trigger Modes include:

- Long-press activation
- Double-press activation
- Cycling modes
- Custom interaction strategies

---

# Summary

Trigger Modes define how user interactions are interpreted.

They separate interaction behaviour from scene configuration and provide a flexible foundation for future extensions without affecting the overall architecture.
