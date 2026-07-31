"""The KNX Scene Cycler integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import CONF_BUTTONS, CONF_HUB_NAME, DOMAIN
from .hub import KNXSceneCyclerHub
from .models import SceneButtonConfig

_LOGGER = logging.getLogger(__name__)

PLATFORMS: tuple[Platform, ...] = (
    Platform.SWITCH,
    Platform.SELECT,
)

DATA_HUB = "hub"

DEFAULT_HUB_NAME = "KNX Scene Cycler"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up KNX Scene Cycler from a config entry."""
    _LOGGER.debug(
        "Setting up KNX Scene Cycler config entry %s",
        entry.entry_id,
    )

    hub_name = _get_hub_name(entry)
    button_configs = _get_button_configs(entry)

    hub = KNXSceneCyclerHub(
        hass=hass,
        button_configs=button_configs,
    )

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name=hub_name,
        manufacturer="F. Wilhelm / Custom",
        model="KNX Scene Cycler",
    )

    domain_data = hass.data.setdefault(DOMAIN, {})
    domain_data[entry.entry_id] = {
        DATA_HUB: hub,
        CONF_HUB_NAME: hub_name,
    }

    try:
        await hass.config_entries.async_forward_entry_setups(
            entry,
            PLATFORMS,
        )
    except Exception:
        await hub.async_shutdown()
        domain_data.pop(entry.entry_id, None)

        if not domain_data:
            hass.data.pop(DOMAIN, None)

        raise

    entry.async_on_unload(
        entry.add_update_listener(async_reload_entry)
    )

    _LOGGER.debug(
        "Finished setting up config entry %s with %s button controller(s)",
        entry.entry_id,
        len(hub),
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload a KNX Scene Cycler config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if not unload_ok:
        return False

    domain_data = hass.data.get(DOMAIN, {})
    entry_data = domain_data.pop(entry.entry_id, None)

    if entry_data is not None:
        hub = entry_data.get(DATA_HUB)

        if isinstance(hub, KNXSceneCyclerHub):
            await hub.async_shutdown()

    if not domain_data:
        hass.data.pop(DOMAIN, None)

    _LOGGER.debug(
        "Unloaded KNX Scene Cycler config entry %s",
        entry.entry_id,
    )

    return True


async def async_reload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Reload the config entry after its configuration changes."""
    await hass.config_entries.async_reload(entry.entry_id)


def _get_hub_name(entry: ConfigEntry) -> str:
    """Return the configured hub name."""
    raw_name = entry.data.get(
        CONF_HUB_NAME,
        DEFAULT_HUB_NAME,
    )

    hub_name = str(raw_name).strip()

    return hub_name or DEFAULT_HUB_NAME


def _get_button_configs(
    entry: ConfigEntry,
) -> tuple[SceneButtonConfig, ...]:
    """Create immutable button configurations from config-entry data."""
    raw_buttons: Any = entry.data.get(CONF_BUTTONS, [])

    if not isinstance(raw_buttons, list):
        raise ValueError(
            f"Config entry field {CONF_BUTTONS!r} must be a list."
        )

    button_configs: list[SceneButtonConfig] = []

    for raw_button in raw_buttons:
        if not isinstance(raw_button, dict):
            raise ValueError(
                "Every configured scene button must be stored as a mapping."
            )

        button_configs.append(
            SceneButtonConfig.from_dict(raw_button)
        )

    return tuple(button_configs)
