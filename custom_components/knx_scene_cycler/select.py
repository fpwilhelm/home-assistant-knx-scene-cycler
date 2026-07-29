"""Select platform for the KNX Scene Cycler integration."""

from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .controller import SceneButtonController
from .hub import KNXSceneCyclerHub

_LOGGER = logging.getLogger(__name__)

DATA_HUB = "hub"

OPTION_PREFIX = "Scene "


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KNX Scene Cycler select entities."""
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    hub = entry_data.get(DATA_HUB)

    if not isinstance(hub, KNXSceneCyclerHub):
        raise RuntimeError(
            "KNX Scene Cycler hub is unavailable for config entry "
            f"{config_entry.entry_id}."
        )

    async_add_entities(
        KnxSceneCyclerSelect(
            config_entry=config_entry,
            controller=controller,
        )
        for controller in hub.controllers
    )


class KnxSceneCyclerSelect(SelectEntity):
    """Represent the scene selection for one logical KNX button."""

    _attr_has_entity_name = True

    def __init__(
        self,
        config_entry: ConfigEntry,
        controller: SceneButtonController,
    ) -> None:
        """Initialize the select entity."""
        self._controller = controller
        self._config = controller.config
        self._runtime = controller.runtime

        self._slot_by_option = {
            self._option_for_slot(mapping.slot): mapping.slot
            for mapping in self._config.scene_mappings
        }
        self._option_by_slot = {
            slot: option
            for option, slot in self._slot_by_option.items()
        }

        self._attr_name = f"{self._config.name} Scene"
        self._attr_unique_id = (
            f"{config_entry.entry_id}_{self._config.button_id}_select"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
        )
        self._attr_options = [
            self._option_for_slot(mapping.slot)
            for mapping in sorted(
                self._config.scene_mappings,
                key=lambda mapping: mapping.slot,
            )
        ]

    @property
    def current_option(self) -> str | None:
        """Return the currently selected regular scene."""
        return self._option_by_slot.get(
            self._runtime.last_active_scene_slot
        )

    @property
    def available(self) -> bool:
        """Return whether the button runtime is available."""
        return self._runtime.is_available

    async def async_added_to_hass(self) -> None:
        """Register the KNX event listener."""
        await super().async_added_to_hass()

        self.async_on_remove(
            self.hass.bus.async_listen(
                "knx_event",
                self._async_handle_knx_event,
            )
        )

    async def async_select_option(self, option: str) -> None:
        """Activate the selected scene."""
        slot = self._slot_by_option.get(option)

        if slot is None:
            raise ValueError(
                f"Unsupported scene option: {option!r}."
            )

        mapping = self._config.mapping_for_slot(slot)

        if mapping is None:
            raise ValueError(
                f"No scene mapping configured for slot {slot}."
            )

        await self._controller.activate_scene(slot)

        await self.hass.services.async_call(
            "knx",
            "send",
            {
                "address": self._config.scene_selection_address,
                "payload": mapping.knx_scene_number,
            },
            blocking=True,
        )

        self.async_write_ha_state()

    @callback
    def _async_handle_knx_event(
        self,
        event: Event,
    ) -> None:
        """Update the select state after a KNX scene telegram."""
        destination = event.data.get("destination")

        if destination != self._config.scene_selection_address:
            return

        knx_scene_number = self._extract_integer_value(event)

        if knx_scene_number is None:
            return

        mapping = self._config.mapping_for_knx_scene_number(
            knx_scene_number
        )

        if mapping is None:
            _LOGGER.debug(
                "Ignoring unmapped KNX scene number %s for button %s",
                knx_scene_number,
                self._config.button_id,
            )
            return

        self.async_write_ha_state()

    @staticmethod
    def _option_for_slot(slot: int) -> str:
        """Return the select option for a regular scene slot."""
        return f"{OPTION_PREFIX}{slot}"

    @staticmethod
    def _extract_integer_value(
        event: Event,
    ) -> int | None:
        """Extract an integer value from a KNX event."""
        raw_value = event.data.get("value")

        if raw_value is None:
            raw_value = event.data.get("data")

        try:
            return int(raw_value)
        except (TypeError, ValueError):
            return None