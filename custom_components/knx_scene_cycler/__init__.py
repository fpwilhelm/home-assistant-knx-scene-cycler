"""The KNX Scene Cycler integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, CONF_DEVICE_NAME

_LOGGER = logging.getLogger(__name__)

# Wir definieren, welche Plattformen geladen werden sollen. In unserem Fall: switch
PLATFORMS: list[Platform] = [Platform.SWITCH]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up KNX Scene Cycler from a config entry."""
    _LOGGER.debug("Setting up config entry %s for DOMAIN %s", entry.entry_id, DOMAIN)

    # 1. Das übergeordnete Gerät (Device) in der Home Assistant Registry registrieren
    device_name = entry.data.get(CONF_DEVICE_NAME, "KNX Scene Cycler")
    
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name=device_name,
        manufacturer="MDT / KNX Custom",
        model="Universal Scene Controller",
    )

    # 2. Die Daten im hass-Objekt speichern, damit switch.py darauf zugreifen kann
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # 3. Den Switch-Plattform-Setup anstoßen (übergibt an switch.py)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Horcht auf spätere Änderungen über den Options Flow (wenn der Nutzer Tasten hinzufügt)
    entry.async_on_unload(entry.add_to_updates_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Entfernt alle Entitäten des Geräts sauber aus dem System, wenn die Integration gelöscht wird
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options are updated."""
    # Wird aufgerufen, wenn über "Konfigurieren" eine neue Taste hinzugefügt wurde
    await hass.config_entries.async_reload(entry.entry_id)
