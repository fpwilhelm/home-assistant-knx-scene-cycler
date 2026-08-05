"""Button configuration factory for KNX Scene Cycler."""

from __future__ import annotations

from typing import Any

from .const import (
    CONF_BUTTON_ID,
    CONF_BUTTON_NAME,
    CONF_SCENE_SELECTION_ADDRESS,
    CONF_STATUS_LED_ADDRESS,
    CONF_TOGGLE_ADDRESS,
    CONF_TRIGGER_MODE,
    DEFAULT_NEUTRAL_KNX_SCENE_NUMBER,
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
    _neutral_mapping_name_key,
    _neutral_scene_entity_key,
    _scene_entity_key,
)
from .validation import _optional_string, _trigger_mode


def _create_button_config(
    user_input: dict[str, Any],
    *,
    existing_config: SceneButtonConfig | None = None,
) -> SceneButtonConfig:
    """Create one immutable button configuration."""
    trigger_mode = _trigger_mode(user_input)
    existing_regular_mappings = (
        existing_config.regular_mappings
        if existing_config is not None
        else ()
    )
    used_mapping_ids = {
        mapping.mapping_id for mapping in existing_regular_mappings
    }

    mappings: list[SceneMapping] = []

    for mapping_number in range(
        1,
        _REGULAR_MAPPING_COUNT + 1,
    ):
        scene_entity_id = _optional_string(
            user_input.get(_scene_entity_key(mapping_number))
        )
        if scene_entity_id is None:
            continue

        mapping_name = str(
            user_input.get(_mapping_name_key(mapping_number), "")
        ).strip()
        raw_scene_number = user_input.get(
            _knx_scene_number_key(mapping_number)
        )
        if not mapping_name or raw_scene_number in (None, ""):
            raise ValueError(
                "Every enabled regular scene requires a name and "
                "a KNX scene number."
            )

        existing_mapping = (
            existing_regular_mappings[mapping_number - 1]
            if mapping_number <= len(existing_regular_mappings)
            else None
        )
        mapping_id = (
            existing_mapping.mapping_id
            if existing_mapping is not None
            else _new_regular_mapping_id(
                preferred_number=mapping_number,
                used_mapping_ids=used_mapping_ids,
            )
        )
        used_mapping_ids.add(mapping_id)
        mappings.append(
            SceneMapping(
                mapping_id=mapping_id,
                name=mapping_name,
                mapping_type=SceneMappingType.REGULAR,
                knx_scene_number=int(raw_scene_number),
                scene_entity_id=scene_entity_id,
                led_color_value=(
                    existing_mapping.led_color_value
                    if existing_mapping is not None
                    else None
                ),
            )
        )

    neutral_knx_scene_number: int | None = None
    if trigger_mode is TriggerMode.NEUTRAL_SCENE:
        neutral_knx_scene_number = DEFAULT_NEUTRAL_KNX_SCENE_NUMBER

    mappings.append(
        SceneMapping(
            mapping_id=(
                existing_config.neutral_mapping.mapping_id
                if existing_config is not None
                else "neutral"
            ),
            name=str(
                user_input[_neutral_mapping_name_key()]
            ).strip(),
            mapping_type=SceneMappingType.NEUTRAL,
            knx_scene_number=neutral_knx_scene_number,
            scene_entity_id=str(
                user_input[_neutral_scene_entity_key()]
            ).strip(),
            led_color_value=(
                existing_config.neutral_mapping.led_color_value
                if existing_config is not None
                else None
            ),
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


def _button_config_to_form_data(
    button_config: SceneButtonConfig,
) -> dict[str, Any]:
    """Convert one stored button configuration to editable form data."""
    form_data: dict[str, Any] = {
        CONF_BUTTON_ID: button_config.button_id,
        CONF_BUTTON_NAME: button_config.name,
        CONF_TRIGGER_MODE: button_config.trigger_mode.value,
        CONF_SCENE_SELECTION_ADDRESS: (
            button_config.scene_selection_address
        ),
        CONF_TOGGLE_ADDRESS: button_config.toggle_address or "",
        CONF_STATUS_LED_ADDRESS: (
            button_config.status_led_address or ""
        ),
    }

    for mapping_number, mapping in enumerate(
        button_config.regular_mappings,
        start=1,
    ):
        form_data[_mapping_name_key(mapping_number)] = mapping.name
        form_data[_scene_entity_key(mapping_number)] = (
            mapping.scene_entity_id
        )
        form_data[_knx_scene_number_key(mapping_number)] = (
            mapping.knx_scene_number
        )

    neutral_mapping = button_config.neutral_mapping
    form_data[_neutral_mapping_name_key()] = neutral_mapping.name
    form_data[_neutral_scene_entity_key()] = (
        neutral_mapping.scene_entity_id
    )

    return form_data


def _replace_regular_scene_form_data(
    base_data: dict[str, Any],
    user_input: dict[str, Any],
) -> dict[str, Any]:
    """Replace all regular-scene form values in accumulated flow data.

    Home Assistant omits cleared optional selector fields from user input.
    Removing every value owned by this form step first prevents a cleared
    scene entity from being restored from the previous form defaults.
    """
    updated_data = dict(base_data)

    for mapping_number in range(
        1,
        _REGULAR_MAPPING_COUNT + 1,
    ):
        updated_data.pop(_mapping_name_key(mapping_number), None)
        updated_data.pop(_scene_entity_key(mapping_number), None)
        updated_data.pop(_knx_scene_number_key(mapping_number), None)

    updated_data.update(user_input)
    return updated_data


def _new_regular_mapping_id(
    *,
    preferred_number: int,
    used_mapping_ids: set[str],
) -> str:
    """Return an unused stable ID for a new regular mapping."""
    candidate_number = preferred_number

    while f"regular_{candidate_number}" in used_mapping_ids:
        candidate_number += 1

    return f"regular_{candidate_number}"
