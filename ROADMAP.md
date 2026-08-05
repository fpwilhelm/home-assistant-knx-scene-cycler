# Roadmap

## Vision

KNX Scene Cycler aims to provide a flexible Scene Mapping Layer between KNX and Home Assistant.

The project preserves the stability of an existing KNX installation while allowing Home Assistant scenes to evolve independently without repeatedly modifying the ETS project.

The long-term goal is a robust, scalable and user-friendly integration that supports multiple KNX scene buttons, flexible scene mappings and seamless Home Assistant integration.

---

## Development Roadmap

### v0.3.0 — Feature Completion

Complete the functionality introduced by the new architecture.

Planned topics include:

- Automatic registration of configured KNX group addresses
- Edit existing scene buttons
- Delete scene buttons
- Clone scene buttons as independent configurations
- Extended LED support
- Improved configuration flow
- User interface improvements
- Additional testing

---

### v0.4.0 — Documentation & User Experience

Improve usability and documentation.

Planned topics include:

- Complete architecture documentation
- Installation guide
- User guide
- Example configurations
- Screenshots
- Better diagnostics and logging

---

### v0.5.0 — Integration Maturity

Prepare the integration for wider adoption.

Planned topics include:

- Performance improvements
- Configuration migration support
- Additional trigger modes
- Improved error handling
- Compatibility testing with additional KNX devices

---

### Post-v0.5.0 — Synchronized Scene Control

Allow multiple physical KNX buttons with different group addresses or local
KNX scene numbers to control one shared logical set of Home Assistant scenes.

Planned development order:

1. Document the synchronization-group concept and data model.
2. Introduce shared logical Scene Mappings and shared Runtime state.
3. Allow existing independent Scene Buttons to join a synchronization group.

A synchronization group shares logical scene identities, the last active
regular scene and the active/neutral state. Each physical button binding keeps
its own KNX group addresses, local KNX scene numbers and status LED address.
This avoids coupling synchronization to identical ETS programming.

---

### v1.0.0 — First Public Release

Goals:

- Stable feature set
- Complete documentation
- Extensive testing
- HACS-ready repository
- Production-ready architecture
- First official public release

---

## Long-Term Vision

Future development may include:

- Additional trigger modes
- Advanced LED feedback
- Enhanced scene management
- Shared logical Scene Mappings
- Synchronization groups for multiple physical KNX buttons
- Import and export of scene mappings
- Additional KNX device compatibility
- Further Home Assistant integration improvements

The roadmap represents the current development direction and may evolve as the project grows.
