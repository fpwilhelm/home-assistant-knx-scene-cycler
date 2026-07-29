"""Runtime state for the KNX Scene Cycler integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum

from .const import DEFAULT_SCENE_SLOT, SCENE_SLOTS
from .models import SceneButtonConfig

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
    current_scene_slot: int | None = None
    last_active_scene_slot: int = DEFAULT_SCENE_SLOT
    _listeners: set[RuntimeListener] = field(
        default_factory=set,
        init=False,
        repr=False,
    )

    @property
    def is_active(self) -> bool:
        """Return whether a regular scene is currently active."""
        return self.state is ButtonState.ACTIVE

    @property
    def is_available(self) -> bool:
        """Return whether the button runtime is available."""
        return self.state is not ButtonState.UNAVAILABLE

    def add_listener(
        self,
        listener: RuntimeListener,
    ) -> Callable[[], None]:
        """Register a runtime state listener."""
        self._listeners.add(listener)

        def remove_listener() -> None:
            self._listeners.discard(listener)

        return remove_listener

    def activate_scene(self, slot: int) -> None:
        """Mark one regular scene slot as active."""
        self._validate_scene_slot(slot)

        self.current_scene_slot = slot
        self.last_active_scene_slot = slot
        self.state = ButtonState.ACTIVE

        self._notify_listeners()

    def deactivate(self) -> None:
        """Mark the neutral scene as active."""
        self.current_scene_slot = None
        self.state = ButtonState.INACTIVE

        self._notify_listeners()

    def mark_unavailable(self) -> None:
        """Mark the runtime as unavailable without forgetting scene history."""
        self.current_scene_slot = None
        self.state = ButtonState.UNAVAILABLE

        self._notify_listeners()

    def reset(self) -> None:
        """Reset runtime state to its initial values."""
        self.current_scene_slot = None
        self.last_active_scene_slot = DEFAULT_SCENE_SLOT
        self.state = ButtonState.INACTIVE

        self._notify_listeners()

    def _notify_listeners(self) -> None:
        """Notify all registered listeners about a state change."""
        for listener in tuple(self._listeners):
            listener()

    @staticmethod
    def _validate_scene_slot(slot: int) -> None:
        """Raise an error if a scene slot is unsupported."""
        if slot not in SCENE_SLOTS:
            raise ValueError(
                f"Unsupported scene slot {slot}. "
                f"Expected one of {SCENE_SLOTS}."
            )