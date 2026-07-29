# Roadmap

This roadmap describes the long-term development plan for the KNX Scene Cycler integration.

Unlike `TODO.md`, which tracks the current implementation work, this document focuses on project milestones and planned releases.

---

# Vision

Develop a modern Home Assistant integration for KNX scene buttons that

- supports multiple independent scene buttons within one logical device,
- follows Home Assistant integration best practices,
- separates configuration, runtime state and business logic,
- provides a scalable architecture,
- remains easy to maintain and extend.

The long-term objective is to replace the original prototype with a clean, fully scalable implementation.

---

# Guiding Principles

The project follows these architectural principles:

- One logical Home Assistant device represents one KNX Scene Cycler hub.
- One hub can contain any number of independent scene buttons.
- Every scene button owns its own configuration, runtime state and controller.
- Business logic exists exclusively inside the controller.
- Platform entities (Switch, Select) never implement business logic.
- KNX communication is isolated from business decisions.
- Configuration models are immutable.
- Runtime state is mutable.
- All architectural changes are introduced in small, testable steps.

---

# Release Plan

## v0.1 – Prototype

Status:

- Completed

Features:

- Initial working prototype
- Single scene button
- Home Assistant scenes
- Toggle functionality
- KNX communication
- Proof of concept

---

## v0.2 – Architecture Refactoring

Status:

- In Progress

Objectives:

- Introduce scalable architecture
- Typed configuration models
- Runtime model
- Controller layer
- Multi-button hub
- Replace prototype incrementally
- Preserve compatibility during migration

Current progress:

- Architecture completed
- Configuration models completed
- Runtime completed
- Controller completed
- Hub completed

Remaining work:

- Integrate the hub into Home Assistant setup
- Migrate Switch platform
- Migrate Select platform
- Migrate KNX routing
- Remove prototype implementation

---

## v0.3 – Multi-Button Support

Status:

- Planned

Objectives:

- Multiple independent scene buttons
- Shared Home Assistant device
- Shared configuration entry
- Shared KNX hub
- Stable device registry support
- Dynamic entity creation

---

## v0.4 – Configuration Improvements

Status:

- Planned

Objectives:

- New multi-button Config Flow
- Button editing
- Button removal
- Configuration validation
- Config-entry migration
- Reconfigure support

---

## v0.5 – Reliability

Status:

- Planned

Objectives:

- Runtime restoration
- Robust error handling
- Improved logging
- KNX listener lifecycle
- LED synchronization
- Automated tests

---

## v0.6 – Documentation

Status:

- Planned

Objectives:

- Complete developer documentation
- User documentation
- Installation guide
- Configuration guide
- Architecture guide
- API documentation

---

## v1.0 – First Stable Release

Status:

- Planned

Objectives:

- Stable API
- Complete documentation
- Automated test suite
- Full multi-button support
- Config-entry migration
- Production-ready architecture

---

# Future Ideas

Potential future enhancements beyond version 1.0:

- Blueprint import
- Scene templates
- Scene groups
- Diagnostics support
- Repair flows
- Backup and restore
- KNX status synchronization
- Additional entity platforms
- Device actions
- Device triggers
- Translation support
- Integration Quality Scale improvements

---

# Development Strategy

The project intentionally follows an incremental migration strategy.

Instead of replacing the original prototype all at once, every architectural component is introduced independently, tested, committed and deployed before continuing with the next step.

This approach minimizes regression risk while allowing the architecture to evolve in a controlled manner.