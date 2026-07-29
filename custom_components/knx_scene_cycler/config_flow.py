"""Config flow for KNX Scene Cycler integration."""
import logging
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_DEVICE_NAME,
    CONF_GA_SCENE_SELECT,
    CONF_GA_SWITCH,
    CONF_GA_STATUS_LED,
    CONF_SCENE_1,
    CONF_SCENE_2,
    CONF_SCENE_3,
    CONF_SCENE_4,
    CONF_SCENE_5_NEUTRAL,
    CONF_KNX_NUM_1,
    CONF_KNX_NUM_2,
    CONF_KNX_NUM_3,
    CONF_KNX_NUM_4,
)

_LOGGER = logging.getLogger(__name__)

class KnxSceneCyclerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for KNX Scene Cycler."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.device_name: str = ""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 1: Handle the initial step to name the device."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.device_name = user_input[CONF_DEVICE_NAME]
            return await self.async_step_function()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_DEVICE_NAME): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_function(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2: Handle adding the first button to the device."""
        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(
                title=self.device_name,
                data={
                    CONF_DEVICE_NAME: self.device_name,
                    "functions": [user_input],
                },
            )

        scene_selector = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="scene")
        )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_GA_SCENE_SELECT): str,
                vol.Required(CONF_GA_SWITCH): str,
                vol.Optional(CONF_GA_STATUS_LED): str,
                
                vol.Required(CONF_SCENE_1): scene_selector,
                vol.Required(CONF_KNX_NUM_1, default=1): vol.All(vol.Coerce(int), vol.Range(min=1, max=64)),
                
                vol.Required(CONF_SCENE_2): scene_selector,
                vol.Required(CONF_KNX_NUM_2, default=2): vol.All(vol.Coerce(int), vol.Range(min=1, max=64)),
                
                vol.Required(CONF_SCENE_3): scene_selector,
                vol.Required(CONF_KNX_NUM_3, default=3): vol.All(vol.Coerce(int), vol.Range(min=1, max=64)),
                
                vol.Required(CONF_SCENE_4): scene_selector,
                vol.Required(CONF_KNX_NUM_4, default=4): vol.All(vol.Coerce(int), vol.Range(min=1, max=64)),
                
                vol.Required(CONF_SCENE_5_NEUTRAL): scene_selector,
            }
        )

        return self.async_show_form(
            step_id="function", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow to add more buttons later."""
        return KnxSceneCyclerOptionsFlowHandler(config_entry)


class KnxSceneCyclerOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow to dynamically add multiple buttons later."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Intermediate menu to choose an action."""
        if user_input is not None:
            if user_input.get("action") == "add":
                return await self.async_step_add_button()
            return self.async_create_entry(title="", data={})

        data_schema = vol.Schema(
            {
                vol.Required("action", default="add"): vol.In(
                    {"add": "Neue Taste/Funktion hinzufügen", "finish": "Konfiguration beenden"}
                )
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)

    async def async_step_add_button(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle adding the extra button parameters."""
        if user_input is not None:
            # WICHTIG: Wir holen uns das originale DATA-Dictionary
            current_data = dict(self.config_entry.data)
            old_functions = list(current_data.get("functions", []))
            
            # Neue Taste an die DATA-Struktur anhängen
            old_functions.append(user_input)
            current_data["functions"] = old_functions
            
            # Wir überschreiben direkt das DATA-Feld des Entries. Das ist absolut stabil!
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=current_data
            )
            return self.async_create_entry(title="", data={})

        scene_selector = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="scene")
        )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_GA_SCENE_SELECT): str,
                vol.Required(CONF_GA_SWITCH): str,
                vol.Optional(CONF_GA_STATUS_LED): str,
                vol.Required(CONF_SCENE_1): scene_selector,
                vol.Required(CONF_KNX_NUM_1, default=1): vol.All(vol.Coerce(int), vol.Range(min=1, max=64)),
                vol.Required(CONF_SCENE_2): scene_selector,
                vol.Required(CONF_KNX_NUM_2, default=2): vol.All(vol.Coerce(int), vol.Range(min=1, max=64)),
                vol.Required(CONF_SCENE_3): scene_selector,
                vol.Required(CONF_KNX_NUM_3, default=3): vol.All(vol.Coerce(int), vol.Range(min=1, max=64)),
                vol.Required(CONF_SCENE_4): scene_selector,
                vol.Required(CONF_KNX_NUM_4, default=4): vol.All(vol.Coerce(int), vol.Range(min=1, max=64)),
                vol.Required(CONF_SCENE_5_NEUTRAL): scene_selector,
            }
        )

        return self.async_show_form(step_id="add_button", data_schema=data_schema)
