# Changelog

All notable changes to this project will be documented in this file.

This project follows the principles of
[Keep a Changelog](https://keepachangelog.com/)
and adheres to Semantic Versioning.

---

# [Unreleased]

## Added

- Editing of existing Scene Buttons through the Options Flow
- Selection of the Scene Button to edit
- German and English Config Flow translations
- Trigger-Mode-specific scene number validation

## Changed

- Add and Edit now reuse the same Button Configuration Flow
- Existing values are prefilled when editing a Scene Button
- Editing preserves the Button ID, button order and internal mapping metadata
- KNX scene numbers use numeric input fields instead of sliders
- Neutral Scene mode now assigns KNX scene number 1 implicitly to the Neutral
  Mapping
- Regular Scene Mappings in Neutral Scene mode are restricted to KNX scene
  numbers 2 through 64
- Invalid form values remain available for correction after validation errors
- Config Flow validation messages are presented as translated user-facing text

## Tested

- Complete Add and Edit flows in Home Assistant
- Trigger-Mode-specific input fields and scene number ranges
- Duplicate KNX scene number validation
- Physical KNX scene selection and neutral activation
- Home Assistant Select and Switch entity behaviour
- Integration reload and Home Assistant restart behaviour

## Planned

- Removing Scene Buttons
- Cloning Scene Buttons
- Additional trigger modes
- Extended LED functionality
- Improved user experience
- Documentation expansion

---

# [0.2.0] - 2026-07-XX

## Architecture Refactoring Complete

This release introduces the new Scene Mapping architecture, replacing the original slot-based design with a modular and scalable implementation.

The new architecture provides the foundation for future development, including additional trigger modes, improved runtime handling and support for multiple independent scene buttons.

### Added

- New Scene Mapping architecture
- Scene Mapping model
- Runtime model
- Multi-button architecture
- Modern Home Assistant Config Flow
- Configurable Scene Mapping
- Neutral scene support
- Home Assistant Select entity
- Home Assistant Switch entity
- Optional KNX status LED support
- Modular controller architecture

### Changed

- Complete internal architecture redesign
- Simplified configuration model
- Internal scene numbering standardized to KNX scene numbers (1–64)
- Improved runtime state handling
- Improved separation between controller, runtime and KNX communication
- Repository structure reorganized
- Documentation restructured

### Removed

- Legacy slot-based architecture
- Slot model
- Legacy runtime implementation

---

# [0.1.0] - 2026-XX-XX

## Proof of Concept

Initial proof-of-concept implementation of KNX Scene Cycler.

### Added

- Initial KNX scene button support
- Basic scene cycling
- Home Assistant scene activation
- Initial Config Flow
- Initial runtime implementation
