"""Platform for switch integration."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Wir importieren die KNX-Event-Konstanten aus der offiziellen KNX-Integration
from homeassistant.components.knx import KNX_ADDRESS, KNX_MODULE
from homeassistant.components.knx.const import EVENT_KNX_TELEGRAM

from .const import (
    DOMAIN,
    CONF_GA_SCENE_SELECT,
    CONF_GA_SWITCH,
    CONF_GA_STATUS_LED,
    CONF_SCENE_1,
    CONF_SCENE_2,
    CONF_SCENE_3,
    CONF_SCENE_4,
    CONF_SCENE_5_NEUTRAL,
    CONF_KNX_NUM_1,
    CONF_KNX_NUM_2,
    CONF_KNX_NUM_3,
    CONF_KNX_NUM_4,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the KNX Scene Cycler switches from a config entry."""
    config_data = hass.data[DOMAIN][config_entry.entry_id]
    functions = config_data.get("functions", [])

    switches = []
    # Für jede konfigurierte Taste/Funktion erstellen wir eine eigene Entität
    for idx, func_config in enumerate(functions):
        switches.append(
            KnxSceneCyclerSwitch(hass, config_entry, func_config, idx + 1)
        )

    async_add_entities(switches)


class KnxSceneCyclerSwitch(SwitchEntity):
    """Representation of a KNX Scene Cycler Switch/Button function."""

    _attr_has_entity_name = True

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, func_config: dict[str, Any], index: int
    ) -> None:
        """Initialize the switch."""
        self.hass = hass
        self._config = func_config
        self._entry_id = config_entry.entry_id
        self._index = index

        # Namen und IDs generieren
        self._attr_name = f"Taste {index}"
        self._attr_unique_id = f"{config_entry.entry_id}_button_{index}"

        # Zuordnung zum übergeordneten Hauptgerät (Glastaster)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
        )

        # Interner Zustand des virtuellen Schalters (Status) & Gedächtnis (Letzte Szene)
        self._is_on = False
        self._last_active_scene = self._config[CONF_SCENE_1] # Fallback auf Szene 1

        # Gruppenadressen aus der Konfiguration auslesen
        self._ga_scene_select = self._config[CONF_GA_SCENE_SELECT]
        self._ga_switch = self._config[CONF_GA_SWITCH]
        self._ga_status_led = self._config.get(CONF_GA_STATUS_LED, "")

    async def async_added_to_hass(self) -> None:
        """Register KNX telegram listeners when added to hass."""
        # Wir hängen uns an den offiziellen KNX Telegram-Bus von Home Assistant
        self.async_on_remove(
            self.hass.bus.async_listen(EVENT_KNX_TELEGRAM, self._async_handle_knx_telegram)
        )

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Triggered when turned ON via Dashboard."""
        await self._async_activate_scene(self._last_active_scene, set_state=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Triggered when turned OFF via Dashboard."""
        await self._async_activate_scene(self._config[CONF_SCENE_5_NEUTRAL], set_state=False)

    async def _async_activate_scene(self, scene_entity_id: str, set_state: bool) -> None:
        """Helper to activate a Home Assistant scene and sync states."""
        # 1. Szene einschalten
        await self.hass.services.async_call(
            "scene", "turn_on", {"entity_id": scene_entity_id}, blocking=True
        )

        # 2. Internen Zustand aktualisieren
        self._is_on = set_state
        if set_state:
            self._last_active_scene = scene_entity_id
        
        self.async_write_ha_state()

        # 3. Status zurück an KNX Gruppenadresse der Status-LED senden
        if self._ga_status_led:
            payload = 1 if set_state else 0
            # Wir nutzen die offizielle KNX-Schnittstelle, um das Telegramm zu senden
            await self.hass.services.async_call(
                "knx", "send", {"address": self._ga_status_led, "payload": payload}
            )

    @callback
    def _async_handle_knx_telegram(self, event: Any) -> None:
        """Handle incoming KNX telegrams."""
        telegram = event.data
        destination = telegram.get("destination")
        
        # Sicherheitsprüfung: Handelt es sich um ein Schreibtelegramm?
        if telegram.get("direction") != "Incoming" or telegram.get("telegramtype") != "GroupValueWrite":
            return

        # --- FALL 1: Kurzer Druck (Szenenwahl) ---
        if destination == self._ga_scene_select:
            value = telegram.get("value")
            if value is None:
                return
                
            # Wir gleichen den empfangenen KNX-Wert mit den konfigurierten Nummern ab
            target_scene = None
            if int(value) == int(self._config[CONF_KNX_NUM_1]):
                target_scene = self._config[CONF_SCENE_1]
            elif int(value) == int(self._config[CONF_KNX_NUM_2]):
                target_scene = self._config[CONF_SCENE_2]
            elif int(value) == int(self._config[CONF_KNX_NUM_3]):
                target_scene = self._config[CONF_SCENE_3]
            elif int(value) == int(self._config[CONF_KNX_NUM_4]):
                target_scene = self._config[CONF_SCENE_4]

            if target_scene:
                # Szene aktivieren und Status auf AN setzen
                self.hass.async_create_task(
                    self._async_activate_scene(target_scene, set_state=True)
                )

        # --- FALL 2: Langer Druck (Schalten) ---
        elif destination == self._ga_switch:
            # Da laut ETS-Parametrierung bei langem Druck immer eine '0' (data: 0) gesendet wird:
            data_val = telegram.get("data")
            if data_val == 0:
                if self._is_on:
                    # System ist AN -> Neutral-/Aus-Szene aktivieren
                    self.hass.async_create_task(
                        self._async_activate_scene(self._config[CONF_SCENE_5_NEUTRAL], set_state=False)
                    )
                else:
                    # System ist AUS -> Letzte gemerkte Szene wiederherstellen
                    self.hass.async_create_task(
                        self._async_activate_scene(self._last_active_scene, set_state=True)
                    )
