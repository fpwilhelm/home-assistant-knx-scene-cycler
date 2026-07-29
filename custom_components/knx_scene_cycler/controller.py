"""Business logic controller for the KNX Scene Cycler integration."""

from __future__ import annotations

import logging

from homeassistant.components.scene import DOMAIN as SCENE_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_ON
from homeassistant.core import HomeAssistant

from .models import SceneButtonConfig
from .runtime import ButtonState, SceneButtonRuntime

_LOGGER = logging.getLogger(__name__)


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
        """Activate one configured regular scene."""
        mapping = self._config.mapping_for_slot(slot)

        if mapping is None:
            raise ValueError(
                f"No scene mapping configured for slot {slot}."
            )

        await self._activate_homeassistant_scene(
            mapping.scene_entity_id
        )

        self._runtime.activate_scene(slot)

        _LOGGER.debug(
            "Activated scene slot %s (%s) for button %s",
            slot,
            mapping.scene_entity_id,
            self._config.button_id,
        )

    async def activate_neutral(self) -> None:
        """Activate the configured neutral scene."""
        await self._activate_homeassistant_scene(
            self._config.neutral_scene_entity_id
        )

        self._runtime.deactivate()

        _LOGGER.debug(
            "Activated neutral scene %s for button %s",
            self._config.neutral_scene_entity_id,
            self._config.button_id,
        )

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
            _LOGGER.debug(
                "Ignoring unmapped KNX scene number %s for button %s",
                knx_scene_number,
                self._config.button_id,
            )
            return

        await self.activate_scene(mapping.slot)

    async def restore_state(self) -> None:
        """Restore runtime state after Home Assistant startup."""
        if self._runtime.state is ButtonState.RESTORING:
            self._runtime.complete_restore()

    async def shutdown(self) -> None:
        """Release runtime resources."""
        return

    async def _activate_homeassistant_scene(
        self,
        scene_entity_id: str,
    ) -> None:
        """Activate one Home Assistant scene entity."""
        _LOGGER.debug(
            "Calling scene.turn_on for %s",
            scene_entity_id,
        )

        await self._hass.services.async_call(
            SCENE_DOMAIN,
            SERVICE_TURN_ON,
            {
                ATTR_ENTITY_ID: scene_entity_id,
            },
            blocking=True,
        )