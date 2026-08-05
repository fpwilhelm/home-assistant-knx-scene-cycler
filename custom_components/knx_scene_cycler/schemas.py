"""Schemas for the KNX Scene Cycler configuration flows."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.helpers import selector

from .const import (
    CONF_BUTTON_ID,
    CONF_BUTTON_NAME,
    CONF_HUB_NAME,
    CONF_KNX_SCENE_NUMBER,
    CONF_MAPPING_NAME,
    CONF_SCENE_ENTITY_ID,
    CONF_SCENE_SELECTION_ADDRESS,
    CONF_STATUS_LED_ADDRESS,
    CONF_TOGGLE_ADDRESS,
    CONF_TRIGGER_MODE,
    DEFAULT_REGULAR_SCENE_MAPPING_SLOTS,
    DEFAULT_NEUTRAL_KNX_SCENE_NUMBER,
    MAX_KNX_SCENE_NUMBER,
    MIN_KNX_SCENE_NUMBER,
)
from .models import TriggerMode

ACTION_ADD_BUTTON = "add_button"
ACTION_EDIT_BUTTON = "edit_button"
ACTION_FINISH = "finish"

DEFAULT_HUB_NAME = "KNX Scene Cycler"
DEFAULT_BUTTON_NAME = "Scene Button"

CONF_ACTION = "action"

_REGULAR_MAPPING_COUNT = DEFAULT_REGULAR_SCENE_MAPPING_SLOTS


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
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        ACTION_ADD_BUTTON,
                        ACTION_EDIT_BUTTON,
                        ACTION_FINISH,
                    ],
                    translation_key="options_action",
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
        }
    )


def _button_trigger_schema(
    *,
    default_button_name: str,
    defaults: Mapping[str, Any] | None = None,
) -> vol.Schema:
    """Return the schema for button name and trigger mode."""
    form_defaults = defaults or {}

    return vol.Schema(
        {
            vol.Required(
                CONF_BUTTON_NAME,
                default=form_defaults.get(
                    CONF_BUTTON_NAME,
                    default_button_name,
                ),
            ): str,
            vol.Required(
                CONF_TRIGGER_MODE,
                default=form_defaults.get(
                    CONF_TRIGGER_MODE,
                    TriggerMode.SEPARATE_TOGGLE.value,
                ),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        TriggerMode.SEPARATE_TOGGLE.value,
                        TriggerMode.NEUTRAL_SCENE.value,
                    ],
                    translation_key="trigger_mode",
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        }
    )


def _button_addresses_schema(
    *,
    trigger_mode: TriggerMode,
    defaults: Mapping[str, Any] | None = None,
) -> vol.Schema:
    """Return the group-address schema for one trigger mode."""
    form_defaults = defaults or {}
    schema: dict[vol.Marker, Any] = {
        vol.Required(
            CONF_SCENE_SELECTION_ADDRESS,
            default=form_defaults.get(
                CONF_SCENE_SELECTION_ADDRESS,
                vol.UNDEFINED,
            ),
        ): str,
    }

    if trigger_mode is TriggerMode.SEPARATE_TOGGLE:
        schema[
            vol.Required(
                CONF_TOGGLE_ADDRESS,
                default=form_defaults.get(
                    CONF_TOGGLE_ADDRESS,
                    vol.UNDEFINED,
                ),
            )
        ] = str

    schema[
        vol.Optional(
            CONF_STATUS_LED_ADDRESS,
            default=form_defaults.get(
                CONF_STATUS_LED_ADDRESS,
                vol.UNDEFINED,
            ),
        )
    ] = str

    return vol.Schema(schema)


def _regular_scenes_schema(
    *,
    trigger_mode: TriggerMode = TriggerMode.SEPARATE_TOGGLE,
    defaults: Mapping[str, Any] | None = None,
) -> vol.Schema:
    """Return the schema for four regular scene mappings."""
    form_defaults = defaults or {}
    schema: dict[vol.Marker, Any] = {}
    scene_selector = _scene_selector()
    minimum_scene_number = (
        DEFAULT_NEUTRAL_KNX_SCENE_NUMBER + 1
        if trigger_mode is TriggerMode.NEUTRAL_SCENE
        else MIN_KNX_SCENE_NUMBER
    )
    scene_number_schema = _scene_number_schema(
        minimum=minimum_scene_number,
    )

    for mapping_number in range(
        1,
        _REGULAR_MAPPING_COUNT + 1,
    ):
        scene_entity_key = _scene_entity_key(mapping_number)
        suggested_scene_entity = form_defaults.get(scene_entity_key)

        schema[
            vol.Required(
                _mapping_name_key(mapping_number),
                default=form_defaults.get(
                    _mapping_name_key(mapping_number),
                    f"Scene {mapping_number}",
                ),
            )
        ] = str
        schema[
            vol.Optional(
                scene_entity_key,
                description=(
                    {
                        "suggested_value": suggested_scene_entity,
                    }
                    if suggested_scene_entity not in (None, "")
                    else None
                ),
            )
        ] = scene_selector
        schema[
            vol.Optional(
                _knx_scene_number_key(mapping_number),
                default=form_defaults.get(
                    _knx_scene_number_key(mapping_number),
                    mapping_number
                    + (
                        1
                        if trigger_mode is TriggerMode.NEUTRAL_SCENE
                        else 0
                    ),
                ),
            )
        ] = scene_number_schema

    return vol.Schema(schema)


def _neutral_scene_schema(
    *,
    trigger_mode: TriggerMode,
    defaults: Mapping[str, Any] | None = None,
) -> vol.Schema:
    """Return the neutral scene schema for one trigger mode."""
    form_defaults = defaults or {}
    schema: dict[vol.Marker, Any] = {
        vol.Required(
            _neutral_mapping_name_key(),
            default=form_defaults.get(
                _neutral_mapping_name_key(),
                "Neutral",
            ),
        ): str,
        vol.Required(
            _neutral_scene_entity_key(),
            default=form_defaults.get(
                _neutral_scene_entity_key(),
                vol.UNDEFINED,
            ),
        ): _scene_selector(),
    }

    return vol.Schema(schema)


def _scene_selector() -> selector.EntitySelector:
    """Return a Home Assistant scene selector."""
    return selector.EntitySelector(
        selector.EntitySelectorConfig(
            domain="scene",
        )
    )


def _scene_number_schema(
    *,
    minimum: int = MIN_KNX_SCENE_NUMBER,
) -> selector.NumberSelector:
    """Return the KNX scene number validator."""
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=minimum,
            max=MAX_KNX_SCENE_NUMBER,
            step=1,
            mode=selector.NumberSelectorMode.BOX,
        )
    )


def _button_selection_schema(
    button_options: Mapping[str, str],
) -> vol.Schema:
    """Return the schema for selecting an existing scene button."""
    return vol.Schema(
        {
            vol.Required(CONF_BUTTON_ID): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(
                            value=button_id,
                            label=button_name,
                        )
                        for button_id, button_name in button_options.items()
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        }
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
