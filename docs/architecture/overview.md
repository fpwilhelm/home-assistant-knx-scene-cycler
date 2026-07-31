Part of the KNX Scene Cycler Architecture Documentation.

Related documents:

- Architecture Overview
- Scene Mapping
- Controller

# Architecture Overview

## Purpose

KNX Scene Cycler provides a configurable Scene Mapping Layer between KNX and Home Assistant.

Its primary goal is to preserve the stability of an existing KNX installation while allowing Home Assistant scene assignments to evolve independently.

The integration separates KNX communication, scene mapping and runtime state into independent components to provide a scalable and maintainable architecture.

---

## Design Goals

The architecture was designed around the following principles:

- Clear separation of responsibilities
- Scalable multi-button support
- Runtime independent from configuration
- Centralized business logic
- Modern Home Assistant integration
- Future extensibility

---

## High-Level Architecture

```text
                Home Assistant
                       │
               Config Entry
                       │
                       ▼
             KNXSceneCyclerHub
                       │
         ┌─────────────┴─────────────┐
         │                           │
         ▼                           ▼
SceneButtonController        SceneButtonController
         │                           │
         ▼                           ▼
 SceneButtonRuntime          SceneButtonRuntime
         │                           │
         ▼                           ▼
     Scene Mapping             Scene Mapping
         │                           │
         └─────────────┬─────────────┘
                       ▼
                     KNX Bus
```

Each configured scene button is represented by its own independent controller and runtime.

The hub coordinates all configured buttons and acts as the integration entry point.

---

## Core Components

### Config Flow

Creates and validates the user configuration.

---

### Hub

The central integration component.

It owns all configured scene buttons and coordinates their lifecycle.

---

### Controller

Contains all business logic.

The controller is responsible for processing KNX events, activating Home Assistant scenes and updating the runtime state.

---

### Runtime

Represents the current runtime state of a scene button.

Runtime data is intentionally separated from the persistent configuration.

---

### Scene Mapping

Defines the relationship between KNX scene numbers and Home Assistant scenes.

Scene mappings are configured by the user and remain independent from runtime state.

---

## Runtime Model

Configuration, runtime state and controller logic are intentionally separated.

This separation improves maintainability and allows future extensions without affecting existing components.

---

## Trigger Modes

The architecture supports multiple trigger modes.

The current implementation includes:

- Separate Toggle
- Neutral Scene

Additional trigger modes can be added without changing the overall architecture.

---

## Extensibility

The modular architecture allows future extensions including:

- Additional trigger modes
- Advanced LED behaviour
- Additional scene mapping strategies
- Extended Home Assistant functionality

---

## Related Documents

- Config Flow
- Scene Mapping
- Runtime
- Controller
- Trigger Modes
