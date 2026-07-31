# Changelog

All notable changes to this project will be documented in this file.

This project follows the principles of
[Keep a Changelog](https://keepachangelog.com/)
and adheres to Semantic Versioning.

---

# [Unreleased]

## Planned

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