from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    meters = coordinator.data.get("meters", [])

    entities = []
    for meter in meters:
        conn = meter["connectionId"]
        mpid = meter["meteringPointId"]
        for ch in meter.get("channels", []):
            entities.append(KenterSensor(coordinator, mpid, ch))
    async_add_entities(entities)

class KenterSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, meter_id, channel):
        super().__init__(coordinator)
        self._meter = meter_id
        self._ch = channel["channel"]
        self._unit = channel.get("unit")

    @property
    def name(self):
        return f"Kenter {self._meter}_{self._ch}"

    @property
    def unique_id(self):
        return f"{self._meter}_{self._ch}"

    @property
    def state(self):
        return self.coordinator.data.get("values", {}).get(self.unique_id)

    @property
    def unit_of_measurement(self):
        return self._unit
