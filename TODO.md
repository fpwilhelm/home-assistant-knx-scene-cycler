# TODO

This document tracks the current implementation work for KNX Scene Cycler.

Long-term project goals are documented in `ROADMAP.md`.

Released functionality is documented in `CHANGELOG.md`.

---

# Current Focus (v0.3.0)

## Configuration

- [ ] Add editing of existing scene buttons
- [ ] Add deletion of existing scene buttons
- [ ] Improve Config Flow user experience
- [ ] Validate all configuration inputs
- [ ] Improve error messages

---

## Runtime

- [ ] Review runtime state restoration
- [ ] Improve startup and shutdown handling
- [ ] Improve controller logging
- [ ] Review edge-case handling

---

## KNX

- [ ] Verify status LED behaviour
- [ ] Review KNX event registration
- [ ] Validate duplicate event handling
- [ ] Test all supported trigger modes

---

## Home Assistant

- [ ] Review device information
- [ ] Review entity naming
- [ ] Review unique IDs
- [ ] Review translations
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

- [ ] Verify all trigger modes
- [ ] Verify scene selection
- [ ] Verify neutral scene handling
- [ ] Verify status LED behaviour
- [ ] Verify multiple configured buttons

---

# Future Enhancements

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