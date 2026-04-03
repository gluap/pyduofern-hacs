import logging
import math

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import voluptuous as vol

from homeassistant.components.light import (
    ColorMode,
    LightEntity,
    PLATFORM_SCHEMA,
    ATTR_BRIGHTNESS,
)

from homeassistant.core import HomeAssistant
from pyduofern.duofern_stick import DuofernStickThreaded

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional('serial_port', default=None): cv.string,
    vol.Optional('config_file', default=None): cv.string,
    vol.Optional('code', default=None): cv.string,
})


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    stick: DuofernStickThreaded = hass.data["duofern"]['stick']

    for device in stick.config['devices']:
        if device['id'].startswith('46') or device['id'].startswith('48'):
            if device['id'] in hass.data[DOMAIN]['devices'].keys():
                continue
            async_add_entities([DuofernLight(device['id'], device['name'], stick, hass)])

        if device['id'].startswith('43'):
            for channel in [1, 2]:
                chanNo = "{:02x}".format(channel)
                if device['id'] + chanNo in hass.data[DOMAIN]['devices'].keys():
                    continue
                async_add_entities([
                    DuofernLight(device['id'], device['name'], stick, hass, channel=channel)
                ])


class DuofernLight(LightEntity):
    def __init__(
        self,
        code: str,
        desc: str,
        stick: DuofernStickThreaded,
        hass: HomeAssistant,
        channel: int | None = None
    ):
        self._code = code
        self._id = code
        self._name = desc

        if channel:
            chanNo = "{:02x}".format(channel)
            self._id += chanNo
            self._name += chanNo

        self._stick = stick
        self._channel = channel

        hass.data[DOMAIN]['devices'][self._id] = self

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._id

    @property
    def is_on(self) -> bool | None:
        try:
            state = self._stick.duofern_parser.get_state(
                self._code, 'state', channel=self._channel
            )
            return state != "off"
        except KeyError:
            return None

    @property
    def brightness(self) -> int | None:
        if self._code.startswith("48"):
            level = self._stick.duofern_parser.get_state(
                self._code, 'level', channel=self._channel
            )
            if level is None:
                return None
            return math.ceil(int(level) / 100.0 * 255)
        return None

    # ✅ FIX: return right set
    @property
    def supported_color_modes(self) -> set[ColorMode]:
        if self._code.startswith("48"):
            return {ColorMode.BRIGHTNESS}
        else:
            return {ColorMode.ONOFF}

    # ✅ FIX: REQUIRED in new HA version
    @property
    def color_mode(self) -> ColorMode:
        if self._code.startswith("48"):
            return ColorMode.BRIGHTNESS
        else:
            return ColorMode.ONOFF

    def turn_on(self, **kwargs: int) -> None:
        if self._code.startswith("48"):
            brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
            level = math.ceil(brightness / 255.0 * 100)

            if ATTR_BRIGHTNESS in kwargs:
                self._stick.command(
                    self._code, "level", level, channel=self._channel
                )
            else:
                self._stick.command(
                    self._code, "on", channel=self._channel
                )

            # Hotfix für verzögerten Status
            self._stick.duofern_parser.update_state(
                self._code, 'level', str(level), channel=self._channel
            )
            self._stick.duofern_parser.update_state(
                self._code, 'state', str(level), channel=self._channel
            )
        else:
            self._stick.command(self._code, "on", channel=self._channel)
            self._stick.duofern_parser.update_state(
                self._code, 'state', "on", channel=self._channel
            )

    def turn_off(self, **kwargs: None) -> None:
        self._stick.command(self._code, "off", channel=self._channel)
        self._stick.duofern_parser.update_state(
            self._code, 'state', "off", channel=self._channel
        )

    def update(self, **kwargs: None) -> None:
        passimport logging
import math

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import voluptuous as vol

from homeassistant.components.light import (
    ColorMode,
    LightEntity,
    PLATFORM_SCHEMA,
    ATTR_BRIGHTNESS,
)

from homeassistant.core import HomeAssistant
from pyduofern.duofern_stick import DuofernStickThreaded

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional('serial_port', default=None): cv.string,
    vol.Optional('config_file', default=None): cv.string,
    vol.Optional('code', default=None): cv.string,
})


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    stick: DuofernStickThreaded = hass.data["duofern"]['stick']

    for device in stick.config['devices']:
        if device['id'].startswith('46') or device['id'].startswith('48'):
            if device['id'] in hass.data[DOMAIN]['devices'].keys():
                continue
            async_add_entities([DuofernLight(device['id'], device['name'], stick, hass)])

        if device['id'].startswith('43'):
            for channel in [1, 2]:
                chanNo = "{:02x}".format(channel)
                if device['id'] + chanNo in hass.data[DOMAIN]['devices'].keys():
                    continue
                async_add_entities([
                    DuofernLight(device['id'], device['name'], stick, hass, channel=channel)
                ])


class DuofernLight(LightEntity):
    def __init__(
        self,
        code: str,
        desc: str,
        stick: DuofernStickThreaded,
        hass: HomeAssistant,
        channel: int | None = None
    ):
        self._code = code
        self._id = code
        self._name = desc

        if channel:
            chanNo = "{:02x}".format(channel)
            self._id += chanNo
            self._name += chanNo

        self._stick = stick
        self._channel = channel

        hass.data[DOMAIN]['devices'][self._id] = self

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._id

    @property
    def is_on(self) -> bool | None:
        try:
            state = self._stick.duofern_parser.get_state(
                self._code, 'state', channel=self._channel
            )
            return state != "off"
        except KeyError:
            return None

    @property
    def brightness(self) -> int | None:
        if self._code.startswith("48"):
            level = self._stick.duofern_parser.get_state(
                self._code, 'level', channel=self._channel
            )
            if level is None:
                return None
            return math.ceil(int(level) / 100.0 * 255)
        return None

    # ✅ FIX: korrektes Set zurückgeben
    @property
    def supported_color_modes(self) -> set[ColorMode]:
        if self._code.startswith("48"):
            return {ColorMode.BRIGHTNESS}
        else:
            return {ColorMode.ONOFF}

    # ✅ FIX: REQUIRED in neuen HA-Versionen
    @property
    def color_mode(self) -> ColorMode:
        if self._code.startswith("48"):
            return ColorMode.BRIGHTNESS
        else:
            return ColorMode.ONOFF

    def turn_on(self, **kwargs: int) -> None:
        if self._code.startswith("48"):
            brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
            level = math.ceil(brightness / 255.0 * 100)

            if ATTR_BRIGHTNESS in kwargs:
                self._stick.command(
                    self._code, "level", level, channel=self._channel
                )
            else:
                self._stick.command(
                    self._code, "on", channel=self._channel
                )

            # Hotfix für verzögerten Status
            self._stick.duofern_parser.update_state(
                self._code, 'level', str(level), channel=self._channel
            )
            self._stick.duofern_parser.update_state(
                self._code, 'state', str(level), channel=self._channel
            )
        else:
            self._stick.command(self._code, "on", channel=self._channel)
            self._stick.duofern_parser.update_state(
                self._code, 'state', "on", channel=self._channel
            )

    def turn_off(self, **kwargs: None) -> None:
        self._stick.command(self._code, "off", channel=self._channel)
        self._stick.duofern_parser.update_state(
            self._code, 'state', "off", channel=self._channel
        )

    def update(self, **kwargs: None) -> None:
        pass