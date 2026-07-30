"""Data models for the KNX Scene Cycler integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .const import (
    CONF_BUTTON_ID,
    CONF_BUTTON_NAME,
    CONF_IS_NEUTRAL,
    CONF_KNX_SCENE_NUMBER,
    CONF_LED_COLOR_VALUE,
    CONF_MAPPING_ID,
    CONF_MAPPING_NAME,
    CONF_NEUTRAL_SCENE_ENTITY_ID,
    CONF_SCENE_ENTITY_ID,
    CONF_SCENE_MAPPINGS,
    CONF_SCENE_SELECTION_ADDRESS,
    CONF_SCENE_SLOT,
    CONF_STATUS_LED_ADDRESS,
    CONF_TOGGLE_ADDRESS,
    MAX_KNX_SCENE_NUMBER,
    MAX_LED_COLOR_VALUE,
    MAX_SCENE_MAPPINGS_PER_BUTTON,
    MIN_KNX_SCENE_NUMBER,
    MIN_LED_COLOR_VALUE,
    REQUIRED_REGULAR_SCENE_MAPPINGS,
    SCENE_SLOTS,
)


@dataclass(frozen=True, slots=True)
class SceneMapping:
    """Map one KNX scene number to one Home Assistant scene.

    ``mapping_id`` is the stable identity of a mapping. ``slot`` is retained
    temporarily as a compatibility field while the controller, runtime and
    entity platforms are migrated away from the former four-slot model.
    """

    slot: int | None
    knx_scene_number: int
    scene_entity_id: str
    mapping_id: str
    name: str
    led_color_value: int | None = None
    is_neutral: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SceneMapping:
        """Create a scene mapping from stored config-entry data."""
        slot = _optional_int(data.get(CONF_SCENE_SLOT))
        knx_scene_number = int(data[CONF_KNX_SCENE_NUMBER])
        mapping_id = str(
            data.get(
                CONF_MAPPING_ID,
                _legacy_mapping_id(slot, knx_scene_number),
            )
        )

        return cls(
            slot=slot,
            knx_scene_number=knx_scene_number,
            scene_entity_id=str(data[CONF_SCENE_ENTITY_ID]),
            mapping_id=mapping_id,
            name=str(
                data.get(
                    CONF_MAPPING_NAME,
                    _legacy_mapping_name(slot, knx_scene_number),
                )
            ),
            led_color_value=_optional_int(
                data.get(CONF_LED_COLOR_VALUE)
            ),
            is_neutral=bool(data.get(CONF_IS_NEUTRAL, False)),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the scene mapping to config-entry data."""
        data: dict[str, Any] = {
            CONF_MAPPING_ID: self.mapping_id,
            CONF_MAPPING_NAME: self.name,
            CONF_KNX_SCENE_NUMBER: self.knx_scene_number,
            CONF_SCENE_ENTITY_ID: self.scene_entity_id,
            CONF_LED_COLOR_VALUE: self.led_color_value,
            CONF_IS_NEUTRAL: self.is_neutral,
        }

        if self.slot is not None:
            data[CONF_SCENE_SLOT] = self.slot

        return data

    def has_valid_knx_scene_number(self) -> bool:
        """Return whether the KNX scene number is within the DPT range."""
        return (
            MIN_KNX_SCENE_NUMBER
            <= self.knx_scene_number
            <= MAX_KNX_SCENE_NUMBER
        )

    def has_valid_led_color_value(self) -> bool:
        """Return whether the optional LED color value is valid."""
        return self.led_color_value is None or (
            MIN_LED_COLOR_VALUE
            <= self.led_color_value
            <= MAX_LED_COLOR_VALUE
        )


@dataclass(frozen=True, slots=True)
class SceneButtonConfig:
    """Persistent configuration for one logical KNX scene button.

    ``neutral_scene_entity_id`` remains available as a temporary compatibility
    field. It will be removed after the config flow and controller use the
    neutral ``SceneMapping`` exclusively.
    """

    button_id: str
    name: str

    scene_selection_address: str
    toggle_address: str
    status_led_address: str | None

    scene_mappings: tuple[SceneMapping, ...]
    neutral_scene_entity_id: str

    _scene_number_index: Mapping[int, SceneMapping] = field(
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        """Build immutable runtime indexes from the stored mapping list."""
        object.__setattr__(
            self,
            "_scene_number_index",
            MappingProxyType(
                {
                    mapping.knx_scene_number: mapping
                    for mapping in self.scene_mappings
                }
            ),
        )

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
        """Return a mapping by legacy scene slot during migration."""
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
        """Return a mapping for a received KNX scene number."""
        return self._scene_number_index.get(knx_scene_number)

    def neutral_mapping(self) -> SceneMapping | None:
        """Return the explicitly marked neutral mapping, if configured."""
        return next(
            (
                mapping
                for mapping in self.scene_mappings
                if mapping.is_neutral
            ),
            None,
        )

    def regular_mappings(self) -> tuple[SceneMapping, ...]:
        """Return all mappings that are not marked as neutral."""
        return tuple(
            mapping
            for mapping in self.scene_mappings
            if not mapping.is_neutral
        )

    def has_valid_scene_slots(self) -> bool:
        """Return whether all legacy scene slots remain configured."""
        configured_slots = {
            mapping.slot
            for mapping in self.scene_mappings
            if not mapping.is_neutral and mapping.slot is not None
        }

        return set(SCENE_SLOTS).issubset(configured_slots)

    def has_required_regular_mappings(self) -> bool:
        """Return whether at least four regular mappings exist."""
        return len(self.regular_mappings()) >= REQUIRED_REGULAR_SCENE_MAPPINGS

    def has_allowed_mapping_count(self) -> bool:
        """Return whether the configured mapping count is supported."""
        return (
            REQUIRED_REGULAR_SCENE_MAPPINGS + 1
            <= len(self.scene_mappings)
            <= MAX_SCENE_MAPPINGS_PER_BUTTON
        )

    def has_unique_mapping_ids(self) -> bool:
        """Return whether every mapping has a unique stable ID."""
        mapping_ids = [mapping.mapping_id for mapping in self.scene_mappings]
        return len(mapping_ids) == len(set(mapping_ids))

    def has_unique_knx_scene_numbers(self) -> bool:
        """Return whether every mapping uses a unique KNX scene number."""
        return len(self._scene_number_index) == len(self.scene_mappings)

    def has_single_neutral_mapping(self) -> bool:
        """Return whether exactly one mapping is marked as neutral."""
        return sum(
            mapping.is_neutral for mapping in self.scene_mappings
        ) == 1

    def has_valid_mapping_values(self) -> bool:
        """Return whether scene numbers and LED values are valid."""
        return all(
            mapping.has_valid_knx_scene_number()
            and mapping.has_valid_led_color_value()
            for mapping in self.scene_mappings
        )


def _legacy_mapping_id(
    slot: int | None,
    knx_scene_number: int,
) -> str:
    """Create a deterministic ID for config data without a mapping ID."""
    if slot is not None:
        return f"mapping_{slot}"

    return f"scene_{knx_scene_number}"


def _legacy_mapping_name(
    slot: int | None,
    knx_scene_number: int,
) -> str:
    """Create a readable name for config data without a mapping name."""
    if slot is not None:
        return f"Scene {slot}"

    return f"Scene {knx_scene_number}"


def _optional_int(value: Any) -> int | None:
    """Return an optional stored integer value."""
    if value in (None, ""):
        return None

    return int(value)
