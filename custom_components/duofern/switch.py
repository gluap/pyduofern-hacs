import logging

from typing import List, Literal

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from homeassistant.components.switch import SwitchEntity

from custom_components.duofern.cover import is_shutter
from pyduofern.duofern_stick import DuofernStickThreaded

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup the Duofern switch platform."""

    stick = hass.data[DOMAIN]['stick']
    alreadyAddedEntityIds = hass.data[DOMAIN]['devices'].keys()

    to_add: List[SwitchEntity] = []
    _LOGGER.info("found: " + str(stick.config['devices']))
    _LOGGER.info("already added: " + str(stick.config['devices']))
    for duofernDevice in stick.config['devices']:
        duofernId: str = duofernDevice['id']
        if not is_shutter(duofernId) or duofernId not in alreadyAddedEntityIds:
            _LOGGER.info("skipping: " + str(duofernId))
            continue

        entityId = duofernId + "_manual_mode"
        if entityId not in alreadyAddedEntityIds:        
            to_add.append(DuofernShutterConfigurableSwitch(duofernId, stick, "manualMode", "Manual Mode", "manual_mode"))

    async_add_entities(to_add)

class DuofernShutterConfigurableSwitch(SwitchEntity):
    def __init__(self, duofernId: str, stick: DuofernStickThreaded, command: str, nameSuffix: str, idSuffix: str):
        """Initialize a switch of the shutter."""
        self._duofernId = duofernId
        self._stick = stick
        self._command = command
        self._nameSuffix = nameSuffix
        self._idSuffix = idSuffix
        self._state: Literal["on", "off"] | None = None

    @property
    def name(self) -> str:
        return self._duofernId + " " + self._nameSuffix

    @property
    def unique_id(self) -> str:
        return self._duofernId + "_" + self._idSuffix

    @property
    def device_info(self) -> DeviceInfo:
        """Return information about the device the entity belongs to group entities to devices"""
        return {
            "identifiers": {
                (DOMAIN, self._duofernId)
            }
        } #type: ignore #(We only care about a subset and DeviceInfo doesn't mark the rest as optional)
    
    @property
    def should_poll(self) -> bool:
        """Whether this entity should be polled or uses subscriptions"""
        return True

    @property
    def is_on(self) -> bool:
        return self._state == "on"

    def turn_on(self, **kwargs: None) -> None:
        """Turns the corresponding property of the shutter to on"""
        self._stick.command(self._duofernId, self._command, "on")

    def turn_off(self, **kwargs: None) -> None:
        """Turns the corresponding property of the shutter to on"""
        self._stick.command(self._duofernId, self._command, "off")
        
    def update(self)-> None:
        try:
            self._state = self._stick.duofern_parser.modules['by_code'][self._duofernId][self._command]
        except KeyError:
            self._state = None
