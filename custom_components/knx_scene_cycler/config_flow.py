"""Config flow for the KNX Scene Cycler integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONFIG_ENTRY_MINOR_VERSION,
    CONFIG_ENTRY_VERSION,
    CONF_BUTTON_ID,
    CONF_BUTTON_NAME,
    CONF_BUTTONS,
    CONF_HUB_NAME,
    CONF_KNX_SCENE_NUMBER,
    CONF_NEUTRAL_SCENE_ENTITY_ID,
    CONF_SCENE_ENTITY_ID,
    CONF_SCENE_MAPPINGS,
    CONF_SCENE_SELECTION_ADDRESS,
    CONF_SCENE_SLOT,
    CONF_STATUS_LED_ADDRESS,
    CONF_TOGGLE_ADDRESS,
    DOMAIN,
    MAX_KNX_SCENE_NUMBER,
    MIN_KNX_SCENE_NUMBER,
    SCENE_SLOTS,
)
from .models import SceneButtonConfig, SceneMapping

ACTION_ADD_BUTTON = "add_button"
ACTION_FINISH = "finish"

DEFAULT_HUB_NAME = "KNX Scene Cycler"
DEFAULT_BUTTON_NAME = "Scene Button"


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

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure the KNX Scene Cycler hub."""
        if user_input is not None:
            self._hub_name = str(
                user_input[CONF_HUB_NAME]
            ).strip()

            return await self.async_step_button()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HUB_NAME,
                        default=DEFAULT_HUB_NAME,
                    ): str,
                }
            ),
        )

    async def async_step_button(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure the first logical KNX scene button."""
        errors: dict[str, str] = {}

        if user_input is not None:
            button_config = _create_button_config(
                user_input=user_input,
                button_id="button_1",
            )

            if not button_config.has_unique_knx_scene_numbers():
                errors["base"] = "duplicate_knx_scene_numbers"
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
            step_id="button",
            data_schema=_button_schema(
                default_button_name=DEFAULT_BUTTON_NAME,
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


class KnxSceneCyclerOptionsFlowHandler(
    config_entries.OptionsFlow
):
    """Handle changes to an existing KNX Scene Cycler entry."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Choose an options-flow action."""
        if user_input is not None:
            action = user_input["action"]

            if action == ACTION_ADD_BUTTON:
                return await self.async_step_add_button()

            return self.async_create_entry(
                title="",
                data={},
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "action",
                        default=ACTION_ADD_BUTTON,
                    ): vol.In(
                        {
                            ACTION_ADD_BUTTON: "Add scene button",
                            ACTION_FINISH: "Finish",
                        }
                    ),
                }
            ),
        )

    async def async_step_add_button(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Add another logical KNX scene button."""
        errors: dict[str, str] = {}

        current_buttons = list(
            self.config_entry.data.get(CONF_BUTTONS, [])
        )
        next_button_number = len(current_buttons) + 1
        button_id = f"button_{next_button_number}"

        if user_input is not None:
            button_config = _create_button_config(
                user_input=user_input,
                button_id=button_id,
            )

            if not button_config.has_unique_knx_scene_numbers():
                errors["base"] = "duplicate_knx_scene_numbers"
            else:
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
            step_id="add_button",
            data_schema=_button_schema(
                default_button_name=(
                    f"{DEFAULT_BUTTON_NAME} "
                    f"{next_button_number}"
                ),
            ),
            errors=errors,
        )


def _button_schema(
    *,
    default_button_name: str,
) -> vol.Schema:
    """Return the schema for one logical scene button."""
    scene_selector = selector.EntitySelector(
        selector.EntitySelectorConfig(
            domain="scene",
        )
    )

    scene_number_schema = vol.All(
        vol.Coerce(int),
        vol.Range(
            min=MIN_KNX_SCENE_NUMBER,
            max=MAX_KNX_SCENE_NUMBER,
        ),
    )

    return vol.Schema(
        {
            vol.Required(
                CONF_BUTTON_NAME,
                default=default_button_name,
            ): str,
            vol.Required(CONF_SCENE_SELECTION_ADDRESS): str,
            vol.Required(CONF_TOGGLE_ADDRESS): str,
            vol.Optional(CONF_STATUS_LED_ADDRESS): str,
            vol.Required(
                _scene_entity_key(1)
            ): scene_selector,
            vol.Required(
                _knx_scene_number_key(1),
                default=1,
            ): scene_number_schema,
            vol.Required(
                _scene_entity_key(2)
            ): scene_selector,
            vol.Required(
                _knx_scene_number_key(2),
                default=2,
            ): scene_number_schema,
            vol.Required(
                _scene_entity_key(3)
            ): scene_selector,
            vol.Required(
                _knx_scene_number_key(3),
                default=3,
            ): scene_number_schema,
            vol.Required(
                _scene_entity_key(4)
            ): scene_selector,
            vol.Required(
                _knx_scene_number_key(4),
                default=4,
            ): scene_number_schema,
            vol.Required(
                CONF_NEUTRAL_SCENE_ENTITY_ID
            ): scene_selector,
        }
    )


def _create_button_config(
    *,
    user_input: dict[str, Any],
    button_id: str,
) -> SceneButtonConfig:
    """Create one immutable button configuration."""
    status_led_value = user_input.get(
        CONF_STATUS_LED_ADDRESS
    )

    status_led_address = (
        str(status_led_value).strip()
        if status_led_value not in (None, "")
        else None
    )

    mappings = tuple(
        SceneMapping(
            slot=slot,
            knx_scene_number=int(
                user_input[_knx_scene_number_key(slot)]
            ),
            scene_entity_id=str(
                user_input[_scene_entity_key(slot)]
            ),
        )
        for slot in SCENE_SLOTS
    )

    return SceneButtonConfig(
        button_id=button_id,
        name=str(user_input[CONF_BUTTON_NAME]).strip(),
        scene_selection_address=str(
            user_input[CONF_SCENE_SELECTION_ADDRESS]
        ).strip(),
        toggle_address=str(
            user_input[CONF_TOGGLE_ADDRESS]
        ).strip(),
        status_led_address=status_led_address,
        scene_mappings=mappings,
        neutral_scene_entity_id=str(
            user_input[CONF_NEUTRAL_SCENE_ENTITY_ID]
        ),
    )


def _scene_entity_key(slot: int) -> str:
    """Return the temporary form key for a scene entity."""
    return f"{CONF_SCENE_ENTITY_ID}_{slot}"


def _knx_scene_number_key(slot: int) -> str:
    """Return the temporary form key for a KNX scene number."""
    return f"{CONF_KNX_SCENE_NUMBER}_{slot}"