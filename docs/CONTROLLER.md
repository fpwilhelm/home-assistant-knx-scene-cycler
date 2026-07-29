cat > docs/CONTROLLER.md <<'EOF'
# Controller

This document describes the public responsibilities of the `SceneButtonController`.

The controller is the central business-logic component for one configured KNX scene button.

It coordinates Home Assistant scene activation and updates the associated runtime state.

---

# Responsibilities

The controller is responsible for:

- activating configured Home Assistant scenes,
- activating the configured neutral scene,
- handling toggle requests,
- processing KNX scene numbers,
- updating runtime state,
- preserving the last active regular scene,
- isolating business logic from Home Assistant entities,
- exposing a consistent interface for KNX and Home Assistant actions.

The controller intentionally does **not** own:

- configuration persistence,
- Config Flow logic,
- KNX telegram registration,
- KNX transport,
- Home Assistant entity presentation,
- persistent runtime restoration.

---

# Architecture

```text
             Home Assistant Entities
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