"""Button configuration factory for KNX Scene Cycler."""

from __future__ import annotations

from typing import Any

from .const import (
    CONF_BUTTON_ID,
    CONF_BUTTON_NAME,
    CONF_SCENE_SELECTION_ADDRESS,
    CONF_STATUS_LED_ADDRESS,
    CONF_TOGGLE_ADDRESS,
)
from .models import (
    SceneButtonConfig,
    SceneMapping,
    SceneMappingType,
    TriggerMode,
)
from .schemas import (
    _REGULAR_MAPPING_COUNT,
    _knx_scene_number_key,
    _mapping_name_key,
    _neutral_knx_scene_number_key,
    _neutral_mapping_name_key,
    _neutral_scene_entity_key,
    _scene_entity_key,
)
from .validation import _optional_string, _trigger_mode


def _create_button_config(
    user_input: dict[str, Any],
) -> SceneButtonConfig:
    """Create one immutable button configuration."""
    trigger_mode = _trigger_mode(user_input)

    mappings = [
        SceneMapping(
            mapping_id=f"regular_{mapping_number}",
            name=str(
                user_input[
                    _mapping_name_key(mapping_number)
                ]
            ).strip(),
            mapping_type=SceneMappingType.REGULAR,
            knx_scene_number=int(
                user_input[
                    _knx_scene_number_key(mapping_number)
                ]
            ),
            scene_entity_id=str(
                user_input[
                    _scene_entity_key(mapping_number)
                ]
            ).strip(),
            led_color_value=None,
        )
        for mapping_number in range(
            1,
            _REGULAR_MAPPING_COUNT + 1,
        )
    ]

    neutral_knx_scene_number: int | None = None
    if trigger_mode is TriggerMode.NEUTRAL_SCENE:
        neutral_knx_scene_number = int(
            user_input[_neutral_knx_scene_number_key()]
        )

    mappings.append(
        SceneMapping(
            mapping_id="neutral",
            name=str(
                user_input[_neutral_mapping_name_key()]
            ).strip(),
            mapping_type=SceneMappingType.NEUTRAL,
            knx_scene_number=neutral_knx_scene_number,
            scene_entity_id=str(
                user_input[_neutral_scene_entity_key()]
            ).strip(),
            led_color_value=None,
        )
    )

    toggle_address: str | None = None
    if trigger_mode is TriggerMode.SEPARATE_TOGGLE:
        toggle_address = str(
            user_input[CONF_TOGGLE_ADDRESS]
        ).strip()

    status_led_address = _optional_string(
        user_input.get(CONF_STATUS_LED_ADDRESS)
    )

    return SceneButtonConfig(
        button_id=str(user_input[CONF_BUTTON_ID]).strip(),
        name=str(user_input[CONF_BUTTON_NAME]).strip(),
        trigger_mode=trigger_mode,
        scene_selection_address=str(
            user_input[CONF_SCENE_SELECTION_ADDRESS]
        ).strip(),
        toggle_address=toggle_address,
        status_led_address=status_led_address,
        scene_mappings=tuple(mappings),
    )
