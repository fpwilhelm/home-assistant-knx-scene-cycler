"""Switch platform for the KNX Scene Cycler integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    KNX_LED_OFF,
    KNX_LED_ON,
    KNX_TOGGLE_VALUE,
)
from .controller import SceneButtonController
from .hub import KNXSceneCyclerHub

_LOGGER = logging.getLogger(__name__)

DATA_HUB = "hub"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KNX Scene Cycler switch entities."""
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    hub = entry_data.get(DATA_HUB)

    if not isinstance(hub, KNXSceneCyclerHub):
        raise RuntimeError(
            "KNX Scene Cycler hub is unavailable for config entry "
            f"{config_entry.entry_id}."
        )

    async_add_entities(
        KnxSceneCyclerSwitch(
            config_entry=config_entry,
            controller=controller,
        )
        for controller in hub.controllers
    )


class KnxSceneCyclerSwitch(SwitchEntity):
    """Represent one logical KNX scene button as a switch."""

    _attr_has_entity_name = True

    def __init__(
        self,
        config_entry: ConfigEntry,
        controller: SceneButtonController,
    ) -> None:
        """Initialize the switch entity."""
        self._controller = controller
        self._config = controller.config
        self._runtime = controller.runtime

        self._attr_name = self._config.name
        self._attr_unique_id = (
            f"{config_entry.entry_id}_{self._config.button_id}_switch"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
        )

    @property
    def is_on(self) -> bool:
        """Return whether a regular scene is active."""
        return self._runtime.is_active

    @property
    def available(self) -> bool:
        """Return whether the button runtime is available."""
        return self._runtime.is_available

    async def async_added_to_hass(self) -> None:
        """Register runtime and KNX event listeners."""
        await super().async_added_to_hass()

        self.async_on_remove(
            self._runtime.add_listener(
                self._async_handle_runtime_update
            )
        )
        self.async_on_remove(
            self.hass.bus.async_listen(
                "knx_event",
                self._async_handle_knx_event,
            )
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Restore the last active regular scene."""
        await self._controller.activate_scene_number(
            self._runtime.last_regular_scene_number
        )
        await self._async_send_status_led(
            is_active=self._runtime.is_active
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Activate the configured neutral scene."""
        await self._controller.activate_neutral()
        await self._async_send_status_led(
            is_active=self._runtime.is_active
        )

    @callback
    def _async_handle_runtime_update(self) -> None:
        """Write entity state after a runtime change."""
        self.async_write_ha_state()

    @callback
    def _async_handle_knx_event(
        self,
        event: Event,
    ) -> None:
        """Handle an incoming Home Assistant KNX event."""
        destination = event.data.get("destination")

        if destination == self._config.scene_selection_address:
            scene_number = self._extract_integer_value(event)

            if scene_number is None:
                return

            self.hass.async_create_task(
                self._async_handle_scene_selection(scene_number),
                f"KNX scene selection for {self._config.button_id}",
            )
            return

        if destination != self._config.toggle_address:
            return

        toggle_value = self._extract_integer_value(event)

        if toggle_value != KNX_TOGGLE_VALUE:
            return

        self.hass.async_create_task(
            self._async_handle_toggle(),
            f"KNX scene toggle for {self._config.button_id}",
        )

    async def _async_handle_scene_selection(
        self,
        scene_number: int,
    ) -> None:
        """Activate a mapped scene received through KNX."""
        mapping = self._config.mapping_for_knx_scene_number(
            scene_number
        )

        if mapping is None:
            _LOGGER.debug(
                "Ignoring unmapped KNX scene number %s for button %s",
                scene_number,
                self._config.button_id,
            )
            return

        await self._controller.handle_knx_scene_number(scene_number)
        await self._async_send_status_led(
            is_active=self._runtime.is_active
        )

    async def _async_handle_toggle(self) -> None:
        """Handle a KNX toggle impulse."""
        await self._controller.toggle()
        await self._async_send_status_led(
            is_active=self._runtime.is_active
        )

    async def _async_send_status_led(
        self,
        *,
        is_active: bool,
    ) -> None:
        """Send the current active state to the KNX status LED."""
        status_led_address = self._config.status_led_address

        if status_led_address is None:
            return

        payload = KNX_LED_ON if is_active else KNX_LED_OFF

        await self.hass.services.async_call(
            "knx",
            "send",
            {
                "address": status_led_address,
                "payload": payload,
            },
            blocking=True,
        )

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
