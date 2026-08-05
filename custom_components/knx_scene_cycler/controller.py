"""Business logic controller for the KNX Scene Cycler integration."""

from __future__ import annotations

import logging

from homeassistant.components.scene import DOMAIN as SCENE_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_TURN_ON
from homeassistant.core import HomeAssistant

from .models import (
    SceneButtonConfig,
    SceneMapping,
    SceneMappingType,
    TriggerMode,
)
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
        mapping = self._config.mapping_for_knx_scene_number(
            scene_number
        )

        if mapping is None:
            raise ValueError(
                "No scene mapping configured for KNX scene number "
                f"{scene_number}."
            )

        if mapping.mapping_type is SceneMappingType.NEUTRAL:
            raise ValueError(
                f"Scene number {scene_number} is configured as neutral."
            )

        await self._activate_scene(mapping)
        self._runtime.activate_scene_number(scene_number)

        _LOGGER.debug(
            "Activated regular scene %s (%s, %s) for button %s",
            scene_number,
            mapping.name,
            mapping.scene_entity_id,
            self._config.button_id,
        )

    async def activate_neutral(self) -> None:
        """Activate the configured neutral scene."""
        mapping = self._config.neutral_mapping

        await self._activate_scene(mapping)
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
    ) -> bool:
        """Handle a received KNX scene number.

        Return whether a repeated neutral-scene telegram restored the
        last regular scene.
        """
        mapping = self._config.mapping_for_knx_scene_number(
            knx_scene_number
        )

        if mapping is None:
            _LOGGER.debug(
                "Ignoring unmapped KNX scene number %s for button %s",
                knx_scene_number,
                self._config.button_id,
            )
            return False

        if mapping.mapping_type is SceneMappingType.NEUTRAL:
            if (
                self._runtime.current_scene_number
                == mapping.knx_scene_number
                and not self._runtime.is_active
            ):
                await self.activate_scene_number(
                    self._runtime.last_regular_scene_number
                )
                return True

            await self.activate_neutral()
            return False

        if (
            self._config.trigger_mode is TriggerMode.NEUTRAL_SCENE
            and not self._runtime.is_active
            and self._runtime.current_scene_number
            == self._config.neutral_mapping.knx_scene_number
        ):
            await self.activate_scene_number(
                self._runtime.last_regular_scene_number
            )
            return True

        await self.activate_scene_number(knx_scene_number)
        return False

    async def shutdown(self) -> None:
        """Release controller resources."""
        return

    async def _activate_scene(
        self,
        mapping: SceneMapping,
    ) -> None:
        """Activate the Home Assistant scene referenced by a mapping."""
        _LOGGER.debug(
            "Calling scene.turn_on for mapping %s (%s)",
            mapping.mapping_id,
            mapping.scene_entity_id,
        )

        await self._activate_homeassistant_scene(
            mapping.scene_entity_id
        )

    async def _activate_homeassistant_scene(
        self,
        scene_entity_id: str,
    ) -> None:
        """Activate one Home Assistant scene entity."""
        await self._hass.services.async_call(
            SCENE_DOMAIN,
            SERVICE_TURN_ON,
            {
                ATTR_ENTITY_ID: scene_entity_id,
            },
            blocking=True,
        )
