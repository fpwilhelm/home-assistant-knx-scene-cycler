"""Config flow for the KNX Scene Cycler integration."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .button_factory import _create_button_config
from .const import (
    CONFIG_ENTRY_MINOR_VERSION,
    CONFIG_ENTRY_VERSION,
    CONF_BUTTON_ID,
    CONF_BUTTON_NAME,
    CONF_BUTTONS,
    CONF_HUB_NAME,
    CONF_KNX_SCENE_NUMBER,
    CONF_MAPPING_ID,
    CONF_MAPPING_NAME,
    CONF_MAPPING_TYPE,
    CONF_SCENE_ENTITY_ID,
    CONF_SCENE_MAPPINGS,
    CONF_SCENE_SELECTION_ADDRESS,
    CONF_STATUS_LED_ADDRESS,
    CONF_TOGGLE_ADDRESS,
    CONF_TRIGGER_MODE,
    DEFAULT_NEUTRAL_KNX_SCENE_NUMBER,
    DOMAIN,
    MAX_KNX_SCENE_NUMBER,
    MIN_KNX_SCENE_NUMBER,
    MIN_REGULAR_SCENE_MAPPINGS,
)
from .models import (
    SceneButtonConfig,
    SceneMapping,
    SceneMappingType,
    TriggerMode,
)
from .options_flow import KnxSceneCyclerOptionsFlowHandler
from .schemas import (
    ACTION_ADD_BUTTON,
    ACTION_FINISH,
    CONF_ACTION,
    DEFAULT_BUTTON_NAME,
    DEFAULT_HUB_NAME,
    _REGULAR_MAPPING_COUNT,
    _button_addresses_schema,
    _button_trigger_schema,
    _hub_schema,
    _knx_scene_number_key,
    _mapping_name_key,
    _neutral_scene_schema,
    _neutral_knx_scene_number_key,
    _neutral_mapping_name_key,
    _neutral_scene_entity_key,
    _options_action_schema,
    _regular_scenes_schema,
    _scene_entity_key,
    _scene_number_schema,
    _scene_selector,
)
from .validation import (
    _has_duplicate_regular_scene_numbers,
    _model_error_key,
    _optional_string,
    _trigger_mode,
)


class KnxSceneCyclerConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle a config flow for KNX Scene Cycler."""

    VERSION = CONFIG_ENTRY_VERSION
    MINOR_VERSION = CONFIG_ENTRY_MINOR_VERSION

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._hub_name = DEFAULT_HUB_NAME
        self._button_data: dict[str, Any] = {}

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure the KNX Scene Cycler hub."""
        if user_input is not None:
            self._hub_name = str(
                user_input[CONF_HUB_NAME]
            ).strip()
            self._button_data = {
                CONF_BUTTON_ID: "button_1",
                CONF_BUTTON_NAME: DEFAULT_BUTTON_NAME,
            }
            return await self.async_step_button_trigger()

        return self.async_show_form(
            step_id="user",
            data_schema=_hub_schema(),
        )

    async def async_step_button_trigger(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Choose the trigger strategy for the first button."""
        if user_input is not None:
            self._button_data.update(user_input)
            return await self.async_step_button_addresses()

        return self.async_show_form(
            step_id="button_trigger",
            data_schema=_button_trigger_schema(
                default_button_name=DEFAULT_BUTTON_NAME,
            ),
        )

    async def async_step_button_addresses(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure KNX group addresses for the first button."""
        if user_input is not None:
            self._button_data.update(user_input)
            return await self.async_step_button_scenes()

        return self.async_show_form(
            step_id="button_addresses",
            data_schema=_button_addresses_schema(
                trigger_mode=_trigger_mode(self._button_data),
            ),
        )

    async def async_step_button_scenes(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure regular scenes for the first button."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if _has_duplicate_regular_scene_numbers(user_input):
                errors["base"] = "duplicate_knx_scene_numbers"
            else:
                self._button_data.update(user_input)
                return await self.async_step_button_neutral()

        return self.async_show_form(
            step_id="button_scenes",
            data_schema=_regular_scenes_schema(),
            errors=errors,
        )

    async def async_step_button_neutral(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure the neutral scene and create the entry."""
        errors: dict[str, str] = {}

        if user_input is not None:
            candidate_data = {
                **self._button_data,
                **user_input,
            }

            try:
                button_config = _create_button_config(candidate_data)
            except ValueError as err:
                errors["base"] = _model_error_key(err)
            else:
                return self.async_create_entry(
                    title=self._hub_name,
                    data={
                        CONF_HUB_NAME: self._hub_name,
                        CONF_BUTTONS: [
                            button_config.to_dict(),
                        ],
                    },
                )

        return self.async_show_form(
            step_id="button_neutral",
            data_schema=_neutral_scene_schema(
                trigger_mode=_trigger_mode(self._button_data),
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow handler."""
        return KnxSceneCyclerOptionsFlowHandler()
