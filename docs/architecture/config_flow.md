# Config Flow

Part of the KNX Scene Cycler Architecture Documentation.

Related documents:

- Architecture Overview
- Scene Mapping
- Runtime
- Controller
- Trigger Modes

---

# Purpose

The Config Flow provides the user interface for configuring KNX Scene Cycler within Home Assistant.

Its primary responsibility is to collect, validate and persist the configuration required by the integration.

The Config Flow creates the persistent configuration from which all runtime components are later initialized.

---

# Responsibilities

The Config Flow is responsible for:

- Collecting user configuration
- Validating configuration data
- Creating Scene Mappings
- Storing persistent configuration
- Supporting configuration updates

The Config Flow is not responsible for:

- Runtime state
- Scene activation
- KNX communication
- Business logic

Those responsibilities belong to other architectural components.

---

# Configuration Model

The user configures one scene button by defining:

- Button name
- Scene selection group address
- Toggle group address
- Optional status LED group address
- Regular Scene Mappings
- Neutral Scene Mapping

The resulting configuration is stored as persistent Home Assistant Config Entry data.

---

# Validation

Before the configuration is stored, the Config Flow validates:

- KNX group address format
- Home Assistant scene entities
- Unique KNX scene numbers
- Required configuration values

Invalid configurations are rejected before becoming part of the persistent configuration.

---

# Configuration Lifecycle

The Config Flow is executed when:

- A new integration is created
- An existing configuration is modified

After successful validation, the configuration is stored by Home Assistant.

During startup, the integration recreates its internal architecture from this stored configuration.

---

# Relationship to the Architecture

The Config Flow creates the persistent configuration.

The Runtime represents the operational state.

The Controller processes events using the stored configuration together with the current Runtime.

This clear separation keeps configuration independent from system operation.

---

# Future Extensions

The Config Flow architecture allows future enhancements including:

- Editing existing scene buttons
- Removing scene buttons
- Improved validation
- Additional Trigger Modes
- Migration support for future configuration versions

---

# Summary

The Config Flow provides the entry point for configuring KNX Scene Cycler.

It creates the persistent configuration that serves as the foundation for the Runtime, Controller and Scene Mapping architecture.
