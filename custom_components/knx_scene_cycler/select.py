"""Select platform for the KNX Scene Cycler integration."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .controller import SceneButtonController
from .hub import KNXSceneCyclerHub
from .models import SceneMapping

DATA_HUB = "hub"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KNX Scene Cycler select entities."""
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    hub = entry_data.get(DATA_HUB)

    if not isinstance(hub, KNXSceneCyclerHub):
        raise RuntimeError(
            f"KNX Scene Cycler hub unavailable for {config_entry.entry_id}."
        )

    async_add_entities(
        KnxSceneCyclerSelect(config_entry, controller)
        for controller in hub.controllers
    )


class KnxSceneCyclerSelect(SelectEntity):
    """Select entity for the regular scenes of one KNX button."""

    _attr_has_entity_name = True

    def __init__(
        self,
        config_entry: ConfigEntry,
        controller: SceneButtonController,
    ) -> None:
        self._controller = controller
        self._config = controller.config
        self._runtime = controller.runtime

        self._mapping_by_option = self._build_option_index(
            self._config.regular_mappings
        )
        self._option_by_scene_number = {
            mapping.knx_scene_number: option
            for option, mapping in self._mapping_by_option.items()
            if mapping.knx_scene_number is not None
        }

        self._attr_name = f"{self._config.name} Scene"
        self._attr_unique_id = (
            f"{config_entry.entry_id}_{self._config.button_id}_select"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)}
        )
        self._attr_options = list(self._mapping_by_option)

    @property
    def current_option(self) -> str | None:
        return self._option_by_scene_number.get(
            self._runtime.last_regular_scene_number
        )

    @property
    def available(self) -> bool:
        return self._runtime.is_available

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            self._runtime.add_listener(
                self._async_handle_runtime_update
            )
        )

    async def async_select_option(self, option: str) -> None:
        mapping = self._mapping_by_option.get(option)
        if mapping is None or mapping.knx_scene_number is None:
            raise ValueError(f"Unsupported scene option: {option!r}.")

        await self._controller.activate_scene_number(
            mapping.knx_scene_number
        )

        await self.hass.services.async_call(
            "knx",
            "send",
            {
                "address": self._config.scene_selection_address,
                "payload": mapping.knx_scene_number,
            },
            blocking=True,
        )

    @callback
    def _async_handle_runtime_update(self) -> None:
        self.async_write_ha_state()

    @staticmethod
    def _build_option_index(
        mappings: tuple[SceneMapping, ...],
    ) -> dict[str, SceneMapping]:
        options: dict[str, SceneMapping] = {}

        for mapping in mappings:
            if mapping.knx_scene_number is None:
                raise ValueError(
                    "Regular scene mappings require a KNX scene number."
                )

            option = mapping.name
            if option in options:
                option = (
                    f"{mapping.name} "
                    f"(KNX {mapping.knx_scene_number})"
                )
            if option in options:
                raise ValueError(
                    "Scene names and KNX scene numbers must produce "
                    "unique select options."
                )
            options[option] = mapping

        return options
