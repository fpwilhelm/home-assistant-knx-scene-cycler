"""Hub for managing KNX Scene Cycler button controllers."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Iterable, Iterator
import logging

from homeassistant.core import Event, HomeAssistant, callback

from .const import KNX_LED_OFF, KNX_LED_ON
from .controller import SceneButtonController
from .knx_event_manager import KNXEventRegistrationManager
from .models import SceneButtonConfig
from .runtime import SceneButtonRuntime

_LOGGER = logging.getLogger(__name__)

KNX_DIRECTION_INCOMING = "Incoming"
KNX_TELEGRAM_GROUP_VALUE_WRITE = "GroupValueWrite"


class KNXSceneCyclerHub:
    """Manage all scene button controllers of one config entry."""

    def __init__(
        self,
        hass: HomeAssistant,
        button_configs: Iterable[SceneButtonConfig],
    ) -> None:
        """Initialize the hub and its button controllers."""
        self._hass = hass
        self._controllers: dict[str, SceneButtonController] = {}
        self._controller_locks: dict[str, asyncio.Lock] = {}
        self._event_manager: KNXEventRegistrationManager | None = None
        self._remove_event_listener: Callable[[], None] | None = None
        self._scene_addresses: set[str] = set()
        self._toggle_addresses: set[str] = set()

        for button_config in button_configs:
            self.add_button(button_config)

    @property
    def controllers(self) -> tuple[SceneButtonController, ...]:
        """Return all button controllers."""
        return tuple(self._controllers.values())

    @property
    def button_ids(self) -> tuple[str, ...]:
        """Return all configured button IDs."""
        return tuple(self._controllers)

    def __iter__(self) -> Iterator[SceneButtonController]:
        """Iterate over all button controllers."""
        return iter(self._controllers.values())

    def __len__(self) -> int:
        """Return the number of configured buttons."""
        return len(self._controllers)

    def add_button(
        self,
        button_config: SceneButtonConfig,
    ) -> SceneButtonController:
        """Create and register a controller for one scene button."""
        button_id = button_config.button_id

        if button_id in self._controllers:
            raise ValueError(
                f"Button ID {button_id!r} is already registered."
            )

        runtime = SceneButtonRuntime(config=button_config)
        controller = SceneButtonController(
            hass=self._hass,
            runtime=runtime,
        )

        self._controllers[button_id] = controller
        self._controller_locks[button_id] = asyncio.Lock()

        return controller

    async def async_start(
        self,
        event_manager: KNXEventRegistrationManager,
    ) -> None:
        """Register KNX inputs and start the central event listener."""
        self._scene_addresses = {
            controller.config.scene_selection_address
            for controller in self._controllers.values()
        }
        self._toggle_addresses = {
            controller.config.toggle_address
            for controller in self._controllers.values()
            if controller.config.toggle_address is not None
        }

        await event_manager.async_acquire(
            scene_addresses=self._scene_addresses,
            toggle_addresses=self._toggle_addresses,
        )
        self._event_manager = event_manager
        self._remove_event_listener = self._hass.bus.async_listen(
            "knx_event",
            self._async_handle_knx_event,
        )

    def get_controller(
        self,
        button_id: str,
    ) -> SceneButtonController:
        """Return the controller for one configured button."""
        try:
            return self._controllers[button_id]
        except KeyError as err:
            raise KeyError(
                f"Unknown KNX Scene Cycler button ID: {button_id!r}."
            ) from err

    def remove_button(
        self,
        button_id: str,
    ) -> SceneButtonController:
        """Remove and return one registered button controller."""
        try:
            controller = self._controllers.pop(button_id)
        except KeyError as err:
            raise KeyError(
                f"Unknown KNX Scene Cycler button ID: {button_id!r}."
            ) from err
        self._controller_locks.pop(button_id, None)
        return controller

    async def async_shutdown(self) -> None:
        """Shut down all button controllers."""
        if self._remove_event_listener is not None:
            self._remove_event_listener()
            self._remove_event_listener = None

        for controller in self._controllers.values():
            await controller.shutdown()

        if self._event_manager is not None:
            await self._event_manager.async_release(
                scene_addresses=self._scene_addresses,
                toggle_addresses=self._toggle_addresses,
            )
            self._event_manager = None

    @callback
    def _async_handle_knx_event(self, event: Event) -> None:
        """Route one KNX event to every matching controller."""
        if (
            event.data.get("direction") != KNX_DIRECTION_INCOMING
            or event.data.get("telegramtype")
            != KNX_TELEGRAM_GROUP_VALUE_WRITE
        ):
            return

        destination = event.data.get("destination")
        if not isinstance(destination, str):
            return

        scene_number = self._extract_integer_value(event)

        for controller in self._controllers.values():
            config = controller.config

            if destination == config.scene_selection_address:
                if scene_number is None:
                    continue
                self._hass.async_create_task(
                    self._async_handle_scene_selection(
                        controller,
                        scene_number,
                    ),
                    f"KNX scene selection for {config.button_id}",
                )
                continue

            if destination == config.toggle_address:
                self._hass.async_create_task(
                    self._async_handle_toggle(controller),
                    f"KNX scene toggle for {config.button_id}",
                )

    async def _async_handle_scene_selection(
        self,
        controller: SceneButtonController,
        scene_number: int,
    ) -> None:
        """Activate a mapped scene received through KNX."""
        config = controller.config
        mapping = config.mapping_for_knx_scene_number(scene_number)

        if mapping is None:
            _LOGGER.debug(
                "Ignoring unmapped KNX scene number %s for button %s",
                scene_number,
                config.button_id,
            )
            return

        async with self._controller_locks[config.button_id]:
            restore_from_neutral = (
                await controller.handle_knx_scene_number(scene_number)
            )

            if restore_from_neutral:
                await self._async_send_scene_feedback(controller)

            await self._async_send_status_led(controller)

    async def _async_handle_toggle(
        self,
        controller: SceneButtonController,
    ) -> None:
        """Handle a KNX toggle impulse."""
        async with self._controller_locks[controller.config.button_id]:
            await controller.toggle()
            await self._async_send_status_led(controller)

    async def _async_send_status_led(
        self,
        controller: SceneButtonController,
    ) -> None:
        """Send one controller's active state to its KNX status LED."""
        status_led_address = controller.config.status_led_address
        if status_led_address is None:
            return

        payload = (
            KNX_LED_ON
            if controller.runtime.is_active
            else KNX_LED_OFF
        )
        await self._hass.services.async_call(
            "knx",
            "send",
            {
                "address": status_led_address,
                "payload": payload,
            },
            blocking=True,
        )

    async def _async_send_scene_feedback(
        self,
        controller: SceneButtonController,
    ) -> None:
        """Synchronize a physical scene cycle after neutral restore."""
        await self._hass.services.async_call(
            "knx",
            "send",
            {
                "address": (
                    controller.config.scene_selection_address
                ),
                "payload": (
                    controller.runtime.last_regular_scene_number
                ),
                "type": "scene_number",
                "response": False,
            },
            blocking=True,
        )

    @staticmethod
    def _extract_integer_value(event: Event) -> int | None:
        """Extract an integer value from a KNX event."""
        raw_value = event.data.get("value")
        if raw_value is None:
            raw_value = event.data.get("data")

        try:
            return int(raw_value)
        except (TypeError, ValueError):
            return None
