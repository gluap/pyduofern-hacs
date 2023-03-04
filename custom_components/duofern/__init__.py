import logging
import os
import re
from typing import Any

# from homeassistant.const import 'serial_port', 'config_file', 'code'
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.helpers.typing import ConfigType

from pyduofern.duofern_stick import DuofernStickThreaded

from custom_components.duofern.domain_data import getDuofernStick, setupDomainData

# found advice in the homeassistant creating components manual
# https://home-assistant.io/developers/creating_components/
# Import the device class from the component that you want to support

# Home Assistant depends on 3rd party packages for API specific code.
REQUIREMENTS = ['pyduofern==0.34.1']

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN, DUOFERN_COMPONENTS

# Validation of the user's configuration
CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({
    vol.Optional('serial_port',
                 default="/dev/serial/by-id/usb-Rademacher_DuoFern_USB-Stick_WR04ZFP4-if00-port0"): cv.string,
    vol.Optional('config_file', default=os.path.join(os.path.dirname(__file__), "../../duofern.json")): cv.string,
    # config file: default to homeassistant config directory (assuming this is a custom component)
    vol.Optional('code', default="0000"): cv.string,
}),
}, extra=vol.ALLOW_EXTRA)


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Setup the duofern stick for communicating with the duofern devices via entities"""
    configEntries = hass.config_entries.async_entries(DOMAIN)
    if len(configEntries) == 0:
        _LOGGER.error("Expected one config entry from configuration flow, got less")
        return False

    if len(configEntries) > 1:
        _LOGGER.error("Expected one config entry from configuration flow, got more")
        return False

    serial_port = configEntries[0].data['serial_port']
    code = configEntries[0].data['code']
    configfile = configEntries[0].data['config_file']

    stick = DuofernStickThreaded(serial_port=serial_port, system_code=code, config_file_json=configfile,
                                      ephemeral=False)

    _registerServices(hass, stick, configEntries[0])
    _registerUpdateHassFromStickCallback(hass, stick)
    _registerStartStickHook(hass, stick)

    setupDomainData(hass, stick)

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup the Duofern Config entries (entities, devices, etc...)"""
    for component in DUOFERN_COMPONENTS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True



def _registerStartStickHook(hass: HomeAssistant, stick: DuofernStickThreaded) -> None:
    def started_callback(event: Any) -> None:
        stick.start() # Start the stick when ha is ready
    
    hass.bus.listen("homeassistant_started", started_callback)


def _registerUpdateHassFromStickCallback(hass: HomeAssistant, stick: DuofernStickThreaded) -> None:
    def update_callback(id: str | None, key: Any, value: Any) -> None:
        if id is not None:
            try:
                _LOGGER.info(f"Updatecallback for {id}")
                device = hass.data[DOMAIN]['devices'][id] # Get device by id
                if device.enabled:
                    try:
                        device.schedule_update_ha_state(True) # Trigger update on the updated entity
                    except AssertionError:
                        _LOGGER.info("Update callback called before HA is ready") # Trying to update before HA is ready
            except KeyError:
                _LOGGER.info("Update callback called on unknown device id") # Ignore invalid device ids

    stick.add_updates_callback(update_callback)

def _registerServices(hass: HomeAssistant, stick: DuofernStickThreaded, entry: ConfigEntry) -> None:
    def start_pairing(call: ServiceCall) -> None:
        _LOGGER.warning("start pairing")
        getDuofernStick(hass).pair(call.data.get('timeout', 60))

    def start_unpairing(call: ServiceCall) -> None:
        _LOGGER.warning("start pairing")
        getDuofernStick(hass).unpair(call.data.get('timeout', 60))

    def sync_devices(call: ServiceCall) -> None:
        stick.sync_devices()
        _LOGGER.warning(call)
        hass.config_entries.async_setup_platforms(entry, DUOFERN_COMPONENTS)

    def dump_device_state(call: ServiceCall) -> None:
        _LOGGER.warning(getDuofernStick(hass).duofern_parser.modules)

    def clean_config(call: ServiceCall) -> None:
        stick.clean_config()
        stick.sync_devices()

    def ask_for_update(call: ServiceCall) -> None:
        try:
            hass_device_id = call.data.get('device_id', None)
            device_id = re.sub(r"[^\.]*.([0-9a-fA-F]+)", "\\1", hass_device_id) if hass_device_id is not None else None
        except Exception:
            _LOGGER.exception(f"exception while getting device id {call}, {call.data}")
            raise
        if device_id is None:
            _LOGGER.warning(f"device_id missing from call {call.data}")
            return
        if device_id not in hass.data[DOMAIN]['stick'].duofern_parser.modules['by_code']:
            _LOGGER.warning(f"{device_id} is not a valid duofern device, I only know {hass.data[DOMAIN]['stick'].duofern_parser.modules['by_code'].keys()}")
            return
        getDuofernStick(hass).command(device_id, 'getStatus')

    PAIRING_SCHEMA = vol.Schema({
        vol.Optional('timeout', default=30): cv.positive_int,
    })

    UPDATE_SCHEMA = vol.Schema({
        vol.Required('device_id', default=None): cv.string,
    })

    hass.services.register(DOMAIN, 'start_pairing', start_pairing, PAIRING_SCHEMA)
    hass.services.register(DOMAIN, 'start_unpairing', start_unpairing, PAIRING_SCHEMA)
    hass.services.register(DOMAIN, 'sync_devices', sync_devices)
    hass.services.register(DOMAIN, 'clean_config', clean_config)
    hass.services.register(DOMAIN, 'dump_device_state', dump_device_state)
    hass.services.register(DOMAIN, 'ask_for_update', ask_for_update, UPDATE_SCHEMA)
