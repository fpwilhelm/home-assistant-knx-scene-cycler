"""Constants for the KNX Scene Cycler integration."""

from typing import Final

DOMAIN: Final = "knx_scene_cycler"

PLATFORMS: Final = ("select", "switch")


# ---------------------------------------------------------------------------
# Config entry
# ---------------------------------------------------------------------------

CONF_HUB_NAME: Final = "hub_name"


# ---------------------------------------------------------------------------
# Button configuration
# ---------------------------------------------------------------------------

CONF_BUTTONS: Final = "buttons"
CONF_BUTTON_ID: Final = "button_id"
CONF_BUTTON_NAME: Final = "button_name"
CONF_TRIGGER_MODE: Final = "trigger_mode"


# ---------------------------------------------------------------------------
# KNX group addresses
# ---------------------------------------------------------------------------

CONF_SCENE_SELECTION_ADDRESS: Final = "scene_selection_address"
CONF_TOGGLE_ADDRESS: Final = "toggle_address"
CONF_STATUS_LED_ADDRESS: Final = "status_led_address"


# ---------------------------------------------------------------------------
# Scene mappings
# ---------------------------------------------------------------------------

CONF_SCENE_MAPPINGS: Final = "scene_mappings"
CONF_MAPPING_ID: Final = "mapping_id"
CONF_MAPPING_NAME: Final = "mapping_name"
CONF_MAPPING_TYPE: Final = "mapping_type"
CONF_KNX_SCENE_NUMBER: Final = "knx_scene_number"
CONF_SCENE_ENTITY_ID: Final = "scene_entity_id"
CONF_LED_COLOR_VALUE: Final = "led_color_value"


# ---------------------------------------------------------------------------
# Runtime state
# ---------------------------------------------------------------------------

ATTR_ACTIVE: Final = "active"
ATTR_ACTIVE_KNX_SCENE_NUMBER: Final = "active_knx_scene_number"
ATTR_LAST_REGULAR_SCENE_NUMBER: Final = "last_regular_scene_number"


# ---------------------------------------------------------------------------
# KNX scene limits
# ---------------------------------------------------------------------------

# Home Assistant exposes DPT 17.001 scene numbers as 1..64.
# The raw KNX payload remains 0..63 and is not used by this integration.
MIN_KNX_SCENE_NUMBER: Final = 1
MAX_KNX_SCENE_NUMBER: Final = 64

MIN_REGULAR_SCENE_MAPPINGS: Final = 4
MAX_REGULAR_SCENE_MAPPINGS: Final = 64

DEFAULT_NEUTRAL_KNX_SCENE_NUMBER: Final = 1


# ---------------------------------------------------------------------------
# KNX LED values
# ---------------------------------------------------------------------------

# DPT 5.005 LED color values. The actual color assignment is device-specific.
MIN_LED_COLOR_VALUE: Final = 0
MAX_LED_COLOR_VALUE: Final = 255
DEFAULT_LED_COLOR_VALUE: Final = 1
DEFAULT_NEUTRAL_LED_COLOR_VALUE: Final = 0

# DPT 1.001 status LED payloads.
KNX_LED_OFF: Final = 0
KNX_LED_ON: Final = 1


# ---------------------------------------------------------------------------
# Config entry versions
# ---------------------------------------------------------------------------

# Version 3 introduces trigger modes and the SceneMapping-only configuration
# model. Existing prototype entries are intentionally not migrated.
CONFIG_ENTRY_VERSION: Final = 3
CONFIG_ENTRY_MINOR_VERSION: Final = 0
