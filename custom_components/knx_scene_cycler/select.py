"""Platform for select integration."""
import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_GA_SCENE_SELECT,
    CONF_SCENE_1,
    CONF_SCENE_2,
    CONF_SCENE_3,
    CONF_SCENE_4,
    CONF_KNX_NUM_1,
    CONF_KNX_NUM_2,
    CONF_KNX_NUM_3,
    CONF_KNX_NUM_4,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the KNX Scene Cycler selects from a config entry."""
    config_data = hass.data[DOMAIN][config_entry.entry_id]
    functions = config_data.get("functions", [])

    selects = []
    for idx, func_config in enumerate(functions):
        selects.append(
            KnxSceneCyclerSelect(hass, config_entry, func_config, idx + 1)
        )

    async_add_entities(selects)


class KnxSceneCyclerSelect(SelectEntity):
    """Representation of a KNX Scene Cycler Select Entity for scene selection."""

    _attr_has_entity_name = True

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, func_config: dict[str, Any], index: int
    ) -> None:
        """Initialize the select entity."""
        self.hass = hass
        self._config = func_config
        self._entry_id = config_entry.entry_id
        self._index = index

        self._attr_name = "Szene" if index == 1 else f"Szene {index}"
        self._attr_unique_id = f"{config_entry.entry_id}_select_{index}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
        )

        self._ga_scene_select = self._config[CONF_GA_SCENE_SELECT]

        self._scene_to_knx = {
            self._config[CONF_SCENE_1]: int(self._config[CONF_KNX_NUM_1]),
            self._config[CONF_SCENE_2]: int(self._config[CONF_KNX_NUM_2]),
            self._config[CONF_SCENE_3]: int(self._config[CONF_KNX_NUM_3]),
            self._config[CONF_SCENE_4]: int(self._config[CONF_KNX_NUM_4]),
        }
        self._knx_to_scene = {v: k for k, v in self._scene_to_knx.items()}

        self._attr_options = ["Szene 1", "Szene 2", "Szene 3", "Szene 4"]
        
        self._name_to_entity = {
            "Szene 1": self._config[CONF_SCENE_1],
            "Szene 2": self._config[CONF_SCENE_2],
            "Szene 3": self._config[CONF_SCENE_3],
            "Szene 4": self._config[CONF_SCENE_4],
        }
        self._entity_to_name = {v: k for k, v in self._name_to_entity.items()}
        self._attr_current_option = "Szene 1"

        # Entspricht der unique_id des gekoppelten Schalters
        self._target_switch_unique_id = f"{config_entry.entry_id}_button_{index}"

    async def async_added_to_hass(self) -> None:
        """Register HA bus listeners when added to hass."""
        self.async_on_remove(
            self.hass.bus.async_listen("knx_event", self._async_handle_knx_event)
        )

    async def async_select_option(self, option: str) -> None:
        """Triggered when user selects a scene from the dropdown in UI."""
        if option not in self._name_to_entity:
            return

        scene_entity_id = self._name_to_entity[option]

        await self.hass.services.async_call(
            "scene", "turn_on", {"entity_id": scene_entity_id}, blocking=True
        )

        self._attr_current_option = option
        self.async_write_ha_state()

        knx_value = self._scene_to_knx[scene_entity_id]
        await self.hass.services.async_call(
            "knx", "send", {"address": self._ga_scene_select, "payload": knx_value}
        )
        
        # Dynamisches Auflösen der echten Schalter-Entity-ID über die Registry
        ent_reg = er.async_get(self.hass)
        switch_entity_id = ent_reg.async_get_entity_id("switch", DOMAIN, self._target_switch_unique_id)
        
        if switch_entity_id:
            await self.hass.services.async_call(
                "switch", "turn_on", {"entity_id": switch_entity_id}, blocking=False
            )

    @callback
    def _async_handle_knx_event(self, event: Any) -> None:
        """Handle incoming Home Assistant knx_event."""
        destination = event.data.get("destination")

        if not destination or destination != self._ga_scene_select:
            return

        value = event.data.get("value")
        if value is None:
            return

        val_int = int(value)
        if val_int in self._knx_to_scene:
            scene_entity = self._knx_to_scene[val_int]
            if scene_entity in self._entity_to_name:
                self._attr_current_option = self._entity_to_name[scene_entity]
                self.async_write_ha_state()
