# Design

This document explains the architectural design decisions behind the KNX Scene Cycler integration.

It focuses on *why* the integration is structured the way it is, rather than documenting individual implementation details.

---

# Design Goals

The integration is designed around the following primary goals:

- scalability
- maintainability
- separation of responsibilities
- predictable runtime behavior
- easy extensibility
- compliance with Home Assistant integration best practices

The architecture intentionally avoids embedding business logic directly inside Home Assistant entity classes.

---

# Overall Architecture

The integration is built in multiple layers.

```text
Config Entry
      │
      ▼
SceneButtonConfig
      │
      ▼
KNXSceneCyclerHub
      │
      ├── SceneButtonController
      │         │
      │         ▼
      │   SceneButtonRuntime
      │
      └── additional button controllers
```

Every layer has a single, well-defined responsibility.

---

# Why a Hub?

Although the original prototype supported only one KNX scene button, the long-term goal is to support any number of independent scene buttons within a single Home Assistant device.

The hub represents this logical device.

Its responsibilities are limited to:

- owning all configured buttons,
- creating controllers,
- providing controller lookup,
- coordinating startup,
- coordinating shutdown.

The hub intentionally contains no scene-selection logic.

---

# Why One Controller per Button?

Each physical KNX button behaves independently.

Therefore each button receives its own controller.

The controller owns all business logic, including:

- scene activation,
- neutral scene activation,
- toggle behavior,
- KNX event handling,
- runtime updates,
- state restoration.

No other component should make business decisions.

---

# Why Separate Runtime State?

Persistent configuration and runtime state have different lifecycles.

Configuration describes what the system should do.

Runtime describes what the system is currently doing.

Separating both models keeps the implementation easier to understand, easier to test and less error-prone.

---

# Why Immutable Configuration?

Configuration data is loaded from the Config Entry.

Once loaded, it should remain unchanged during normal operation.

Treating configuration as immutable prevents accidental runtime modifications and makes the controller behavior deterministic.

---

# Why Mutable Runtime?

Runtime values change continuously.

Examples include:

- current active scene,
- last active scene,
- availability,
- restoration state.

Keeping runtime isolated allows state transitions without modifying configuration objects.

---

# Why Slots Instead of Entity IDs?

The runtime stores only logical scene slots.

Example:

```text
Current Scene: Slot 2
```

instead of

```text
scene.living_room_evening
```

The controller translates slots into Home Assistant scene entities whenever activation is required.

This provides several advantages:

- runtime stays independent from Home Assistant entity names,
- scene mappings remain configurable,
- business logic remains simple,
- future migration becomes easier.

---

# Why No Business Logic in Entity Classes?

Home Assistant entities should expose state and forward user interaction.

They should not implement application logic.

Instead:

```text
Switch
Select
KNX Events
        │
        ▼
SceneButtonController
        │
        ▼
Runtime
```

This keeps all behavior consistent regardless of whether the action originates from Home Assistant or from KNX.

---

# Why Incremental Migration?

Replacing the original prototype in a single step would introduce unnecessary risk.

Instead, the architecture is migrated component by component.

Each completed component is:

1. implemented,
2. tested,
3. deployed,
4. verified,
5. committed,
6. pushed.

Only then does development continue.

This strategy minimizes regressions and keeps the integration functional throughout the refactoring process.

---

# Long-Term Vision

The architecture is intended to serve as a solid foundation for future features, including:

- multiple scene buttons,
- improved configuration flow,
- runtime restoration,
- diagnostics,
- repair flows,
- automated testing,
- additional entity platforms,
- future Home Assistant quality improvements.

The architecture should remain understandable, modular and easy to extend without requiring fundamental redesign.