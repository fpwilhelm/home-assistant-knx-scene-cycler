"""Runtime state for the KNX Scene Cycler integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum

from .const import DEFAULT_SCENE_SLOT, SCENE_SLOTS
from .models import SceneButtonConfig, SceneMapping

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
        """Initialize scene history from the configured regular mappings."""
        self.last_regular_scene_number = (
            self._default_regular_mapping().knx_scene_number
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
    def current_scene_slot(self) -> int | None:
        """Return the legacy slot for the current scene during migration."""
        if self.current_scene_number is None:
            return None

        mapping = self.config.mapping_for_scene_number(
            self.current_scene_number
        )
        return mapping.slot if mapping is not None else None

    @property
    def last_active_scene_slot(self) -> int:
        """Return the legacy slot for the last regular scene."""
        mapping = self.config.mapping_for_scene_number(
            self.last_regular_scene_number
        )
        if mapping is None or mapping.slot is None:
            return DEFAULT_SCENE_SLOT

        return mapping.slot

    def add_listener(
        self,
        listener: RuntimeListener,
    ) -> Callable[[], None]:
        """Register a runtime state listener."""
        self._listeners.add(listener)

        def remove_listener() -> None:
            self._listeners.discard(listener)

        return remove_listener

    def activate_scene_number(self, scene_number: int) -> None:
        """Mark one configured regular KNX scene number as active."""
        mapping = self._regular_mapping_for_scene_number(scene_number)

        self.current_scene_number = mapping.knx_scene_number
        self.last_regular_scene_number = mapping.knx_scene_number
        self.state = ButtonState.ACTIVE

        self._notify_listeners()

    def activate_scene(self, slot: int) -> None:
        """Activate a regular scene by legacy slot during migration."""
        self._validate_scene_slot(slot)

        mapping = self.config.mapping_for_slot(slot)
        if mapping is None:
            raise ValueError(f"No scene mapping configured for slot {slot}.")

        self.activate_scene_number(mapping.knx_scene_number)

    def deactivate(self, scene_number: int | None = None) -> None:
        """Mark the configured neutral scene as active."""
        neutral_mapping = self.config.neutral_mapping()

        if scene_number is not None:
            if (
                neutral_mapping is None
                or neutral_mapping.knx_scene_number != scene_number
            ):
                raise ValueError(
                    f"Scene number {scene_number} is not the neutral scene."
                )

        self.current_scene_number = (
            neutral_mapping.knx_scene_number
            if neutral_mapping is not None
            else None
        )
        self.state = ButtonState.INACTIVE

        self._notify_listeners()

    def mark_unavailable(self) -> None:
        """Mark the runtime as unavailable without forgetting scene history."""
        self.current_scene_number = None
        self.state = ButtonState.UNAVAILABLE

        self._notify_listeners()

    def reset(self) -> None:
        """Reset runtime state to its initial values."""
        self.current_scene_number = None
        self.last_regular_scene_number = (
            self._default_regular_mapping().knx_scene_number
        )
        self.state = ButtonState.INACTIVE

        self._notify_listeners()

    def _default_regular_mapping(self) -> SceneMapping:
        """Return the preferred initial regular scene mapping."""
        legacy_default = self.config.mapping_for_slot(DEFAULT_SCENE_SLOT)
        if legacy_default is not None and not legacy_default.is_neutral:
            return legacy_default

        regular_mappings = self.config.regular_mappings()
        if not regular_mappings:
            raise ValueError(
                f"Button {self.config.button_id} has no regular scene mappings."
            )

        return regular_mappings[0]

    def _regular_mapping_for_scene_number(
        self,
        scene_number: int,
    ) -> SceneMapping:
        """Return a regular mapping or raise a descriptive error."""
        mapping = self.config.mapping_for_scene_number(scene_number)
        if mapping is None:
            raise ValueError(
                f"No scene mapping configured for scene number "
                f"{scene_number}."
            )
        if mapping.is_neutral:
            raise ValueError(
                f"Scene number {scene_number} is configured as neutral."
            )

        return mapping

    def _notify_listeners(self) -> None:
        """Notify all registered listeners about a state change."""
        for listener in tuple(self._listeners):
            listener()

    @staticmethod
    def _validate_scene_slot(slot: int) -> None:
        """Raise an error if a legacy scene slot is unsupported."""
        if slot not in SCENE_SLOTS:
            raise ValueError(
                f"Unsupported scene slot {slot}. "
                f"Expected one of {SCENE_SLOTS}."
            )