# TODO

This document tracks the current implementation work for the KNX Scene Cycler integration.

Long-term milestones belong in `ROADMAP.md`. User-facing changes belong in `CHANGELOG.md`.

---

## Current Development Status

The integration is being refactored from the original single-button prototype into a scalable multi-button architecture.

The new architecture has been implemented alongside the existing prototype. It is not yet connected to the active Home Assistant setup path.

Current branch:

```text
refactor/multi-button-architecture
```

Current integration structure:

```text
Config Entry
      │
      ▼
SceneButtonConfig
      │
      ▼
KNXSceneCyclerHub
      │
      ├── SceneButtonController
      │         │
      │         ▼
      │   SceneButtonRuntime
      │
      └── additional button controllers
```

---

## Completed

### Architecture

- [x] Define the scalable multi-button architecture.
- [x] Document the target architecture in `docs/architecture.md`.
- [x] Separate persistent configuration, runtime state and business logic.
- [x] Define one logical Home Assistant device as a hub containing multiple scene buttons.
- [x] Define one controller and one runtime instance per configured button.
- [x] Establish the controller as the only component responsible for business decisions.

### Constants and configuration models

- [x] Modernize `const.py`.
- [x] Add constants for hub and multi-button configuration.
- [x] Add scene-slot constants.
- [x] Add KNX scene-number limits.
- [x] Add KNX toggle and status LED values.
- [x] Retain legacy prototype constants during migration.
- [x] Add typed `SceneMapping` configuration model.
- [x] Add typed `SceneButtonConfig` configuration model.
- [x] Add dictionary conversion methods for stored config-entry data.
- [x] Add scene lookup by slot.
- [x] Add scene lookup by KNX scene number.
- [x] Add validation helpers for scene slots and KNX scene-number uniqueness.

### Runtime state

- [x] Add `ButtonState`.
- [x] Add `SceneButtonRuntime`.
- [x] Track the current regular scene slot.
- [x] Track the last active regular scene slot.
- [x] Represent the neutral state without a synthetic scene slot.
- [x] Add active, inactive, restoring and unavailable states.
- [x] Preserve the last active scene while the neutral scene is active.
- [x] Use Scene 1 as the default restore fallback.

### Controller

- [x] Add the public `SceneButtonController` interface.
- [x] Add regular scene activation by slot.
- [x] Add neutral scene activation.
- [x] Add toggle behavior.
- [x] Add KNX scene-number handling.
- [x] Ignore unmapped KNX scene numbers.
- [x] Activate Home Assistant scenes through `scene.turn_on`.
- [x] Update runtime state only after successful scene activation.
- [x] Add controller debug logging.
- [x] Add initial restore and shutdown interfaces.

### Multi-button hub

- [x] Add `KNXSceneCyclerHub`.
- [x] Create one runtime and controller per button configuration.
- [x] Store controllers by stable button ID.
- [x] Add controller lookup by button ID.
- [x] Add button registration and removal.
- [x] Add iteration over all controllers.
- [x] Add hub-level restore handling.
- [x] Add hub-level shutdown handling.

### Development workflow

- [x] Work on the dedicated refactoring branch.
- [x] Keep architectural changes in small commits.
- [x] Deploy each meaningful Python change to the Home Assistant host.
- [x] Run the Home Assistant configuration check after deployment.
- [x] Preserve the existing prototype until the replacement path is ready.
- [x] Push each completed refactoring step to GitHub.

---

## Current Task

### Integrate the hub into Home Assistant setup

- [ ] Review the current `__init__.py`.
- [ ] Parse stored config-entry data into typed button configurations.
- [ ] Create one `KNXSceneCyclerHub` during config-entry setup.
- [ ] Store the hub in the integration runtime data.
- [ ] Forward platform setup without migrating entity behavior yet.
- [ ] Shut down the hub during config-entry unload.
- [ ] Preserve compatibility with the current single-button config entry.
- [ ] Deploy the setup change.
- [ ] Restart Home Assistant.
- [ ] Check logs for `knx_scene_cycler` errors.
- [ ] Commit and push the setup migration separately.

---

## Next Implementation Steps

### Switch platform

- [ ] Create one switch entity per configured button.
- [ ] Resolve the button controller through the hub.
- [ ] Report ON when a regular scene is active.
- [ ] Turn ON by restoring the last active regular scene.
- [ ] Turn OFF by activating the neutral scene.
- [ ] Remove business logic from `switch.py`.
- [ ] Add stable unique IDs.
- [ ] Add shared device information for the hub.

### Select platform

- [ ] Create one select entity per configured button.
- [ ] Expose the four configured regular scene slots.
- [ ] Resolve the button controller through the hub.
- [ ] Activate scenes exclusively through the controller.
- [ ] Reflect the current regular scene selection.
- [ ] Preserve the last selected regular scene while neutral is active.
- [ ] Remove business logic from `select.py`.
- [ ] Add stable unique IDs.
- [ ] Add shared device information for the hub.

### KNX event routing

- [ ] Register one scene-selection listener per configured button.
- [ ] Register one toggle listener per configured button.
- [ ] Route incoming scene numbers to the correct controller.
- [ ] Route the configured toggle impulse to the correct controller.
- [ ] Ignore unrelated KNX telegrams.
- [ ] Validate the received toggle value.
- [ ] Prevent duplicate listener registration.
- [ ] Unregister all listeners during unload.
- [ ] Add useful debug logging for received telegrams.

### KNX status LED

- [ ] Send status LED value `1` after successful regular scene activation.
- [ ] Send status LED value `0` after successful neutral scene activation.
- [ ] Skip LED output when no LED group address is configured.
- [ ] Keep runtime and LED state consistent when a service call fails.
- [ ] Define behavior when KNX LED writing fails.
- [ ] Avoid duplicate LED writes where practical.

### Config Flow

- [ ] Redesign the config flow around one hub and multiple buttons.
- [ ] Add hub-name configuration.
- [ ] Add repeated button configuration.
- [ ] Generate stable button IDs.
- [ ] Configure scene-selection, toggle and optional status LED group addresses.
- [ ] Configure four regular scene mappings per button.
- [ ] Configure one neutral scene per button.
- [ ] Allow arbitrary KNX scene numbers from 1 to 64.
- [ ] Validate unique KNX scene numbers within each button.
- [ ] Validate unique button IDs.
- [ ] Validate required Home Assistant scene entities.
- [ ] Add button editing.
- [ ] Add button removal.
- [ ] Add reconfiguration support.
- [ ] Add config-entry migration from the prototype format.

### State restoration

- [ ] Define which runtime values are restored after restart.
- [ ] Restore the last active regular scene slot.
- [ ] Restore the active or neutral state where reliable.
- [ ] Define fallback behavior when no prior state exists.
- [ ] Define behavior when configured scenes were renamed or removed.
- [ ] Keep restored entity state consistent across Switch and Select.
- [ ] Avoid activating scenes automatically during startup unless explicitly required.

---

## Testing

### Unit tests

- [ ] Add tests for `SceneMapping.from_dict()`.
- [ ] Add tests for `SceneMapping.to_dict()`.
- [ ] Add tests for `SceneButtonConfig.from_dict()`.
- [ ] Add tests for `SceneButtonConfig.to_dict()`.
- [ ] Test scene lookup by slot.
- [ ] Test scene lookup by KNX scene number.
- [ ] Test missing mappings.
- [ ] Test duplicate KNX scene numbers.
- [ ] Test invalid scene slots.
- [ ] Test runtime activation.
- [ ] Test neutral-state handling.
- [ ] Test last-scene restoration.
- [ ] Test unavailable-state handling.
- [ ] Test controller toggle behavior.
- [ ] Test unmapped KNX scene numbers.
- [ ] Test scene-service failures.
- [ ] Test duplicate button IDs in the hub.
- [ ] Test unknown controller lookup.

### Home Assistant integration tests

- [ ] Test config-entry setup.
- [ ] Test config-entry unload.
- [ ] Test platform forwarding.
- [ ] Test Switch state and commands.
- [ ] Test Select state and commands.
- [ ] Test multiple buttons in one hub.
- [ ] Test scene activation service calls.
- [ ] Test KNX event routing.
- [ ] Test optional LED behavior.
- [ ] Test config-entry migration.

### Manual acceptance tests

- [ ] Short press activates the mapped Home Assistant scene.
- [ ] Arbitrary configured KNX scene numbers work.
- [ ] Long press while active activates the neutral scene.
- [ ] Long press while inactive restores the last active scene.
- [ ] Scene 1 is restored when no previous scene exists.
- [ ] Switch ON restores the last active scene.
- [ ] Switch OFF activates the neutral scene.
- [ ] Select activates the chosen regular scene.
- [ ] Regular scene activation switches the status LED on.
- [ ] Neutral scene activation switches the status LED off.
- [ ] Multiple buttons operate independently.
- [ ] Restarting Home Assistant does not mix button states.
- [ ] Reloading the config entry does not duplicate KNX listeners.

---

## Documentation

- [x] Add architecture documentation.
- [ ] Add project roadmap.
- [ ] Add changelog.
- [ ] Add design decisions.
- [ ] Add controller API documentation.
- [ ] Document KNX behavior and expected datapoint types.
- [ ] Document config-entry migration.
- [ ] Document installation and configuration.
- [ ] Document the multi-button user workflow.
- [ ] Document debugging and logging.
- [ ] Document the test strategy.
- [ ] Review the README before the first public release.

---

## Cleanup Before Stable Release

- [ ] Remove legacy constants after migration is complete.
- [ ] Remove the original prototype data model.
- [ ] Remove duplicated scene and toggle logic from platform files.
- [ ] Remove temporary migration helpers.
- [ ] Confirm all user-facing strings are ready for translation.
- [ ] Run formatting and linting.
- [ ] Run the complete automated test suite.
- [ ] Verify compatibility with the supported Home Assistant version.
- [ ] Review logging levels and messages.
- [ ] Review entity names and unique IDs.
- [ ] Review device registry behavior.
- [ ] Review config-entry migration paths.
- [ ] Complete release documentation.