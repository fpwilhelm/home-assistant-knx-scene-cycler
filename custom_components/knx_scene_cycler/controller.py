"""Business logic controller for the KNX Scene Cycler integration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant

from .models import SceneButtonConfig
from .runtime import SceneButtonRuntime


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
        """Activate one regular scene."""
        raise NotImplementedError

    async def activate_neutral(self) -> None:
        """Activate the neutral scene."""
        raise NotImplementedError

    async def toggle(self) -> None:
        """Toggle between neutral and the last active regular scene."""
        raise NotImplementedError

    async def handle_knx_scene_number(
        self,
        knx_scene_number: int,
    ) -> None:
        """Handle a received KNX scene number."""
        raise NotImplementedError

    async def restore_state(self) -> None:
        """Restore runtime state after Home Assistant startup."""
        raise NotImplementedError

    async def shutdown(self) -> None:
        """Release runtime resources."""
        return