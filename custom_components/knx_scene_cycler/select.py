"""Platform for select integration."""
import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the KNX Scene Cycler selects from a config entry."""
    config_data = hass.data["knx_scene_cycler"][config_entry.entry_id]
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
            identifiers={("knx_scene_cycler", config_entry.entry_id)},
        )

        self._ga_scene_select = self._config["ga_scene_select"]

        self._scene_to_knx = {
            self._config["scene_1"]: int(self._config["knx_num_1"]),
            self._config["scene_2"]: int(self._config["knx_num_2"]),
            self._config["scene_3"]: int(self._config["knx_num_3"]),
            self._config["scene_4"]: int(self._config["knx_num_4"]),
        }
        self._knx_to_scene = {v: k for k, v in self._scene_to_knx.items()}

        self._attr_options = ["Szene 1", "Szene 2", "Szene 3", "Szene 4"]
        
        self._name_to_entity = {
            "Szene 1": self._config["scene_1"],
            "Szene 2": self._config["scene_2"],
            "Szene 3": self._config["scene_3"],
            "Szene 4": self._config["scene_4"],
        }
        self._entity_to_name = {v: k for k, v in self._name_to_entity.items()}
        self._attr_current_option = "Szene 1"

        suffix = "" if self._index == 1 else f"_{self._index}"
        self._switch_entity_id = f"switch.knx_scene_cycler_szenenwahl{suffix}"

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

        # 1. Gewählte Home Assistant Szene aktivieren
        await self.hass.services.async_call(
            "scene", "turn_on", {"entity_id": scene_entity_id}, blocking=True
        )

        # 2. Zustand im Dropdown aktualisieren
        self._attr_current_option = option
        self.async_write_ha_state()

        # 3. Zugehörigen KNX-Szenenwert auf den Bus senden
        knx_value = self._scene_to_knx[scene_entity_id]
        await self.hass.services.async_call(
            "knx", "send", {"address": self._ga_scene_select, "payload": knx_value}
        )
        
        # 4. DIREKTER SYNCHRON-AUFRUF: Wir schalten die Schalter-Entität über den Zustands-Bus ein
        await self.hass.services.async_call(
            "switch", "turn_on", {"entity_id": self._switch_entity_id}, blocking=False
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
