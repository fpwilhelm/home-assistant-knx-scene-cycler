"""Runtime state for the KNX Scene Cycler integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum

from .models import (
    SceneButtonConfig,
    SceneMapping,
    SceneMappingType,
)

RuntimeListener = Callable[[], None]


class ButtonState(StrEnum):
    """Runtime state of one logical KNX scene button."""

    INACTIVE = "inactive"
    ACTIVE = "active"
    UNAVAILABLE = "unavailable"


@dataclass(slots=True)
class SceneButtonRuntime:
    """Mutable runtime state for one logical KNX scene button."""

    config: SceneButtonConfig
    state: ButtonState = ButtonState.INACTIVE
    current_scene_number: int | None = None
    last_regular_scene_number: int = field(init=False)
    _listeners: set[RuntimeListener] = field(
        default_factory=set,
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        """Initialize scene history from the first regular mapping."""
        self.last_regular_scene_number = (
            self._scene_number(self._default_regular_mapping())
        )

    @property
    def is_active(self) -> bool:
        """Return whether a regular scene is currently active."""
        return self.state is ButtonState.ACTIVE

    @property
    def is_available(self) -> bool:
        """Return whether the button runtime is available."""
        return self.state is not ButtonState.UNAVAILABLE

    @property
    def current_mapping(self) -> SceneMapping | None:
        """Return the mapping for the current KNX scene number."""
        if self.current_scene_number is None:
            return None

        return self.config.mapping_for_knx_scene_number(
            self.current_scene_number
        )

    @property
    def last_regular_mapping(self) -> SceneMapping:
        """Return the last activated regular scene mapping."""
        mapping = self.config.mapping_for_knx_scene_number(
            self.last_regular_scene_number
        )

        if (
            mapping is None
            or mapping.mapping_type is not SceneMappingType.REGULAR
        ):
            raise RuntimeError(
                "The stored last regular scene number no longer refers "
                "to a regular scene mapping."
            )

        return mapping

    def add_listener(
        self,
        listener: RuntimeListener,
    ) -> Callable[[], None]:
        """Register a runtime-state listener."""
        self._listeners.add(listener)

        def remove_listener() -> None:
            self._listeners.discard(listener)

        return remove_listener

    def activate_scene_number(self, scene_number: int) -> None:
        """Mark one configured regular KNX scene number as active."""
        mapping = self._regular_mapping_for_knx_scene_number(
            scene_number
        )
        mapped_scene_number = self._scene_number(mapping)

        self.current_scene_number = mapped_scene_number
        self.last_regular_scene_number = mapped_scene_number
        self.state = ButtonState.ACTIVE

        self._notify_listeners()

    def deactivate(self, scene_number: int | None = None) -> None:
        """Mark the configured neutral scene as active."""
        neutral_mapping = self.config.neutral_mapping

        if (
            scene_number is not None
            and neutral_mapping.knx_scene_number != scene_number
        ):
            raise ValueError(
                f"Scene number {scene_number} is not the neutral scene."
            )

        self.current_scene_number = neutral_mapping.knx_scene_number
        self.state = ButtonState.INACTIVE

        self._notify_listeners()

    def mark_unavailable(self) -> None:
        """Mark the runtime unavailable without forgetting scene history."""
        self.current_scene_number = None
        self.state = ButtonState.UNAVAILABLE

        self._notify_listeners()

    def reset(self) -> None:
        """Reset runtime state to its initial values."""
        self.current_scene_number = None
        self.last_regular_scene_number = (
            self._scene_number(self._default_regular_mapping())
        )
        self.state = ButtonState.INACTIVE

        self._notify_listeners()

    def _default_regular_mapping(self) -> SceneMapping:
        """Return the preferred initial regular scene mapping."""
        regular_mappings = self.config.regular_mappings

        if not regular_mappings:
            raise ValueError(
                f"Button {self.config.button_id} has no regular "
                "scene mappings."
            )

        return regular_mappings[0]

    def _regular_mapping_for_knx_scene_number(
        self,
        scene_number: int,
    ) -> SceneMapping:
        """Return a regular mapping or raise a descriptive error."""
        mapping = self.config.mapping_for_knx_scene_number(
            scene_number
        )

        if mapping is None:
            raise ValueError(
                "No scene mapping configured for KNX scene number "
                f"{scene_number}."
            )

        if mapping.mapping_type is SceneMappingType.NEUTRAL:
            raise ValueError(
                f"KNX scene number {scene_number} is configured "
                "as neutral."
            )

        return mapping

    def _notify_listeners(self) -> None:
        """Notify all registered listeners about a state change."""
        for listener in tuple(self._listeners):
            listener()

    @staticmethod
    def _scene_number(mapping: SceneMapping) -> int:
        """Return the required KNX scene number of a regular mapping."""
        if mapping.knx_scene_number is None:
            raise RuntimeError(
                f"Regular scene mapping {mapping.mapping_id!r} has "
                "no KNX scene number."
            )

        return mapping.knx_scene_number
