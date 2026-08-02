"""Schemas for the KNX Scene Cycler configuration flows."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.helpers import selector

from .const import (
    CONF_BUTTON_NAME,
    CONF_HUB_NAME,
    CONF_KNX_SCENE_NUMBER,
    CONF_MAPPING_NAME,
    CONF_SCENE_ENTITY_ID,
    CONF_SCENE_SELECTION_ADDRESS,
    CONF_STATUS_LED_ADDRESS,
    CONF_TOGGLE_ADDRESS,
    CONF_TRIGGER_MODE,
    DEFAULT_NEUTRAL_KNX_SCENE_NUMBER,
    MAX_KNX_SCENE_NUMBER,
    MIN_KNX_SCENE_NUMBER,
    MIN_REGULAR_SCENE_MAPPINGS,
)
from .models import TriggerMode

ACTION_ADD_BUTTON = "add_button"
ACTION_FINISH = "finish"

DEFAULT_HUB_NAME = "KNX Scene Cycler"
DEFAULT_BUTTON_NAME = "Scene Button"

CONF_ACTION = "action"

_REGULAR_MAPPING_COUNT = MIN_REGULAR_SCENE_MAPPINGS


def _hub_schema() -> vol.Schema:
    """Return the hub configuration schema."""
    return vol.Schema(
        {
            vol.Required(
                CONF_HUB_NAME,
                default=DEFAULT_HUB_NAME,
            ): str,
        }
    )


def _options_action_schema() -> vol.Schema:
    """Return the options-flow action schema."""
    return vol.Schema(
        {
            vol.Required(
                CONF_ACTION,
                default=ACTION_ADD_BUTTON,
            ): vol.In(
                {
                    ACTION_ADD_BUTTON: "Add scene button",
                    ACTION_FINISH: "Finish",
                }
            ),
        }
    )


def _button_trigger_schema(
    *,
    default_button_name: str,
) -> vol.Schema:
    """Return the schema for button name and trigger mode."""
    return vol.Schema(
        {
            vol.Required(
                CONF_BUTTON_NAME,
                default=default_button_name,
            ): str,
            vol.Required(
                CONF_TRIGGER_MODE,
                default=TriggerMode.SEPARATE_TOGGLE.value,
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(
                            value=TriggerMode.SEPARATE_TOGGLE.value,
                            label="Separate Toggle GA",
                        ),
                        selector.SelectOptionDict(
                            value=TriggerMode.NEUTRAL_SCENE.value,
                            label="Neutral Scene on Scene GA",
                        ),
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        }
    )


def _button_addresses_schema(
    *,
    trigger_mode: TriggerMode,
) -> vol.Schema:
    """Return the group-address schema for one trigger mode."""
    schema: dict[vol.Marker, Any] = {
        vol.Required(CONF_SCENE_SELECTION_ADDRESS): str,
    }

    if trigger_mode is TriggerMode.SEPARATE_TOGGLE:
        schema[vol.Required(CONF_TOGGLE_ADDRESS)] = str

    schema[vol.Optional(CONF_STATUS_LED_ADDRESS)] = str

    return vol.Schema(schema)


def _regular_scenes_schema() -> vol.Schema:
    """Return the schema for four regular scene mappings."""
    schema: dict[vol.Marker, Any] = {}
    scene_selector = _scene_selector()
    scene_number_schema = _scene_number_schema()

    for mapping_number in range(
        1,
        _REGULAR_MAPPING_COUNT + 1,
    ):
        schema[
            vol.Required(
                _mapping_name_key(mapping_number),
                default=f"Scene {mapping_number}",
            )
        ] = str
        schema[
            vol.Required(
                _scene_entity_key(mapping_number)
            )
        ] = scene_selector
        schema[
            vol.Required(
                _knx_scene_number_key(mapping_number),
                default=mapping_number,
            )
        ] = scene_number_schema

    return vol.Schema(schema)


def _neutral_scene_schema(
    *,
    trigger_mode: TriggerMode,
) -> vol.Schema:
    """Return the neutral scene schema for one trigger mode."""
    schema: dict[vol.Marker, Any] = {
        vol.Required(
            _neutral_mapping_name_key(),
            default="Neutral",
        ): str,
        vol.Required(
            _neutral_scene_entity_key()
        ): _scene_selector(),
    }

    if trigger_mode is TriggerMode.NEUTRAL_SCENE:
        schema[
            vol.Required(
                _neutral_knx_scene_number_key(),
                default=DEFAULT_NEUTRAL_KNX_SCENE_NUMBER,
            )
        ] = _scene_number_schema()

    return vol.Schema(schema)


def _scene_selector() -> selector.EntitySelector:
    """Return a Home Assistant scene selector."""
    return selector.EntitySelector(
        selector.EntitySelectorConfig(
            domain="scene",
        )
    )


def _scene_number_schema() -> vol.All:
    """Return the KNX scene number validator."""
    return vol.All(
        vol.Coerce(int),
        vol.Range(
            min=MIN_KNX_SCENE_NUMBER,
            max=MAX_KNX_SCENE_NUMBER,
        ),
    )


def _mapping_name_key(mapping_number: int) -> str:
    """Return the temporary form key for a mapping name."""
    return f"{CONF_MAPPING_NAME}_{mapping_number}"


def _scene_entity_key(mapping_number: int) -> str:
    """Return the temporary form key for a scene entity."""
    return f"{CONF_SCENE_ENTITY_ID}_{mapping_number}"


def _knx_scene_number_key(mapping_number: int) -> str:
    """Return the temporary form key for a KNX scene number."""
    return f"{CONF_KNX_SCENE_NUMBER}_{mapping_number}"


def _neutral_mapping_name_key() -> str:
    """Return the temporary form key for the neutral mapping name."""
    return f"{CONF_MAPPING_NAME}_neutral"


def _neutral_scene_entity_key() -> str:
    """Return the temporary form key for the neutral scene entity."""
    return f"{CONF_SCENE_ENTITY_ID}_neutral"


def _neutral_knx_scene_number_key() -> str:
    """Return the temporary form key for the neutral KNX scene number."""
    return f"{CONF_KNX_SCENE_NUMBER}_neutral"
