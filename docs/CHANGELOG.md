# Changelog

All notable changes to this project will be documented in this file.

The format is based on **Keep a Changelog**, and this project aims to follow **Semantic Versioning**.

---

## [Unreleased]

### Added

- Introduced a scalable multi-button architecture.
- Added typed configuration models (`SceneMapping` and `SceneButtonConfig`).
- Added dedicated runtime state management (`SceneButtonRuntime`).
- Added `ButtonState` runtime enumeration.
- Added the `SceneButtonController` abstraction.
- Added a central `KNXSceneCyclerHub`.
- Added typed constants for the new architecture.
- Added architecture documentation.
- Added project roadmap.
- Added project TODO tracking.
- Added controller documentation.
- Added design documentation.

### Changed

- Started the migration from the original single-button prototype to a scalable architecture.
- Separated configuration, runtime state and business logic.
- Refactored scene activation into the controller layer.
- Introduced one controller and one runtime instance per configured scene button.
- Introduced a hub-based architecture for future multi-button support.

### Fixed

- Improved validation of scene mappings.
- Improved runtime consistency after successful scene activation.

---

## [0.1.0]

Initial prototype release.

### Added

- Initial Home Assistant integration.
- KNX scene selection support.
- Home Assistant scene activation.
- Toggle functionality.
- Optional KNX status LED support.
- Switch entity.
- Select entity.
- Configuration flow.
- Initial documentation.