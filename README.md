# KNX Scene Cycler

*A configurable mapping layer for Home Assistant scenes using existing KNX scene buttons.*

> [!NOTE]
> **Current Status**
>
> **Version:** v0.2.0
>
> **Architecture Refactoring Complete**
>
> The new Scene Mapping architecture is complete and serves as the foundation for future development.
>
> Current development focuses on feature completion, testing and documentation.

---

# Why this project exists

Many KNX installations already use high-quality wall-mounted push-buttons for scene control.

This project originated from a real-world installation using numerous **MDT Glass Push-button II Smart** devices.

As Home Assistant became more capable, the number of automations and scenes continued to grow. Reassigning KNX buttons in ETS whenever a Home Assistant scene changed quickly became cumbersome.

KNX Scene Cycler introduces a configurable **Scene Mapping Layer** between KNX and Home Assistant.

Once a KNX button has been configured in ETS to send scene numbers, all scene mapping is managed in Home Assistant. No further ETS changes are required.

The KNX installation remains stable while Home Assistant scenes can evolve independently.

---

# What is a Scene Mapping Layer?

Instead of assigning Home Assistant scenes directly inside the ETS project, KNX Scene Cycler acts as a configurable mapping layer between KNX scene numbers and Home Assistant scenes.

```text
ETS Project
      │
      ▼
 KNX Scene Number
      │
      ▼
KNX Scene Cycler
(Scene Mapping Layer)
      │
      ▼
Home Assistant Scene
```

This approach separates the stable KNX installation from the more dynamic Home Assistant environment.

Changing, replacing or extending Home Assistant scenes no longer requires modifications to the ETS project.

---

# Features

Current functionality includes:

- Configurable mapping between KNX scene numbers and Home Assistant scenes
- Multiple independent KNX scene buttons
- Scene cycling with configurable neutral state
- Return to the previously active scene
- Optional KNX status LED feedback
- Home Assistant Config Flow
- Home Assistant Select entity
- Home Assistant Switch entity
- Runtime state management
- Scalable multi-button architecture

---

# Reference Installation

The current reference implementation is developed and tested using:

- MDT Glass Push-button II Smart
- KNX
- Home Assistant

Support for additional KNX devices is expected where compatible scene telegrams are available, but has not yet been verified.

---

# Architecture

The integration follows a modular architecture consisting of independent components:

- Config Flow
- Hub
- Controller
- Runtime
- Scene Mapping Model

This separation keeps KNX communication, runtime state and business logic independent while providing a scalable foundation for future extensions.

Further architectural details are available in the documentation.

---

# Documentation

Additional documentation can be found in the `docs` directory.

## Architecture

- Architecture Overview
- Config Flow
- Controller
- Runtime
- Scene Mapping
- Trigger Modes

## Project

- ROADMAP.md
- TODO.md
- CHANGELOG.md

---

# Development Status

## Completed

- New Scene Mapping architecture
- Multi-button architecture
- Runtime model
- Controller
- Config Flow
- Entity platforms
- Project restructuring

## Currently in Progress

- Feature completion
- Documentation
- Testing
- User experience improvements

---

# Project Vision

KNX Scene Cycler does not replace KNX.

Instead, it extends an existing KNX installation with a flexible mapping layer for Home Assistant scenes while preserving the stability of the ETS project.

The long-term goal is to provide an elegant way to integrate Home Assistant scenes into existing KNX installations without repeatedly modifying the ETS project.

---

# License

This project is licensed under the MIT License.

See the `LICENSE` file for details.
