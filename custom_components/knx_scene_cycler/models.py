"""Data models for the KNX Scene Cycler integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .const import (
    CONF_BUTTON_ID,
    CONF_BUTTON_NAME,
    CONF_KNX_SCENE_NUMBER,
    CONF_NEUTRAL_SCENE_ENTITY_ID,
    CONF_SCENE_ENTITY_ID,
    CONF_SCENE_MAPPINGS,
    CONF_SCENE_SELECTION_ADDRESS,
    CONF_SCENE_SLOT,
    CONF_STATUS_LED_ADDRESS,
    CONF_TOGGLE_ADDRESS,
    SCENE_SLOTS,
)


@dataclass(frozen=True, slots=True)
class SceneMapping:
    """Map one KNX scene number to one Home Assistant scene."""

    slot: int
    knx_scene_number: int
    scene_entity_id: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SceneMapping:
        """Create a scene mapping from stored config-entry data."""
        return cls(
            slot=int(data[CONF_SCENE_SLOT]),
            knx_scene_number=int(data[CONF_KNX_SCENE_NUMBER]),
            scene_entity_id=str(data[CONF_SCENE_ENTITY_ID]),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the scene mapping to config-entry data."""
        return {
            CONF_SCENE_SLOT: self.slot,
            CONF_KNX_SCENE_NUMBER: self.knx_scene_number,
            CONF_SCENE_ENTITY_ID: self.scene_entity_id,
        }


@dataclass(frozen=True, slots=True)
class SceneButtonConfig:
    """Persistent configuration for one logical KNX scene button."""

    button_id: str
    name: str

    scene_selection_address: str
    toggle_address: str
    status_led_address: str | None

    scene_mappings: tuple[SceneMapping, ...]
    neutral_scene_entity_id: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SceneButtonConfig:
        """Create a button configuration from stored config-entry data."""
        raw_status_led_address = data.get(CONF_STATUS_LED_ADDRESS)

        status_led_address = (
            str(raw_status_led_address).strip()
            if raw_status_led_address not in (None, "")
            else None
        )

        mappings = tuple(
            SceneMapping.from_dict(mapping)
            for mapping in data[CONF_SCENE_MAPPINGS]
        )

        return cls(
            button_id=str(data[CONF_BUTTON_ID]),
            name=str(data[CONF_BUTTON_NAME]),
            scene_selection_address=str(
                data[CONF_SCENE_SELECTION_ADDRESS]
            ),
            toggle_address=str(data[CONF_TOGGLE_ADDRESS]),
            status_led_address=status_led_address,
            scene_mappings=mappings,
            neutral_scene_entity_id=str(
                data[CONF_NEUTRAL_SCENE_ENTITY_ID]
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the button configuration to config-entry data."""
        return {
            CONF_BUTTON_ID: self.button_id,
            CONF_BUTTON_NAME: self.name,
            CONF_SCENE_SELECTION_ADDRESS: self.scene_selection_address,
            CONF_TOGGLE_ADDRESS: self.toggle_address,
            CONF_STATUS_LED_ADDRESS: self.status_led_address or "",
            CONF_SCENE_MAPPINGS: [
                mapping.to_dict() for mapping in self.scene_mappings
            ],
            CONF_NEUTRAL_SCENE_ENTITY_ID: self.neutral_scene_entity_id,
        }

    def mapping_for_slot(self, slot: int) -> SceneMapping | None:
        """Return the scene mapping for a regular scene slot."""
        return next(
            (
                mapping
                for mapping in self.scene_mappings
                if mapping.slot == slot
            ),
            None,
        )

    def mapping_for_knx_scene_number(
        self,
        knx_scene_number: int,
    ) -> SceneMapping | None:
        """Return the mapping for a received KNX scene number."""
        return next(
            (
                mapping
                for mapping in self.scene_mappings
                if mapping.knx_scene_number == knx_scene_number
            ),
            None,
        )

    def has_valid_scene_slots(self) -> bool:
        """Return whether the configuration contains all four scene slots."""
        configured_slots = {
            mapping.slot for mapping in self.scene_mappings
        }

        return configured_slots == set(SCENE_SLOTS)

    def has_unique_knx_scene_numbers(self) -> bool:
        """Return whether every regular scene uses a unique KNX number."""
        scene_numbers = [
            mapping.knx_scene_number
            for mapping in self.scene_mappings
        ]

        return len(scene_numbers) == len(set(scene_numbers))