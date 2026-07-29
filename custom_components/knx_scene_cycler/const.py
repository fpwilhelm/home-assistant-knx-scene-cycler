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


# ---------------------------------------------------------------------------
# KNX group addresses
# ---------------------------------------------------------------------------

CONF_SCENE_SELECTION_ADDRESS: Final = "scene_selection_address"
CONF_TOGGLE_ADDRESS: Final = "toggle_address"
CONF_STATUS_LED_ADDRESS: Final = "status_led_address"


# ---------------------------------------------------------------------------
# Scene configuration
# ---------------------------------------------------------------------------

CONF_SCENE_MAPPINGS: Final = "scene_mappings"
CONF_SCENE_SLOT: Final = "scene_slot"
CONF_KNX_SCENE_NUMBER: Final = "knx_scene_number"
CONF_SCENE_ENTITY_ID: Final = "scene_entity_id"
CONF_NEUTRAL_SCENE_ENTITY_ID: Final = "neutral_scene_entity_id"


# ---------------------------------------------------------------------------
# Runtime state
# ---------------------------------------------------------------------------

ATTR_ACTIVE: Final = "active"
ATTR_LAST_ACTIVE_SCENE_SLOT: Final = "last_active_scene_slot"


# ---------------------------------------------------------------------------
# Scene slots
# ---------------------------------------------------------------------------

SCENE_SLOT_1: Final = 1
SCENE_SLOT_2: Final = 2
SCENE_SLOT_3: Final = 3
SCENE_SLOT_4: Final = 4

SCENE_SLOTS: Final = (
    SCENE_SLOT_1,
    SCENE_SLOT_2,
    SCENE_SLOT_3,
    SCENE_SLOT_4,
)

DEFAULT_SCENE_SLOT: Final = SCENE_SLOT_1


# ---------------------------------------------------------------------------
# KNX values
# ---------------------------------------------------------------------------

# Scene numbers supported by DPT 17.001 in the integration UI.
MIN_KNX_SCENE_NUMBER: Final = 1
MAX_KNX_SCENE_NUMBER: Final = 64

# The MDT long-press object sends 0 as a toggle impulse.
KNX_TOGGLE_VALUE: Final = 0

# Status LED payloads.
KNX_LED_OFF: Final = 0
KNX_LED_ON: Final = 1


# ---------------------------------------------------------------------------
# Config entry versions
# ---------------------------------------------------------------------------

CONFIG_ENTRY_VERSION: Final = 2
CONFIG_ENTRY_MINOR_VERSION: Final = 1


# ---------------------------------------------------------------------------
# Legacy prototype constants
#
# These constants are still used by the existing prototype implementation.
# They remain available during the refactor so the integration continues to
# load while config_flow.py, switch.py and select.py are migrated.
#
# Remove them only after the complete codebase has been converted to the new
# configuration model and an appropriate config-entry migration exists.
# ---------------------------------------------------------------------------

CONF_DEVICE_NAME: Final = "device_name"

CONF_GA_SCENE_SELECT: Final = "ga_scene_select"
CONF_GA_SWITCH: Final = "ga_switch"
CONF_GA_STATUS_LED: Final = "ga_status_led"

CONF_SCENE_1: Final = "scene_1"
CONF_SCENE_2: Final = "scene_2"
CONF_SCENE_3: Final = "scene_3"
CONF_SCENE_4: Final = "scene_4"
CONF_SCENE_5_NEUTRAL: Final = "scene_5_neutral"

CONF_KNX_NUM_1: Final = "knx_num_1"
CONF_KNX_NUM_2: Final = "knx_num_2"
CONF_KNX_NUM_3: Final = "knx_num_3"
CONF_KNX_NUM_4: Final = "knx_num_4"