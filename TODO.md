# TODO

This document tracks the current implementation work for KNX Scene Cycler.

Long-term project goals are documented in `ROADMAP.md`.

Released functionality is documented in `CHANGELOG.md`.

---

# Current Focus (v0.3.0)

## Development Handoff (2026-08-02)

- Automatic GA registration is implemented; the basic HA test without KNX YAML passed.
- The serialized Neutral-scene restore/feedback fix passed the manual HA/KNX regression test: regular scene cycling, neutral activation, restoration of the previous regular scene and continuation with the next scene all behave correctly.
- The Options Flow fix for clearing optional scene entities passed manual HA verification; configurations with fewer than four active regular mappings now persist correctly.
- Restoring the last regular scene from Neutral Scene mode passed manual HA/KNX verification for both a short press and a repeated long press; subsequent scene cycling also continues correctly.
- The ETS test setup now uses only one physical button for `31/0/200`; one physical telegram per press was confirmed.
- The current Config Flow and Neutral Scene changes have passed their manual regression tests.
- Scene Button deletion passed the complete manual HA/KNX test: confirmation,
  entity cleanup, preserved button order, shared GA registration, collision-free
  reuse of the released Button ID and protection of the final Scene Button were
  verified.

---

## Configuration

- [x] Add editing of existing scene buttons
- [x] Automatically register configured KNX group addresses
- [x] Add deletion of existing scene buttons
- [ ] Clone scene buttons as independent configurations
- [ ] Improve Config Flow user experience
- [ ] Validate all configuration inputs
- [x] Allow one to four regular mappings while keeping four suggested rows
- [x] Configure the Neutral Mapping before regular mappings
- [x] Allow repeated HA scene entities while requiring unique KNX scene numbers
- [x] Improve error messages
- [x] Apply Trigger-Mode-specific KNX scene number ranges
- [x] Make Neutral Scene number 1 implicit in Neutral Scene mode

---

## Runtime

- [ ] Review runtime state restoration
- [ ] Improve startup and shutdown handling
- [ ] Improve controller logging
- [ ] Review edge-case handling

---

## KNX

- [ ] Verify status LED behaviour
- [x] Add a central KNX event registration manager
- [x] Reference-count shared group-address registrations across Config Entries
- [x] Route one group address to multiple Scene Button controllers
- [x] Reject use of one group address as both scene and toggle input
- [x] Remove KNX event handling from entity classes
- [x] Verify automatic registration without KNX YAML configuration
- [ ] Validate duplicate event handling
- [x] Test all supported trigger modes

---

## Home Assistant

- [ ] Review device information
- [ ] Review entity naming
- [ ] Review unique IDs
- [x] Review translations
- [ ] Review diagnostics support

---

## Documentation

- [ ] Complete architecture documentation
- [ ] Add installation guide
- [ ] Add configuration guide
- [ ] Add troubleshooting guide
- [ ] Add developer documentation

---

## Testing

### Unit Tests

- [ ] Add tests for configuration models
- [ ] Add controller tests
- [ ] Add runtime tests

### Integration Tests

- [ ] Test Config Flow
- [ ] Test entity behaviour
- [ ] Test KNX communication
- [ ] Test restart behaviour

### Manual Tests

- [x] Verify all trigger modes
- [x] Verify scene selection
- [x] Verify neutral scene handling
- [x] Verify Scene Button deletion and shared-GA lifecycle
- [ ] Verify status LED behaviour
- [x] Verify multiple configured buttons

---

# Future Enhancements

- [ ] Document synchronization-group concept and data model
- [ ] Add shared logical Scene Mappings and Runtime state
- [ ] Allow existing Scene Buttons to join a synchronization group
- [ ] Additional trigger modes
- [ ] Enhanced LED functionality
- [ ] Import / Export of scene mappings
- [ ] Additional KNX device compatibility
- [ ] Improved diagnostics

---

# Before v1.0.0

- [ ] Complete documentation review
- [ ] Complete translation review
- [ ] Complete code cleanup
- [ ] Run full test suite
- [ ] Review logging
- [ ] Review entity model
- [ ] Verify HACS compatibility
- [ ] Perform release review
