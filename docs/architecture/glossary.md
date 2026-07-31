# Glossary

This glossary defines the official terminology used throughout the KNX Scene Cycler project.

The definitions in this document are authoritative and should be used consistently across the documentation, source code, comments and future user documentation.

---

## Config Flow

The Home Assistant user interface responsible for collecting, validating and storing the persistent configuration of the integration.

---

## Controller

The component responsible for all business logic.

The Controller processes user interactions, evaluates Trigger Modes, activates Home Assistant scenes and updates the Runtime.

---

## Hub

The central integration component.

The Hub owns all configured Scene Buttons and coordinates their lifecycle within Home Assistant.

---

## KNX Scene Number

A KNX scene number transmitted by a compatible KNX device.

Within KNX Scene Cycler, scene numbers are used to select the corresponding Scene Mapping.

---

## Neutral Mapping

A special Scene Mapping representing the neutral state.

Unlike a Regular Mapping, a Neutral Mapping has no KNX Scene Number and is activated only through the configured Trigger Mode.

---

## Regular Mapping

A Scene Mapping representing a normal selectable Home Assistant scene.

Regular Mappings are directly associated with KNX Scene Numbers.

---

## Runtime

The dynamic operational state of a configured Scene Button.

The Runtime stores only information that changes while the integration is running.

---

## Scene Button

A logical representation of one configured KNX scene button.

Each Scene Button owns its own Scene Mappings, Runtime and Controller.

---

## Scene Mapping

The central configuration concept of KNX Scene Cycler.

A Scene Mapping defines the relationship between a KNX Scene Number and a Home Assistant scene while remaining independent from Runtime state and business logic.

---

## Trigger Mode

The interaction model used to interpret incoming KNX events.

Trigger Modes determine when a Scene Mapping becomes active.

---

# Terminology Rules

To maintain a consistent architecture and documentation, the following terminology rules apply:

- Use **Scene Mapping** instead of *Scene Model* or *Mapping Model*.
- Use **Runtime** instead of *State Model*.
- Use **Controller** instead of *Logic* or *Business Layer*.
- Use **Trigger Mode** instead of *Operating Mode* or *Interaction Mode*.
- Use **Regular Mapping** and **Neutral Mapping** consistently.
- Avoid introducing synonyms for the defined terms.

These terms form the common language of the KNX Scene Cycler architecture and should be used consistently throughout the project.