# KNX Scene Cycler for Home Assistant

> [!WARNING]
> **Early Development**
>
> KNX Scene Cycler is currently under active development.
>
> The original proof-of-concept is being refactored into a scalable multi-button architecture. Until this work is completed, interfaces, configuration and internal implementation may change.

## Overview

KNX Scene Cycler is a custom Home Assistant integration that connects KNX scene buttons with Home Assistant scenes.

Instead of implementing automation logic inside ETS, the integration allows KNX buttons to control Home Assistant scenes while maintaining a clean separation between KNX communication, runtime state and business logic.

The long-term goal is to support multiple independent KNX scene buttons within a single integration instance.

---

## Planned Features

- Multiple independent KNX scene buttons
- Four configurable Home Assistant scenes per button
- Dedicated neutral scene
- Short press scene selection
- Long press toggle (neutral ↔ last active scene)
- Optional KNX status LED feedback
- Home Assistant Switch entity
- Home Assistant Select entity
- Runtime state restoration
- Modern Config Flow
- Scalable multi-button architecture

---

## Architecture

The integration follows a layered architecture.

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

Design goals:

- clear separation of responsibilities
- scalable architecture
- maintainable codebase
- predictable runtime behaviour
- Home Assistant best practices

Business logic is implemented exclusively inside the controller layer.

---

## Current Development Status

### Completed

- Architecture design
- Typed configuration models
- Runtime model
- Controller layer
- Multi-button hub
- Project documentation

### In Progress

- Home Assistant integration migration
- Multi-button runtime integration
- Platform migration
- KNX event routing

### Planned

- Config Flow redesign
- Runtime restoration
- Automated tests
- Documentation expansion
- First public beta

---

## Documentation

Additional documentation can be found in the `docs` directory.

| Document | Description |
|----------|-------------|
| `ARCHITECTURE.md` | Overall software architecture |
| `DESIGN.md` | Design decisions and architectural principles |
| `CONTROLLER.md` | Controller responsibilities |
| `ROADMAP.md` | Planned project milestones |
| `TODO.md` | Current implementation tasks |
| `CHANGELOG.md` | Project history |

---

## Development Workflow

Development follows an incremental migration strategy.

Each architectural change is

1. implemented,
2. deployed to Home Assistant,
3. configuration checked,
4. tested,
5. committed,
6. pushed to GitHub.

This minimizes regression risk while allowing the architecture to evolve continuously.

---

## Repository Structure

```text
custom_components/
└── knx_scene_cycler/

docs/
├── ARCHITECTURE.md
├── CHANGELOG.md
├── CONTROLLER.md
├── DESIGN.md
├── ROADMAP.md
└── TODO.md
```

---

## Supported Platform

- Home Assistant (Custom Integration)
- KNX
- Home Assistant Scenes

---

## License

This project is licensed under the MIT License.

See the `LICENSE` file for details.