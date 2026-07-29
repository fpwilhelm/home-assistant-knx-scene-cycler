"""The KNX Scene Cycler integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, CONF_DEVICE_NAME

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SWITCH, Platform.SELECT]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up KNX Scene Cycler from a config entry."""
    _LOGGER.debug("Setting up config entry %s", entry.entry_id)

    device_name = entry.data.get(CONF_DEVICE_NAME, "KNX Scene Cycler")
    
    # 1. Hauptgerät in der Registry registrieren
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name=device_name,
        manufacturer="MDT / KNX Custom",
        model="Universal Scene Controller",
    )

    # 2. Daten im hass-Objekt speichern. Wir prüfen BEIDE Speicherorte (data und options)
    # Wenn der Nutzer nachträglich Tasten hinzufügt, landen diese in entry.options
    functions = entry.options.get("functions", entry.data.get("functions", []))
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        CONF_DEVICE_NAME: device_name,
        "functions": functions
    }

    # 3. Plattformen (Switch & Select) laden
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # WICHTIG: Höre auf Änderungen, wenn der Nutzer über "Konfigurieren" eine Taste hinzufügt
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options are updated (e.g. adding a button)."""
    _LOGGER.debug("Options updated, reloading integration entry")
    await hass.config_entries.async_reload(entry.entry_id)
