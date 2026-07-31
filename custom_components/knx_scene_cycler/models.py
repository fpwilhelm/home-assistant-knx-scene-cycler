"""Data models for the KNX Scene Cycler integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping

from .const import (
    CONF_BUTTON_ID,
    CONF_BUTTON_NAME,
    CONF_KNX_SCENE_NUMBER,
    CONF_LED_COLOR_VALUE,
    CONF_MAPPING_ID,
    CONF_MAPPING_NAME,
    CONF_MAPPING_TYPE,
    CONF_SCENE_ENTITY_ID,
    CONF_SCENE_MAPPINGS,
    CONF_SCENE_SELECTION_ADDRESS,
    CONF_STATUS_LED_ADDRESS,
    CONF_TOGGLE_ADDRESS,
    CONF_TRIGGER_MODE,
    MAX_KNX_SCENE_NUMBER,
    MAX_LED_COLOR_VALUE,
    MAX_REGULAR_SCENE_MAPPINGS,
    MIN_KNX_SCENE_NUMBER,
    MIN_LED_COLOR_VALUE,
    MIN_REGULAR_SCENE_MAPPINGS,
)


class TriggerMode(StrEnum):
    """Supported KNX trigger strategies."""

    SEPARATE_TOGGLE = "separate_toggle"
    NEUTRAL_SCENE = "neutral_scene"


class SceneMappingType(StrEnum):
    """Supported scene mapping roles."""

    REGULAR = "regular"
    NEUTRAL = "neutral"


@dataclass(frozen=True, slots=True)
class SceneMapping:
    """Map a logical scene role to a Home Assistant scene."""

    mapping_id: str
    name: str
    mapping_type: SceneMappingType
    knx_scene_number: int | None
    scene_entity_id: str
    led_color_value: int | None = None

    def __post_init__(self) -> None:
        """Validate values independent of the button trigger mode."""
        if not self.mapping_id.strip():
            raise ValueError("Scene mapping ID must not be empty.")

        if not self.name.strip():
            raise ValueError("Scene mapping name must not be empty.")

        if not self.scene_entity_id.strip():
            raise ValueError(
                "Home Assistant scene entity ID must not be empty."
            )

        if self.knx_scene_number is not None and not (
            MIN_KNX_SCENE_NUMBER
            <= self.knx_scene_number
            <= MAX_KNX_SCENE_NUMBER
        ):
            raise ValueError(
                "KNX scene number must be between "
                f"{MIN_KNX_SCENE_NUMBER} and {MAX_KNX_SCENE_NUMBER}."
            )

        if self.led_color_value is not None and not (
            MIN_LED_COLOR_VALUE
            <= self.led_color_value
            <= MAX_LED_COLOR_VALUE
        ):
            raise ValueError(
                "LED color value must be between "
                f"{MIN_LED_COLOR_VALUE} and {MAX_LED_COLOR_VALUE}."
            )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> SceneMapping:
        """Create a scene mapping from config-entry data."""
        return cls(
            mapping_id=str(data[CONF_MAPPING_ID]).strip(),
            name=str(data[CONF_MAPPING_NAME]).strip(),
            mapping_type=SceneMappingType(
                str(data[CONF_MAPPING_TYPE])
            ),
            knx_scene_number=_optional_int(
                data.get(CONF_KNX_SCENE_NUMBER)
            ),
            scene_entity_id=str(data[CONF_SCENE_ENTITY_ID]).strip(),
            led_color_value=_optional_int(
                data.get(CONF_LED_COLOR_VALUE)
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the scene mapping to config-entry data."""
        return {
            CONF_MAPPING_ID: self.mapping_id,
            CONF_MAPPING_NAME: self.name,
            CONF_MAPPING_TYPE: self.mapping_type.value,
            CONF_KNX_SCENE_NUMBER: self.knx_scene_number,
            CONF_SCENE_ENTITY_ID: self.scene_entity_id,
            CONF_LED_COLOR_VALUE: self.led_color_value,
        }


@dataclass(frozen=True, slots=True)
class SceneButtonConfig:
    """Persistent configuration for one logical KNX scene button."""

    button_id: str
    name: str
    trigger_mode: TriggerMode

    scene_selection_address: str
    toggle_address: str | None
    status_led_address: str | None

    scene_mappings: tuple[SceneMapping, ...]

    _scene_number_index: Mapping[int, SceneMapping] = field(
        init=False,
        repr=False,
        compare=False,
    )
    _mapping_id_index: Mapping[str, SceneMapping] = field(
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        """Validate configuration and build immutable indexes."""
        self._validate()

        object.__setattr__(
            self,
            "_scene_number_index",
            MappingProxyType(
                {
                    mapping.knx_scene_number: mapping
                    for mapping in self.scene_mappings
                    if mapping.knx_scene_number is not None
                }
            ),
        )
        object.__setattr__(
            self,
            "_mapping_id_index",
            MappingProxyType(
                {
                    mapping.mapping_id: mapping
                    for mapping in self.scene_mappings
                }
            ),
        )

    def _validate(self) -> None:
        """Validate the complete button configuration."""
        if not self.button_id.strip():
            raise ValueError("Button ID must not be empty.")

        if not self.name.strip():
            raise ValueError("Button name must not be empty.")

        if not self.scene_selection_address.strip():
            raise ValueError(
                "Scene selection group address must not be empty."
            )

        if self.trigger_mode is TriggerMode.SEPARATE_TOGGLE:
            if self.toggle_address is None or not self.toggle_address.strip():
                raise ValueError(
                    "Separate-toggle mode requires a toggle group address."
                )

            if (
                self.toggle_address.strip()
                == self.scene_selection_address.strip()
            ):
                raise ValueError(
                    "Scene selection and toggle group addresses must differ."
                )

        elif self.toggle_address not in (None, ""):
            raise ValueError(
                "Neutral-scene mode must not define a toggle group address."
            )

        regular_mappings = self.regular_mappings
        regular_count = len(regular_mappings)

        if not (
            MIN_REGULAR_SCENE_MAPPINGS
            <= regular_count
            <= MAX_REGULAR_SCENE_MAPPINGS
        ):
            raise ValueError(
                "A button requires between "
                f"{MIN_REGULAR_SCENE_MAPPINGS} and "
                f"{MAX_REGULAR_SCENE_MAPPINGS} regular scene mappings."
            )

        neutral_mappings = tuple(
            mapping
            for mapping in self.scene_mappings
            if mapping.mapping_type is SceneMappingType.NEUTRAL
        )
        if len(neutral_mappings) != 1:
            raise ValueError(
                "A button must define exactly one neutral scene mapping."
            )

        if any(
            mapping.knx_scene_number is None
            for mapping in regular_mappings
        ):
            raise ValueError(
                "Every regular scene mapping requires a KNX scene number."
            )

        neutral_mapping = neutral_mappings[0]

        if self.trigger_mode is TriggerMode.SEPARATE_TOGGLE:
            if neutral_mapping.knx_scene_number is not None:
                raise ValueError(
                    "The neutral mapping must not have a KNX scene number "
                    "in separate-toggle mode."
                )
        elif neutral_mapping.knx_scene_number is None:
            raise ValueError(
                "The neutral mapping requires a KNX scene number "
                "in neutral-scene mode."
            )

        mapping_ids = [
            mapping.mapping_id for mapping in self.scene_mappings
        ]
        if len(mapping_ids) != len(set(mapping_ids)):
            raise ValueError("Scene mapping IDs must be unique.")

        scene_numbers = [
            mapping.knx_scene_number
            for mapping in self.scene_mappings
            if mapping.knx_scene_number is not None
        ]
        if len(scene_numbers) != len(set(scene_numbers)):
            raise ValueError(
                "KNX scene numbers must be unique within one button."
            )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> SceneButtonConfig:
        """Create a button configuration from config-entry data."""
        return cls(
            button_id=str(data[CONF_BUTTON_ID]).strip(),
            name=str(data[CONF_BUTTON_NAME]).strip(),
            trigger_mode=TriggerMode(str(data[CONF_TRIGGER_MODE])),
            scene_selection_address=str(
                data[CONF_SCENE_SELECTION_ADDRESS]
            ).strip(),
            toggle_address=_optional_string(
                data.get(CONF_TOGGLE_ADDRESS)
            ),
            status_led_address=_optional_string(
                data.get(CONF_STATUS_LED_ADDRESS)
            ),
            scene_mappings=tuple(
                SceneMapping.from_dict(mapping)
                for mapping in data[CONF_SCENE_MAPPINGS]
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the button configuration to config-entry data."""
        return {
            CONF_BUTTON_ID: self.button_id,
            CONF_BUTTON_NAME: self.name,
            CONF_TRIGGER_MODE: self.trigger_mode.value,
            CONF_SCENE_SELECTION_ADDRESS: self.scene_selection_address,
            CONF_TOGGLE_ADDRESS: self.toggle_address or "",
            CONF_STATUS_LED_ADDRESS: self.status_led_address or "",
            CONF_SCENE_MAPPINGS: [
                mapping.to_dict() for mapping in self.scene_mappings
            ],
        }

    @property
    def neutral_mapping(self) -> SceneMapping:
        """Return the configured neutral scene mapping."""
        return next(
            mapping
            for mapping in self.scene_mappings
            if mapping.mapping_type is SceneMappingType.NEUTRAL
        )

    @property
    def regular_mappings(self) -> tuple[SceneMapping, ...]:
        """Return all regular scene mappings."""
        return tuple(
            mapping
            for mapping in self.scene_mappings
            if mapping.mapping_type is SceneMappingType.REGULAR
        )

    @property
    def scene_mappings_by_knx_number(
        self,
    ) -> Mapping[int, SceneMapping]:
        """Return the immutable scene-number index."""
        return self._scene_number_index

    def mapping_for_knx_scene_number(
        self,
        knx_scene_number: int,
    ) -> SceneMapping | None:
        """Return the mapping for a KNX scene number."""
        return self._scene_number_index.get(knx_scene_number)

    def mapping_for_id(
        self,
        mapping_id: str,
    ) -> SceneMapping | None:
        """Return a mapping by its stable mapping ID."""
        return self._mapping_id_index.get(mapping_id)


def _optional_int(value: Any) -> int | None:
    """Return an optional integer from stored data."""
    if value in (None, ""):
        return None

    return int(value)


def _optional_string(value: Any) -> str | None:
    """Return a stripped optional string from stored data."""
    if value in (None, ""):
        return None

    stripped_value = str(value).strip()
    return stripped_value or None
