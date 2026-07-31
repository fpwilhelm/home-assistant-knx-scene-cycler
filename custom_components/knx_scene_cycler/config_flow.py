"""Config flow for the KNX Scene Cycler integration."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONFIG_ENTRY_MINOR_VERSION,
    CONFIG_ENTRY_VERSION,
    CONF_BUTTON_ID,
    CONF_BUTTON_NAME,
    CONF_BUTTONS,
    CONF_HUB_NAME,
    CONF_KNX_SCENE_NUMBER,
    CONF_MAPPING_ID,
    CONF_MAPPING_NAME,
    CONF_MAPPING_TYPE,
    CONF_SCENE_ENTITY_ID,
    CONF_SCENE_MAPPINGS,
    CONF_SCENE_SELECTION_ADDRESS,
    CONF_STATUS_LED_ADDRESS,
    CONF_TOGGLE_ADDRESS,
    CONF_TRIGGER_MODE,
    DEFAULT_NEUTRAL_KNX_SCENE_NUMBER,
    DOMAIN,
    MAX_KNX_SCENE_NUMBER,
    MIN_KNX_SCENE_NUMBER,
    MIN_REGULAR_SCENE_MAPPINGS,
)
from .models import (
    SceneButtonConfig,
    SceneMapping,
    SceneMappingType,
    TriggerMode,
)

ACTION_ADD_BUTTON = "add_button"
ACTION_FINISH = "finish"

DEFAULT_HUB_NAME = "KNX Scene Cycler"
DEFAULT_BUTTON_NAME = "Scene Button"

CONF_ACTION = "action"

_REGULAR_MAPPING_COUNT = MIN_REGULAR_SCENE_MAPPINGS


class KnxSceneCyclerConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle a config flow for KNX Scene Cycler."""

    VERSION = CONFIG_ENTRY_VERSION
    MINOR_VERSION = CONFIG_ENTRY_MINOR_VERSION

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._hub_name = DEFAULT_HUB_NAME
        self._button_data: dict[str, Any] = {}

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure the KNX Scene Cycler hub."""
        if user_input is not None:
            self._hub_name = str(
                user_input[CONF_HUB_NAME]
            ).strip()
            self._button_data = {
                CONF_BUTTON_ID: "button_1",
                CONF_BUTTON_NAME: DEFAULT_BUTTON_NAME,
            }
            return await self.async_step_button_trigger()

        return self.async_show_form(
            step_id="user",
            data_schema=_hub_schema(),
        )

    async def async_step_button_trigger(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Choose the trigger strategy for the first button."""
        if user_input is not None:
            self._button_data.update(user_input)
            return await self.async_step_button_addresses()

        return self.async_show_form(
            step_id="button_trigger",
            data_schema=_button_trigger_schema(
                default_button_name=DEFAULT_BUTTON_NAME,
            ),
        )

    async def async_step_button_addresses(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure KNX group addresses for the first button."""
        if user_input is not None:
            self._button_data.update(user_input)
            return await self.async_step_button_scenes()

        return self.async_show_form(
            step_id="button_addresses",
            data_schema=_button_addresses_schema(
                trigger_mode=_trigger_mode(self._button_data),
            ),
        )

    async def async_step_button_scenes(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure regular scenes for the first button."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if _has_duplicate_regular_scene_numbers(user_input):
                errors["base"] = "duplicate_knx_scene_numbers"
            else:
                self._button_data.update(user_input)
                return await self.async_step_button_neutral()

        return self.async_show_form(
            step_id="button_scenes",
            data_schema=_regular_scenes_schema(),
            errors=errors,
        )

    async def async_step_button_neutral(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure the neutral scene and create the entry."""
        errors: dict[str, str] = {}

        if user_input is not None:
            candidate_data = {
                **self._button_data,
                **user_input,
            }

            try:
                button_config = _create_button_config(candidate_data)
            except ValueError as err:
                errors["base"] = _model_error_key(err)
            else:
                return self.async_create_entry(
                    title=self._hub_name,
                    data={
                        CONF_HUB_NAME: self._hub_name,
                        CONF_BUTTONS: [
                            button_config.to_dict(),
                        ],
                    },
                )

        return self.async_show_form(
            step_id="button_neutral",
            data_schema=_neutral_scene_schema(
                trigger_mode=_trigger_mode(self._button_data),
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow handler."""
        return KnxSceneCyclerOptionsFlowHandler()


class KnxSceneCyclerOptionsFlowHandler(
    config_entries.OptionsFlow
):
    """Handle changes to an existing KNX Scene Cycler entry."""

    def __init__(self) -> None:
        """Initialize the options flow."""
        self._button_data: dict[str, Any] = {}

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Choose an options-flow action."""
        if user_input is not None:
            action = user_input[CONF_ACTION]

            if action == ACTION_ADD_BUTTON:
                next_button_number = (
                    len(
                        self.config_entry.data.get(
                            CONF_BUTTONS,
                            [],
                        )
                    )
                    + 1
                )
                self._button_data = {
                    CONF_BUTTON_ID: (
                        f"button_{next_button_number}"
                    ),
                    CONF_BUTTON_NAME: (
                        f"{DEFAULT_BUTTON_NAME} "
                        f"{next_button_number}"
                    ),
                }
                return await self.async_step_add_button_trigger()

            return self.async_create_entry(
                title="",
                data={},
            )

        return self.async_show_form(
            step_id="init",
            data_schema=_options_action_schema(),
        )

    async def async_step_add_button_trigger(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Choose the trigger strategy for another button."""
        if user_input is not None:
            self._button_data.update(user_input)
            return await self.async_step_add_button_addresses()

        return self.async_show_form(
            step_id="add_button_trigger",
            data_schema=_button_trigger_schema(
                default_button_name=str(
                    self._button_data[CONF_BUTTON_NAME]
                ),
            ),
        )

    async def async_step_add_button_addresses(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure group addresses for another button."""
        if user_input is not None:
            self._button_data.update(user_input)
            return await self.async_step_add_button_scenes()

        return self.async_show_form(
            step_id="add_button_addresses",
            data_schema=_button_addresses_schema(
                trigger_mode=_trigger_mode(self._button_data),
            ),
        )

    async def async_step_add_button_scenes(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure regular scenes for another button."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if _has_duplicate_regular_scene_numbers(user_input):
                errors["base"] = "duplicate_knx_scene_numbers"
            else:
                self._button_data.update(user_input)
                return await self.async_step_add_button_neutral()

        return self.async_show_form(
            step_id="add_button_scenes",
            data_schema=_regular_scenes_schema(),
            errors=errors,
        )

    async def async_step_add_button_neutral(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Configure the neutral scene and save another button."""
        errors: dict[str, str] = {}

        if user_input is not None:
            candidate_data = {
                **self._button_data,
                **user_input,
            }

            try:
                button_config = _create_button_config(candidate_data)
            except ValueError as err:
                errors["base"] = _model_error_key(err)
            else:
                current_buttons = list(
                    self.config_entry.data.get(CONF_BUTTONS, [])
                )
                updated_data = dict(self.config_entry.data)
                updated_data[CONF_BUTTONS] = [
                    *current_buttons,
                    button_config.to_dict(),
                ]

                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data=updated_data,
                )

                return self.async_create_entry(
                    title="",
                    data={},
                )

        return self.async_show_form(
            step_id="add_button_neutral",
            data_schema=_neutral_scene_schema(
                trigger_mode=_trigger_mode(self._button_data),
            ),
            errors=errors,
        )


def _hub_schema() -> vol.Schema:
    """Return the hub configuration schema."""
    return vol.Schema(
        {
            vol.Required(
                CONF_HUB_NAME,
                default=DEFAULT_HUB_NAME,
            ): str,
        }
    )


def _options_action_schema() -> vol.Schema:
    """Return the options-flow action schema."""
    return vol.Schema(
        {
            vol.Required(
                CONF_ACTION,
                default=ACTION_ADD_BUTTON,
            ): vol.In(
                {
                    ACTION_ADD_BUTTON: "Add scene button",
                    ACTION_FINISH: "Finish",
                }
            ),
        }
    )


def _button_trigger_schema(
    *,
    default_button_name: str,
) -> vol.Schema:
    """Return the schema for button name and trigger mode."""
    return vol.Schema(
        {
            vol.Required(
                CONF_BUTTON_NAME,
                default=default_button_name,
            ): str,
            vol.Required(
                CONF_TRIGGER_MODE,
                default=TriggerMode.SEPARATE_TOGGLE.value,
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(
                            value=TriggerMode.SEPARATE_TOGGLE.value,
                            label="Separate Toggle GA",
                        ),
                        selector.SelectOptionDict(
                            value=TriggerMode.NEUTRAL_SCENE.value,
                            label="Neutral Scene on Scene GA",
                        ),
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        }
    )


def _button_addresses_schema(
    *,
    trigger_mode: TriggerMode,
) -> vol.Schema:
    """Return the group-address schema for one trigger mode."""
    schema: dict[vol.Marker, Any] = {
        vol.Required(CONF_SCENE_SELECTION_ADDRESS): str,
    }

    if trigger_mode is TriggerMode.SEPARATE_TOGGLE:
        schema[vol.Required(CONF_TOGGLE_ADDRESS)] = str

    schema[vol.Optional(CONF_STATUS_LED_ADDRESS)] = str

    return vol.Schema(schema)


def _regular_scenes_schema() -> vol.Schema:
    """Return the schema for four regular scene mappings."""
    schema: dict[vol.Marker, Any] = {}
    scene_selector = _scene_selector()
    scene_number_schema = _scene_number_schema()

    for mapping_number in range(
        1,
        _REGULAR_MAPPING_COUNT + 1,
    ):
        schema[
            vol.Required(
                _mapping_name_key(mapping_number),
                default=f"Scene {mapping_number}",
            )
        ] = str
        schema[
            vol.Required(
                _scene_entity_key(mapping_number)
            )
        ] = scene_selector
        schema[
            vol.Required(
                _knx_scene_number_key(mapping_number),
                default=mapping_number,
            )
        ] = scene_number_schema

    return vol.Schema(schema)


def _neutral_scene_schema(
    *,
    trigger_mode: TriggerMode,
) -> vol.Schema:
    """Return the neutral scene schema for one trigger mode."""
    schema: dict[vol.Marker, Any] = {
        vol.Required(
            _neutral_mapping_name_key(),
            default="Neutral",
        ): str,
        vol.Required(
            _neutral_scene_entity_key()
        ): _scene_selector(),
    }

    if trigger_mode is TriggerMode.NEUTRAL_SCENE:
        schema[
            vol.Required(
                _neutral_knx_scene_number_key(),
                default=DEFAULT_NEUTRAL_KNX_SCENE_NUMBER,
            )
        ] = _scene_number_schema()

    return vol.Schema(schema)


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


def _scene_selector() -> selector.EntitySelector:
    """Return a Home Assistant scene selector."""
    return selector.EntitySelector(
        selector.EntitySelectorConfig(
            domain="scene",
        )
    )


def _scene_number_schema() -> vol.All:
    """Return the KNX scene number validator."""
    return vol.All(
        vol.Coerce(int),
        vol.Range(
            min=MIN_KNX_SCENE_NUMBER,
            max=MAX_KNX_SCENE_NUMBER,
        ),
    )


def _optional_string(value: Any) -> str | None:
    """Return a stripped optional string."""
    if value in (None, ""):
        return None

    stripped_value = str(value).strip()
    return stripped_value or None


def _mapping_name_key(mapping_number: int) -> str:
    """Return the temporary form key for a mapping name."""
    return f"{CONF_MAPPING_NAME}_{mapping_number}"


def _scene_entity_key(mapping_number: int) -> str:
    """Return the temporary form key for a scene entity."""
    return f"{CONF_SCENE_ENTITY_ID}_{mapping_number}"


def _knx_scene_number_key(mapping_number: int) -> str:
    """Return the temporary form key for a KNX scene number."""
    return f"{CONF_KNX_SCENE_NUMBER}_{mapping_number}"


def _neutral_mapping_name_key() -> str:
    """Return the temporary form key for the neutral mapping name."""
    return f"{CONF_MAPPING_NAME}_neutral"


def _neutral_scene_entity_key() -> str:
    """Return the temporary form key for the neutral scene entity."""
    return f"{CONF_SCENE_ENTITY_ID}_neutral"


def _neutral_knx_scene_number_key() -> str:
    """Return the temporary form key for the neutral KNX scene number."""
    return f"{CONF_KNX_SCENE_NUMBER}_neutral"
