# Scene Mapping

Part of the KNX Scene Cycler Architecture Documentation.

Related documents:

- Architecture Overview
- Runtime
- Controller
- Trigger Modes

---

# Purpose

Scene Mapping is the central concept of KNX Scene Cycler.

It defines the relationship between KNX scene numbers and Home Assistant scenes without requiring changes to the ETS project.

Instead of binding KNX scene numbers directly to automation logic, KNX Scene Cycler introduces a configurable mapping layer that can be modified entirely from within Home Assistant.

---

# Concept

A Scene Mapping associates a KNX scene number with exactly one Home Assistant scene.

Additionally, it stores all information required for scene activation and optional status LED handling.

The Scene Mapping itself is static configuration.

It never contains runtime information.

---

# Responsibilities

A Scene Mapping is responsible for defining:

- KNX scene number
- Home Assistant scene entity
- Mapping type
- Optional LED value
- User-visible mapping name

It is **not** responsible for:

- Current active scene
- Previously active scene
- Runtime state
- Trigger processing
- KNX communication

Those responsibilities belong to the Runtime and Controller.

---

# Mapping Types

The current architecture defines two mapping types.

## Regular Mapping

Represents a normal selectable scene.

Regular mappings are activated directly through KNX scene numbers and can become the current active scene.

---

## Neutral Mapping

Represents the neutral state.

The neutral mapping intentionally has no KNX scene number.

It is activated only through the configured trigger mode and allows temporarily leaving the currently active regular scene while preserving it for later restoration.

---

# Design Principles

The Scene Mapping model follows several design principles.

## Immutable Configuration

Scene mappings represent persistent configuration.

Runtime changes never modify the mapping itself.

---

## Runtime Independence

Runtime information is intentionally stored elsewhere.

This separation keeps configuration stable while runtime changes continuously.

---

## KNX Independence

Scene mappings describe logical relationships.

They do not communicate with the KNX bus directly.

---

## Controller Independence

Scene mappings contain data only.

All business decisions are implemented inside the controller.

---

# Scene Mapping Lifecycle

Scene mappings are created during the Home Assistant configuration process.

Once created they remain unchanged until the user edits the configuration.

During normal operation the controller only reads Scene Mappings.

Runtime information is stored separately.

---

# Future Extensions

The current model was intentionally designed to support future extensions without changing its overall structure.

Possible future enhancements include:

- Additional mapping types
- Extended LED behaviour
- Mapping metadata
- Import and export of mappings

---

# Summary

Scene Mapping is the central configuration model of KNX Scene Cycler.

It separates persistent scene configuration from runtime state and business logic, providing a flexible and scalable foundation for the entire integration.
