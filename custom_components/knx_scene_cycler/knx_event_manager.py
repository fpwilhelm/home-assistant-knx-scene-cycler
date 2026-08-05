"""Lifecycle management for Home Assistant KNX event registrations."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DATA_KNX_EVENT_MANAGER = "knx_scene_cycler_knx_event_manager"

KNX_DOMAIN = "knx"
KNX_EVENT_REGISTER_SERVICE = "event_register"
KNX_SCENE_NUMBER_TYPE = "scene_number"

ROLE_SCENE = "scene"
ROLE_TOGGLE = "toggle"


@dataclass
class _Registration:
    """Track one integration-owned KNX event registration."""

    role: str
    references: int


class KNXEventRegistrationManager:
    """Reference-count KNX event registrations across Config Entries."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the registration manager."""
        self._hass = hass
        self._registrations: dict[str, _Registration] = {}
        self._lock = asyncio.Lock()

    async def async_acquire(
        self,
        *,
        scene_addresses: set[str],
        toggle_addresses: set[str],
    ) -> None:
        """Acquire all registrations required by one Config Entry."""
        requested = _build_role_index(
            scene_addresses=scene_addresses,
            toggle_addresses=toggle_addresses,
        )

        async with self._lock:
            self._validate_roles(requested)
            newly_registered: list[str] = []

            try:
                for address, role in requested.items():
                    if address in self._registrations:
                        continue

                    await self._async_modify_registration(
                        address=address,
                        role=role,
                        remove=False,
                    )
                    newly_registered.append(address)
            except Exception:
                for address in reversed(newly_registered):
                    try:
                        await self._async_modify_registration(
                            address=address,
                            role=requested[address],
                            remove=True,
                        )
                    except Exception:
                        _LOGGER.exception(
                            "Failed to roll back KNX event registration "
                            "for %s",
                            address,
                        )
                raise

            for address, role in requested.items():
                registration = self._registrations.get(address)
                if registration is None:
                    self._registrations[address] = _Registration(
                        role=role,
                        references=1,
                    )
                else:
                    registration.references += 1

    async def async_release(
        self,
        *,
        scene_addresses: set[str],
        toggle_addresses: set[str],
    ) -> None:
        """Release registrations no longer used by one Config Entry."""
        requested = _build_role_index(
            scene_addresses=scene_addresses,
            toggle_addresses=toggle_addresses,
        )

        async with self._lock:
            for address, role in requested.items():
                registration = self._registrations.get(address)
                if registration is None:
                    continue

                if registration.references > 1:
                    registration.references -= 1
                    continue

                try:
                    await self._async_modify_registration(
                        address=address,
                        role=role,
                        remove=True,
                    )
                except Exception:
                    _LOGGER.exception(
                        "Failed to remove KNX event registration for %s",
                        address,
                    )
                finally:
                    self._registrations.pop(address, None)

    def _validate_roles(self, requested: dict[str, str]) -> None:
        """Reject addresses already registered for another input role."""
        for address, role in requested.items():
            registration = self._registrations.get(address)
            if (
                registration is not None
                and registration.role != role
            ):
                raise ValueError(
                    f"KNX group address {address!r} is already used as "
                    f"a {registration.role} input and cannot also be "
                    f"used as a {role} input."
                )

    async def _async_modify_registration(
        self,
        *,
        address: str,
        role: str,
        remove: bool,
    ) -> None:
        """Add or remove one KNX event registration."""
        service_data: dict[str, object] = {
            "address": address,
            "remove": remove,
        }

        if not remove and role == ROLE_SCENE:
            service_data["type"] = KNX_SCENE_NUMBER_TYPE

        await self._hass.services.async_call(
            KNX_DOMAIN,
            KNX_EVENT_REGISTER_SERVICE,
            service_data,
            blocking=True,
        )


def async_get_knx_event_registration_manager(
    hass: HomeAssistant,
) -> KNXEventRegistrationManager:
    """Return the shared KNX event registration manager."""
    manager = hass.data.get(DATA_KNX_EVENT_MANAGER)

    if not isinstance(manager, KNXEventRegistrationManager):
        manager = KNXEventRegistrationManager(hass)
        hass.data[DATA_KNX_EVENT_MANAGER] = manager

    return manager


def _build_role_index(
    *,
    scene_addresses: set[str],
    toggle_addresses: set[str],
) -> dict[str, str]:
    """Build and validate the requested address-role index."""
    conflicting_addresses = scene_addresses & toggle_addresses
    if conflicting_addresses:
        formatted_addresses = ", ".join(
            sorted(conflicting_addresses)
        )
        raise ValueError(
            "KNX group addresses cannot be used as both scene and "
            f"toggle inputs: {formatted_addresses}."
        )

    return {
        **dict.fromkeys(scene_addresses, ROLE_SCENE),
        **dict.fromkeys(toggle_addresses, ROLE_TOGGLE),
    }
