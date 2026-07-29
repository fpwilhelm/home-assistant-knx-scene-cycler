"""Business logic controller for the KNX Scene Cycler integration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant

from .models import SceneButtonConfig
from .runtime import ButtonState, SceneButtonRuntime


class SceneButtonController:
    """Controller for one logical KNX scene button."""

    def __init__(
        self,
        hass: HomeAssistant,
        runtime: SceneButtonRuntime,
    ) -> None:
        """Initialize the controller."""
        self._hass = hass
        self._runtime = runtime
        self._config: SceneButtonConfig = runtime.config

    @property
    def runtime(self) -> SceneButtonRuntime:
        """Return the runtime state."""
        return self._runtime

    @property
    def config(self) -> SceneButtonConfig:
        """Return the immutable button configuration."""
        return self._config

    async def activate_scene(self, slot: int) -> None:
        """Activate one regular scene in the runtime state."""
        mapping = self._config.mapping_for_slot(slot)

        if mapping is None:
            raise ValueError(
                f"No scene mapping configured for slot {slot}."
            )

        self._runtime.activate_scene(slot)

    async def activate_neutral(self) -> None:
        """Activate the neutral state in the runtime."""
        self._runtime.deactivate()

    async def toggle(self) -> None:
        """Toggle between neutral and the last active regular scene."""
        if self._runtime.is_active:
            await self.activate_neutral()
            return

        slot = self._runtime.begin_restore()

        try:
            await self.activate_scene(slot)
        except Exception:
            self._runtime.deactivate()
            raise

    async def handle_knx_scene_number(
        self,
        knx_scene_number: int,
    ) -> None:
        """Handle a received KNX scene number."""
        mapping = self._config.mapping_for_knx_scene_number(
            knx_scene_number
        )

        if mapping is None:
            return

        await self.activate_scene(mapping.slot)

    async def restore_state(self) -> None:
        """Restore runtime state after Home Assistant startup."""
        if self._runtime.state is ButtonState.RESTORING:
            self._runtime.complete_restore()

    async def shutdown(self) -> None:
        """Release runtime resources."""
        return