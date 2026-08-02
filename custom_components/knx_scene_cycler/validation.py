"""Validation helpers for KNX Scene Cycler configuration flows."""

from __future__ import annotations

from typing import Any

from .const import CONF_TRIGGER_MODE
from .models import TriggerMode
from .schemas import (
    _REGULAR_MAPPING_COUNT,
    _knx_scene_number_key,
)


def _trigger_mode(data: dict[str, Any]) -> TriggerMode:
    """Return the selected trigger mode."""
    return TriggerMode(str(data[CONF_TRIGGER_MODE]))


def _has_duplicate_regular_scene_numbers(
    user_input: dict[str, Any],
) -> bool:
    """Return whether regular scene numbers are duplicated."""
    scene_numbers = [
        int(user_input[_knx_scene_number_key(number)])
        for number in range(
            1,
            _REGULAR_MAPPING_COUNT + 1,
        )
    ]
    return len(scene_numbers) != len(set(scene_numbers))


def _model_error_key(error: ValueError) -> str:
    """Map model validation failures to config-flow errors."""
    message = str(error)

    if "KNX scene numbers must be unique" in message:
        return "duplicate_knx_scene_numbers"

    if "group addresses must differ" in message:
        return "duplicate_group_addresses"

    return "invalid_configuration"


def _optional_string(value: Any) -> str | None:
    """Return a stripped optional string."""
    if value in (None, ""):
        return None

    stripped_value = str(value).strip()
    return stripped_value or None
