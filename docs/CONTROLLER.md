# Controller

This document describes the public responsibilities of the `SceneButtonController`.

The controller is the central component of the integration.

It owns all business logic for one configured KNX scene button.

---

# Responsibilities

The controller is responsible for:

- activating Home Assistant scenes,
- activating the neutral scene,
- handling toggle requests,
- processing KNX scene numbers,
- updating runtime state,
- restoring runtime state,
- coordinating status LED updates,
- isolating business logic from Home Assistant entities.

The controller intentionally does **not** own configuration persistence or KNX communication.

---

# Architecture

```text
                Switch
                   │
                   │
                Select
                   │
                   │
              KNX Listener
                   │
                   ▼
        SceneButtonController
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
SceneButtonRuntime     Home Assistant
                           Scene Service
```

Every user interaction passes through the controller.

This guarantees identical behavior regardless of whether the action originates from Home Assistant or from KNX.

---

# Public Interface

## activate_scene(slot)

Activates one configured regular scene.

Responsibilities:

- validate the slot,
- resolve the configured mapping,
- activate the Home Assistant scene,
- update the runtime,
- keep the last active regular scene.

---

## activate_neutral()

Activates the configured neutral scene.

Responsibilities:

- activate the neutral Home Assistant scene,
- update runtime state,
- preserve the last active regular scene,
- switch the controller into the inactive state.

---

## toggle()

Implements the KNX long-press behavior.

If a regular scene is active:

```text
Regular Scene
      │
      ▼
Neutral Scene
```

If the controller is inactive:

```text
Inactive
    │
    ▼
Restore Last Regular Scene
```

If no previous scene exists, Scene Slot 1 is restored.

---

## handle_knx_scene_number(scene_number)

Processes incoming KNX scene numbers.

Responsibilities:

- resolve the configured mapping,
- ignore unmapped values,
- activate the matching regular scene.

---

## restore_state()

Restores runtime information after Home Assistant startup.

The exact restoration strategy is defined separately from scene activation.

The controller should restore internal state without causing unnecessary scene activations.

---

## shutdown()

Performs controller shutdown.

Responsibilities:

- release resources,
- prepare runtime for unloading,
- support clean config-entry removal.

---

# Runtime Ownership

Each controller owns exactly one runtime instance.

```text
SceneButtonController
          │
          ▼
SceneButtonRuntime
```

The runtime is never shared between controllers.

---

# Configuration Ownership

Each controller owns exactly one immutable configuration.

```text
SceneButtonController
          │
          ▼
SceneButtonConfig
```

The controller never modifies its configuration.

---

# Design Principles

The controller follows these design principles:

- one responsibility,
- deterministic behavior,
- no duplicated logic,
- no UI-specific decisions,
- no Home Assistant entity logic,
- no KNX transport logic,
- predictable state transitions,
- testable public API.

---

# Future Responsibilities

As the integration evolves, additional responsibilities may be delegated to the controller, including:

- status LED synchronization,
- runtime restoration,
- diagnostics,
- repair actions,
- telemetry,
- advanced validation.

The controller should remain the single entry point for all business decisions related to one configured scene button.