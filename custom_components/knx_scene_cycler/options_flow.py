"""Options flow for the KNX Scene Cycler integration."""

from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.const import Platform
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import entity_registry as er

from .button_factory import (
    _button_config_to_form_data,
    _create_button_config,
    _replace_regular_scene_form_data,
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
    ACTION_REMOVE_BUTTON,
    CONF_ACTION,
    DEFAULT_BUTTON_NAME,
    _button_addresses_schema,
    _button_selection_schema,
    _button_trigger_schema,
    _neutral_scene_schema,
    _options_action_schema,
    _regular_scenes_schema,
    _remove_confirmation_schema,
)
from .validation import (
    _has_cross_button_address_role_conflict,
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
        self._selected_button_name: str | None = None

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Choose an options-flow action."""
        if user_input is not None:
            action = user_input[CONF_ACTION]

            if action == ACTION_ADD_BUTTON:
                self._operation = ACTION_ADD_BUTTON
                next_button_number = self._next_button_number(
                    self.config_entry.data.get(CONF_BUTTONS, [])
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

            if action == ACTION_REMOVE_BUTTON:
                self._operation = ACTION_REMOVE_BUTTON
                return await self.async_step_select_button()

            return self.async_create_entry(
                title="",
                data={},
            )

        return self.async_show_form(
            step_id="init",
            data_schema=_options_action_schema(
                can_remove=(
                    len(
                        self.config_entry.data.get(
                            CONF_BUTTONS,
                            [],
                        )
                    )
                    > 1
                ),
            ),
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
            self._selected_button_name = button_config.name
            self._existing_button_config = button_config

            if self._operation == ACTION_REMOVE_BUTTON:
                return await self.async_step_confirm_remove()

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

    async def async_step_confirm_remove(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Confirm and persist removal of one scene button."""
        if user_input is not None:
            selected_button_id = self._selected_button_id
            if selected_button_id is None:
                return self.async_abort(reason="invalid_configuration")

            current_buttons = list(
                self.config_entry.data.get(CONF_BUTTONS, [])
            )
            remaining_buttons = [
                button
                for button in current_buttons
                if button[CONF_BUTTON_ID] != selected_button_id
            ]

            if len(remaining_buttons) == len(current_buttons):
                return self.async_abort(reason="invalid_configuration")

            if not remaining_buttons:
                return self.async_abort(reason="last_button")

            self._remove_button_entities(selected_button_id)

            updated_data = dict(self.config_entry.data)
            updated_data[CONF_BUTTONS] = remaining_buttons
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=updated_data,
            )

            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="confirm_remove",
            data_schema=_remove_confirmation_schema(),
            description_placeholders={
                "button_name": self._selected_button_name or "",
            },
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
            return await self.async_step_button_neutral()

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
        """Configure regular scenes and save a scene button."""
        errors: dict[str, str] = {}
        form_defaults = self._button_data

        if user_input is not None:
            candidate_data = _replace_regular_scene_form_data(
                self._button_data,
                user_input,
            )

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
                other_button_configs = [
                    SceneButtonConfig.from_dict(button)
                    for button in current_buttons
                    if button[CONF_BUTTON_ID]
                    != self._selected_button_id
                ]

                if _has_cross_button_address_role_conflict(
                    button_config,
                    other_button_configs,
                ):
                    errors["base"] = (
                        "conflicting_group_address_roles"
                    )
                    form_defaults = candidate_data
                else:
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
        """Configure the neutral scene."""
        if user_input is not None:
            self._button_data.update(user_input)
            return await self.async_step_button_scenes()

        return self.async_show_form(
            step_id="button_neutral",
            data_schema=_neutral_scene_schema(
                trigger_mode=_trigger_mode(self._button_data),
                defaults=self._button_data,
            ),
        )

    def _remove_button_entities(self, button_id: str) -> None:
        """Remove the switch and select registry entries for one button."""
        registry = er.async_get(self.hass)

        for platform in (Platform.SWITCH, Platform.SELECT):
            unique_id = (
                f"{self.config_entry.entry_id}_{button_id}_{platform}"
            )
            entity_id = registry.async_get_entity_id(
                platform,
                self.config_entry.domain,
                unique_id,
            )
            if entity_id is not None:
                registry.async_remove(entity_id)

    @staticmethod
    def _next_button_number(
        stored_buttons: list[dict[str, Any]],
    ) -> int:
        """Return the first unused generated button number."""
        used_button_ids = {
            str(button.get(CONF_BUTTON_ID, ""))
            for button in stored_buttons
        }
        button_number = 1

        while f"button_{button_number}" in used_button_ids:
            button_number += 1

        return button_number
