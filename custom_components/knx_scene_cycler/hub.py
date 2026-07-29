"""Hub for managing KNX Scene Cycler button controllers."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from homeassistant.core import HomeAssistant

from .controller import SceneButtonController
from .models import SceneButtonConfig
from .runtime import SceneButtonRuntime


class KNXSceneCyclerHub:
    """Manage all scene button controllers of one config entry."""

    def __init__(
        self,
        hass: HomeAssistant,
        button_configs: Iterable[SceneButtonConfig],
    ) -> None:
        """Initialize the hub and its button controllers."""
        self._hass = hass
        self._controllers: dict[str, SceneButtonController] = {}

        for button_config in button_configs:
            self.add_button(button_config)

    @property
    def controllers(self) -> tuple[SceneButtonController, ...]:
        """Return all button controllers."""
        return tuple(self._controllers.values())

    @property
    def button_ids(self) -> tuple[str, ...]:
        """Return all configured button IDs."""
        return tuple(self._controllers)

    def __iter__(self) -> Iterator[SceneButtonController]:
        """Iterate over all button controllers."""
        return iter(self._controllers.values())

    def __len__(self) -> int:
        """Return the number of configured buttons."""
        return len(self._controllers)

    def add_button(
        self,
        button_config: SceneButtonConfig,
    ) -> SceneButtonController:
        """Create and register a controller for one scene button."""
        button_id = button_config.button_id

        if button_id in self._controllers:
            raise ValueError(
                f"Button ID {button_id!r} is already registered."
            )

        runtime = SceneButtonRuntime(config=button_config)
        controller = SceneButtonController(
            hass=self._hass,
            runtime=runtime,
        )

        self._controllers[button_id] = controller

        return controller

    def get_controller(
        self,
        button_id: str,
    ) -> SceneButtonController:
        """Return the controller for one configured button."""
        try:
            return self._controllers[button_id]
        except KeyError as err:
            raise KeyError(
                f"Unknown KNX Scene Cycler button ID: {button_id!r}."
            ) from err

    def remove_button(
        self,
        button_id: str,
    ) -> SceneButtonController:
        """Remove and return one registered button controller."""
        try:
            return self._controllers.pop(button_id)
        except KeyError as err:
            raise KeyError(
                f"Unknown KNX Scene Cycler button ID: {button_id!r}."
            ) from err

    async def async_shutdown(self) -> None:
        """Shut down all button controllers."""
        for controller in self._controllers.values():
            await controller.shutdown()