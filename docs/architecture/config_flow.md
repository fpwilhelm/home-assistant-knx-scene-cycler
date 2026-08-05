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
- Neutral Scene Mapping
- Between one and four Regular Scene Mappings

The resulting configuration is stored as persistent Home Assistant Config Entry data.

---

# Validation

Before the configuration is stored, the Config Flow validates:

- KNX group address format
- Home Assistant scene entities
- Required configuration values

KNX scene numbers are entered as integer values and are restricted to the
supported range from 1 through 64.

Invalid configurations are rejected before becoming part of the persistent configuration.

The form proposes four regular mapping rows. Only rows with a selected Home
Assistant scene entity are stored. Unused rows are omitted from the persistent
configuration and therefore do not participate in scene selection or
last-scene restoration. At least one regular mapping is required.

Using the same Home Assistant scene entity in more than one mapping is valid.
KNX scene numbers must remain unique within one Scene Button because identical
KNX telegrams do not identify which repeated mapping position was intended.
This also keeps per-mapping runtime state and future LED color feedback
deterministic after restarts or missed telegrams.

---

# Trigger-Mode-Specific Scene Number Rules

The available KNX scene numbers depend on the selected Trigger Mode.

## Separate Toggle

- Regular Scene Mappings may use KNX scene numbers 1 through 64.
- The Neutral Mapping has no KNX scene number because neutral activation uses
  the separate toggle group address.

## Neutral Scene

- KNX scene number 1 is reserved for the Neutral Mapping.
- The Neutral Mapping uses scene number 1 automatically; the Config Flow does
  not ask the user to enter it.
- Regular Scene Mappings may use KNX scene numbers 2 through 64.
- The Config Flow explains that scene number 1 is reserved in this Trigger
  Mode.

This reservation is required because KNX scene number 1 and raw KNX scene
value 0 represent the same DPT 17.001 telegram. A regular and a neutral mapping
on the same group address therefore cannot both use scene number 1
unambiguously.

---

# Configuration Lifecycle

The Config Flow is executed when:

- A new integration is created
- An existing configuration is modified

After successful validation, the configuration is stored by Home Assistant.

During startup, the integration recreates its internal architecture from this stored configuration.

---

# Scene Button Management

Existing Config Entries manage their Scene Buttons through the Options Flow.

The user first chooses an operation:

- Add Scene Button
- Edit Scene Button
- Remove Scene Button
- Finish

Editing requires selecting an existing Scene Button. The stored
`SceneButtonConfig` is then converted into form data and used to prefill the
same Button Configuration Flow that is used when adding a Scene Button.

```text
Manage Scene Buttons
        │
        ├── Add Scene Button
        │
        ├── Edit Scene Button
        │       │
        │       └── Select Scene Button
        │
        ├── Remove Scene Button
        │       │
        │       ├── Select Scene Button
        │       └── Confirm Removal
        │
        └── Finish
                │
                ▼
      Button Configuration Flow
                │
                ├── Trigger Mode
                ├── Group Addresses
                ├── Neutral Scene Mapping
                ├── Regular Scene Mappings
                └── Save
```

The selected operation determines only how the completed configuration is
stored:

- Add appends the new Scene Button.
- Edit replaces the selected Scene Button while preserving its stable Button
  ID, its position in the stored list and mapping metadata that is not exposed
  by the current forms.
- Remove deletes the selected Scene Button while preserving the order of all
  remaining buttons. Its Switch and Select entity-registry entries are removed.
  Shared KNX input addresses remain registered while another Scene Button or
  Config Entry still uses them.

The final Scene Button cannot be removed through this operation. Removing the
entire Config Entry is the explicit way to remove the last Scene Button and its
Hub.

Manual HA/KNX verification covered deletion with two Scene Buttons sharing one
scene-selection address. Removing one button left the shared address registered
for the remaining button, removed only the deleted button's entities and
mappings, and allowed its released stable Button ID to be reused without an
entity-registry collision.

The shared Button Configuration Flow is intentionally independent from the
operation. This allows future operations such as Clone to reuse the same forms
without duplicating configuration logic.

---

# Relationship to the Architecture

The Config Flow creates the persistent configuration.

The Runtime represents the operational state.

The Controller processes events using the stored configuration together with the current Runtime.

This clear separation keeps configuration independent from system operation.

---

# Future Extensions

The Config Flow architecture allows future enhancements including:

- Cloning scene buttons
- Improved validation
- Additional Trigger Modes
- Migration support for future configuration versions

---

# Summary

The Config Flow provides the entry point for configuring KNX Scene Cycler.

It creates the persistent configuration that serves as the foundation for the Runtime, Controller and Scene Mapping architecture.
