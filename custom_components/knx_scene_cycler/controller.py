"""Business logic controller for the KNX Scene Cycler integration."""

from __future__ import annotations

import logging

from homeassistant.components.scene import DOMAIN as SCENE_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_ON
from homeassistant.core import HomeAssistant

from .models import SceneButtonConfig, SceneMapping
from .runtime import SceneButtonRuntime

_LOGGER = logging.getLogger(__name__)


class SceneButtonController:
    """Coordinate scene activation for one logical KNX scene button."""

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

    async def activate_scene_number(self, scene_number: int) -> None:
        """Activate one configured regular scene by KNX scene number."""
        mapping = self._mapping_for_scene_number(scene_number)

        if mapping.is_neutral:
            raise ValueError(
                f"Scene number {scene_number} is configured as neutral."
            )

        await self._activate_mapping(mapping)
        self._runtime.activate_scene_number(mapping.knx_scene_number)

        _LOGGER.debug(
            "Activated regular scene %s (%s, %s) for button %s",
            mapping.knx_scene_number,
            mapping.name,
            mapping.scene_entity_id,
            self._config.button_id,
        )

    async def activate_scene(self, slot: int) -> None:
        """Activate a regular scene by legacy slot during migration."""
        mapping = self._config.mapping_for_slot(slot)

        if mapping is None:
            raise ValueError(
                f"No scene mapping configured for legacy slot {slot}."
            )

        await self.activate_scene_number(mapping.knx_scene_number)

    async def activate_neutral(self) -> None:
        """Activate the configured neutral scene."""
        mapping = self._neutral_mapping()

        await self._activate_mapping(mapping)
        self._runtime.deactivate(mapping.knx_scene_number)

        _LOGGER.debug(
            "Activated neutral scene %s (%s, %s) for button %s",
            mapping.knx_scene_number,
            mapping.name,
            mapping.scene_entity_id,
            self._config.button_id,
        )

    async def toggle(self) -> None:
        """Toggle between neutral and the last active regular scene."""
        if self._runtime.is_active:
            await self.activate_neutral()
            return

        await self.activate_scene_number(
            self._runtime.last_regular_scene_number
        )

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

        if mapping.is_neutral:
            await self.activate_neutral()
            return

        await self.activate_scene_number(mapping.knx_scene_number)

    async def shutdown(self) -> None:
        """Release controller resources."""
        return

    def _mapping_for_scene_number(
        self,
        scene_number: int,
    ) -> SceneMapping:
        """Return a configured mapping or raise a descriptive error."""
        mapping = self._config.mapping_for_knx_scene_number(scene_number)

        if mapping is None:
            raise ValueError(
                f"No scene mapping configured for KNX scene number "
                f"{scene_number}."
            )

        return mapping

    def _neutral_mapping(self) -> SceneMapping:
        """Return the configured neutral mapping."""
        mapping = self._config.neutral_mapping()

        if mapping is None:
            raise ValueError(
                f"Button {self._config.button_id} has no neutral "
                "scene mapping."
            )

        return mapping

    async def _activate_mapping(
        self,
        mapping: SceneMapping,
    ) -> None:
        """Activate the Home Assistant scene of one mapping."""
        _LOGGER.debug(
            "Calling scene.turn_on for mapping %s (%s)",
            mapping.mapping_id,
            mapping.scene_entity_id,
        )

        await self._hass.services.async_call(
            SCENE_DOMAIN,
            SERVICE_TURN_ON,
            {
                ATTR_ENTITY_ID: mapping.scene_entity_id,
            },
            blocking=True,
        )
