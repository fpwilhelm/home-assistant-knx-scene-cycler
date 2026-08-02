"""Options flow for the KNX Scene Cycler integration."""

from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .button_factory import _create_button_config
from .const import (
    CONF_BUTTON_ID,
    CONF_BUTTON_NAME,
    CONF_BUTTONS,
)
from .schemas import (
    ACTION_ADD_BUTTON,
    CONF_ACTION,
    DEFAULT_BUTTON_NAME,
    _button_addresses_schema,
    _button_trigger_schema,
    _neutral_scene_schema,
    _options_action_schema,
    _regular_scenes_schema,
)
from .validation import (
    _has_duplicate_regular_scene_numbers,
    _model_error_key,
    _trigger_mode,
)


class KnxSceneCyclerOptionsFlowHandler(
    config_entries.OptionsFlow
):
    """Handle changes to an existing KNX Scene Cycler entry."""

    def __init__(self) -> None:
        """Initialize the options flow."""
        self._button_data: dict[str, Any] = {}

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Choose an options-flow action."""
        if user_input is not None:
            action = user_input[CONF_ACTION]

            if action == ACTION_ADD_BUTTON:
                next_button_number = (
                    len(
                        self.config_entry.data.get(
                            CONF_BUTTONS,
                            [],
                        )
                    )
                    + 1
                )
                self._button_data = {
                    CONF_BUTTON_ID: (
                        f"button_{next_button_number}"
                    ),
                    CONF_BUTTON_NAME: (
                        f"{DEFAULT_BUTTON_NAME} "
                        f"{next_button_number}"
                    ),
                }
                return await self.async_step_add_button_trigger()

            return self.async_create_entry(
                title="",
                data={},
            )

        return self.async_show_form(
            step_id="init",
            data_schema=_options_action_schema(),
        )

    async def async_step_add_button_trigger(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Choose the trigger strategy for another button."""
        if user_input is not None:
            self._button_data.update(user_input)
            return await self.async_step_add_button_addresses()

        return self.async_show_form(
            step_id="add_button_trigger",
            data_schema=_button_trigger_schema(
                default_button_name=str(
                    self._button_data[CONF_BUTTON_NAME]
                ),
            ),
        )

    async def async_step_add_button_addresses(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure group addresses for another button."""
        if user_input is not None:
            self._button_data.update(user_input)
            return await self.async_step_add_button_scenes()

        return self.async_show_form(
            step_id="add_button_addresses",
            data_schema=_button_addresses_schema(
                trigger_mode=_trigger_mode(self._button_data),
            ),
        )

    async def async_step_add_button_scenes(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure regular scenes for another button."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if _has_duplicate_regular_scene_numbers(user_input):
                errors["base"] = "duplicate_knx_scene_numbers"
            else:
                self._button_data.update(user_input)
                return await self.async_step_add_button_neutral()

        return self.async_show_form(
            step_id="add_button_scenes",
            data_schema=_regular_scenes_schema(),
            errors=errors,
        )

    async def async_step_add_button_neutral(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure the neutral scene and save another button."""
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
                current_buttons = list(
                    self.config_entry.data.get(CONF_BUTTONS, [])
                )
                updated_data = dict(self.config_entry.data)
                updated_data[CONF_BUTTONS] = [
                    *current_buttons,
                    button_config.to_dict(),
                ]

                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data=updated_data,
                )

                return self.async_create_entry(
                    title="",
                    data={},
                )

        return self.async_show_form(
            step_id="add_button_neutral",
            data_schema=_neutral_scene_schema(
                trigger_mode=_trigger_mode(self._button_data),
            ),
            errors=errors,
        )
