# Runtime

Part of the KNX Scene Cycler Architecture Documentation.

Related documents:

- Architecture Overview
- Scene Mapping
- Controller

---

# Purpose

The Runtime represents the current operational state of a configured scene button.

Unlike the Scene Mapping, which contains persistent configuration, the Runtime stores dynamic information that changes while the integration is running.

The Runtime exists solely to represent the current state of the system.

---

# Responsibilities

The Runtime is responsible for storing:

- The currently active Scene Mapping
- The last active regular Scene Mapping
- The current button state

The Runtime is not responsible for:

- Scene configuration
- Business logic
- KNX communication
- Home Assistant service calls

Those responsibilities belong to the Controller.

---

# Runtime State

The Runtime changes continuously during operation.

Typical state changes include:

- Activation of a regular scene
- Activation of the neutral scene
- Restoration of the previous scene
- Home Assistant startup
- Home Assistant shutdown

The Runtime always reflects the current operational state.

---

# Separation from Configuration

A key design goal of the architecture is the strict separation between configuration and runtime state.

Scene Mappings describe what can happen.

The Runtime describes what is currently happening.

This separation simplifies maintenance and avoids unintended modification of persistent configuration.

---

# Runtime Lifecycle

A Runtime instance is created for every configured scene button.

During operation, the Controller updates the Runtime whenever the operational state changes.

Other components read Runtime information but do not modify it directly.

---

# Design Principles

The Runtime follows several design principles.

## Runtime Only

The Runtime contains no persistent configuration.

---

## Controller Managed

Only the Controller modifies Runtime data.

This guarantees that all state transitions follow the defined business rules.

---

## Lightweight

The Runtime stores only the information required during normal operation.

Configuration data remains inside the Scene Mapping model.

---

# Future Extensions

The Runtime model was intentionally designed to allow future extensions.

Possible additions include:

- Extended runtime diagnostics
- Timestamp of the last scene activation
- Activation statistics
- Additional runtime states

---

# Summary

The Runtime represents the current operational state of a configured scene button.

It intentionally separates dynamic state from persistent configuration and allows the Controller to manage all state transitions consistently.
