from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .channels import CHANNEL_MAP

DOMAIN = "kenter"

# Map device_class by unit
DEVICE_CLASS_MAP = {
    "kWh": "energy",
    "W": "power",
    "m³": "gas",
    "GJ": "energy",  # treat heat energy like electricity energy
    "°C": "temperature",
}

# Map state_class by unit
STATE_CLASS_MAP = {
    "kWh": "total_increasing",
    "W": "measurement",
    "m³": "total_increasing",
    "GJ": "total_increasing",
    "°C": "measurement",
}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Kenter sensors based on the config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    meters = coordinator.data.get("meters", [])

    entities = []
    for meter in meters:
        conn = meter["connectionId"]
        mpid = meter["meteringPointId"]
        for ch in meter["channels"]:
            entities.append(KenterSensor(coordinator, mpid, ch))
    async_add_entities(entities)


class KenterSensor(CoordinatorEntity, SensorEntity):
    """Representation of a single Kenter channel as a sensor."""

    def __init__(self, coordinator, meter_id, channel):
        super().__init__(coordinator)
        self._meter = meter_id
        self._ch = channel["channel"]
        self._unit = channel.get("unit")
        self._shortname = CHANNEL_MAP.get(self._ch, f"ch{self._ch}")

    @property
    def name(self):
        """Return the friendly name of the sensor."""
        return f"Kenter {self._meter} {self._shortname}"

    @property
    def unique_id(self):
        """Return a unique ID for this sensor."""
        return f"{self._meter}_{self._shortname}"

    @property
    def state(self):
        """Return the current value of the sensor."""
        return self.coordinator.data.get("values", {}).get(f"{self._meter}_{self._ch}")

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def device_class(self):
        """Return the device class based on unit."""
        return DEVICE_CLASS_MAP.get(self._unit)

    @property
    def state_class(self):
        """Return the state class for long-term statistics."""
        return STATE_CLASS_MAP.get(self._unit, "measurement")
