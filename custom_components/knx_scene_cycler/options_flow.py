"""Options flow for the KNX Scene Cycler integration."""

from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .button_factory import (
    _button_config_to_form_data,
    _create_button_config,
)
from .const import (
    CONF_BUTTON_ID,
    CONF_BUTTON_NAME,
    CONF_BUTTONS,
)
from .models import SceneButtonConfig
from .schemas import (
    ACTION_ADD_BUTTON,
    ACTION_EDIT_BUTTON,
    CONF_ACTION,
    DEFAULT_BUTTON_NAME,
    _button_addresses_schema,
    _button_selection_schema,
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
        self._operation = ""
        self._selected_button_id: str | None = None
        self._existing_button_config: SceneButtonConfig | None = None

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Choose an options-flow action."""
        if user_input is not None:
            action = user_input[CONF_ACTION]

            if action == ACTION_ADD_BUTTON:
                self._operation = ACTION_ADD_BUTTON
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
                return await self.async_step_button_trigger()

            if action == ACTION_EDIT_BUTTON:
                self._operation = ACTION_EDIT_BUTTON
                return await self.async_step_select_button()

            return self.async_create_entry(
                title="",
                data={},
            )

        return self.async_show_form(
            step_id="init",
            data_schema=_options_action_schema(),
        )

    async def async_step_select_button(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Select an existing scene button to edit."""
        stored_buttons = self.config_entry.data.get(CONF_BUTTONS, [])

        if user_input is not None:
            selected_button_id = str(
                user_input[CONF_BUTTON_ID]
            )
            selected_button = next(
                button
                for button in stored_buttons
                if button[CONF_BUTTON_ID] == selected_button_id
            )
            button_config = SceneButtonConfig.from_dict(
                selected_button
            )
            self._selected_button_id = selected_button_id
            self._existing_button_config = button_config
            self._button_data = _button_config_to_form_data(
                button_config
            )
            return await self.async_step_button_trigger()

        button_options = {
            str(button[CONF_BUTTON_ID]): str(
                button[CONF_BUTTON_NAME]
            )
            for button in stored_buttons
        }

        return self.async_show_form(
            step_id="select_button",
            data_schema=_button_selection_schema(button_options),
        )

    async def async_step_button_trigger(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Choose the trigger strategy for a scene button."""
        if user_input is not None:
            self._button_data.update(user_input)
            return await self.async_step_button_addresses()

        return self.async_show_form(
            step_id="button_trigger",
            data_schema=_button_trigger_schema(
                default_button_name=str(
                    self._button_data[CONF_BUTTON_NAME]
                ),
                defaults=self._button_data,
            ),
        )

    async def async_step_button_addresses(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure group addresses for a scene button."""
        if user_input is not None:
            self._button_data.update(user_input)
            return await self.async_step_button_scenes()

        return self.async_show_form(
            step_id="button_addresses",
            data_schema=_button_addresses_schema(
                trigger_mode=_trigger_mode(self._button_data),
                defaults=self._button_data,
            ),
        )

    async def async_step_button_scenes(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure regular scenes for a scene button."""
        errors: dict[str, str] = {}
        form_defaults = self._button_data

        if user_input is not None:
            if _has_duplicate_regular_scene_numbers(user_input):
                errors["base"] = "duplicate_knx_scene_numbers"
                form_defaults = {
                    **self._button_data,
                    **user_input,
                }
            else:
                self._button_data.update(user_input)
                return await self.async_step_button_neutral()

        return self.async_show_form(
            step_id="button_scenes",
            data_schema=_regular_scenes_schema(
                trigger_mode=_trigger_mode(self._button_data),
                defaults=form_defaults,
            ),
            errors=errors,
        )

    async def async_step_button_neutral(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure the neutral scene and save a scene button."""
        errors: dict[str, str] = {}
        form_defaults = self._button_data

        if user_input is not None:
            candidate_data = {
                **self._button_data,
                **user_input,
            }

            try:
                button_config = _create_button_config(
                    candidate_data,
                    existing_config=self._existing_button_config,
                )
            except ValueError as err:
                errors["base"] = _model_error_key(err)
                form_defaults = candidate_data
            else:
                current_buttons = list(
                    self.config_entry.data.get(CONF_BUTTONS, [])
                )
                updated_data = dict(self.config_entry.data)

                if self._operation == ACTION_EDIT_BUTTON:
                    updated_data[CONF_BUTTONS] = [
                        (
                            button_config.to_dict()
                            if button[CONF_BUTTON_ID]
                            == self._selected_button_id
                            else button
                        )
                        for button in current_buttons
                    ]
                else:
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
            step_id="button_neutral",
            data_schema=_neutral_scene_schema(
                trigger_mode=_trigger_mode(self._button_data),
                defaults=form_defaults,
            ),
            errors=errors,
        )
