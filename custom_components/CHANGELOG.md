cat << 'EOF' > CHANGELOG.md
# Changelog

All notable changes to this project will be documented in this file.

## - 2026-07-29
### Added
- Initial release of the `knx_scene_cycler` integration.
- Full multi-button configuration flow for custom device structures.
- KNX Telegram listener integration hooked directly into the Home Assistant KNX bus.
- Synchronized toggle logic (Last scene / Neutral scene) for long press actions.
- Automatic status feedback transmitting state values back to the KNX status LED group address.
EOF
