from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    meters = coordinator.data.get("meters", [])

    entities = []
    for mp in meters:
        entities.append(KenterStandSensor(coordinator, mp, "delivery"))
        entities.append(KenterStandSensor(coordinator, mp, "return"))
        entities.append(KenterIntervalSensor(coordinator, mp, "delivery"))
        entities.append(KenterIntervalSensor(coordinator, mp, "return"))
    async_add_entities(entities)


def _device_info(coordinator, ean, meter_nr) -> DeviceInfo:
    """Gedeelde DeviceInfo voor alle sensoren van één aansluiting."""
    meters = coordinator.data.get("meters", [])
    mp = next((m for m in meters if m["connectionId"] == ean), {})
    display = mp.get("customName") or mp.get("displayName") or ean
    return DeviceInfo(
        identifiers={(DOMAIN, ean)},
        name=f"{display} ·{ean[-6:]}",
        manufacturer="Kenter",
        model="Slimme meter aansluiting",
        serial_number=meter_nr,
    )


def _common_attributes(mp: dict) -> dict:
    """Attributen die op alle sensoren van een aansluiting staan."""
    return {
        "ean":                       mp["connectionId"],
        "meter_number":              mp.get("meterNumber", ""),
        "metering_point_id":         mp.get("meteringPointId", ""),
        "related_metering_point_id": mp.get("relatedMeteringPointId", ""),
        "status":                    mp.get("status", ""),
        "client_name":               mp.get("bpName", ""),
    }


class KenterStandSensor(CoordinatorEntity, SensorEntity):
    """Cumulatieve tellerstand levering of teruglevering."""

    def __init__(self, coordinator, mp: dict, direction: str):
        super().__init__(coordinator)
        self._ean       = mp["connectionId"]
        self._mpid      = mp["meteringPointId"]
        self._meter_nr  = mp.get("meterNumber", "")
        self._direction = direction
        self._mp        = mp

        suffix = "energy" if direction == "delivery" else "return"
        label  = "Energy"  if direction == "delivery" else "Return"

        display = mp.get("customName") or mp.get("displayName") or self._ean
        self._attr_name      = f"{display} {label}"
        self._attr_unique_id = f"kenter_{self._ean}_{suffix}"
        self._entity_id_val  = f"sensor.{self._ean}_{suffix}"

    @property
    def entity_id(self) -> str:
        return self._entity_id_val

    @entity_id.setter
    def entity_id(self, value):
        pass

    @property
    def device_info(self) -> DeviceInfo:
        return _device_info(self.coordinator, self._ean, self._meter_nr)

    @property
    def _data(self) -> dict:
        return self.coordinator.data.get("ean_data", {}).get(self._ean, {})

    @property
    def native_value(self):
        key = "delivery_estimated" if self._direction == "delivery" else "return_estimated"
        return self._data.get(key)

    @property
    def native_unit_of_measurement(self) -> str:
        return "kWh"

    @property
    def device_class(self):
        return SensorDeviceClass.ENERGY

    @property
    def state_class(self):
        return SensorStateClass.TOTAL_INCREASING

    @property
    def extra_state_attributes(self) -> dict:
        d = self._data
        attrs = _common_attributes(self._mp)
        if self._direction == "delivery":
            attrs.update({
                "confirmed_stand":    d.get("delivery_confirmed"),
                "confirmed_date":     d.get("delivery_confirmed_date"),
                "intervals_today":    d.get("delivery_intervals"),
                "interval_count":     d.get("delivery_interval_count"),
                "contains_estimated": d.get("delivery_has_estimated", False),
            })
        else:
            attrs.update({
                "confirmed_stand":    d.get("return_confirmed"),
                "confirmed_date":     d.get("return_confirmed_date"),
                "intervals_today":    d.get("return_intervals"),
                "interval_count":     d.get("return_interval_count"),
                "contains_estimated": d.get("return_has_estimated", False),
            })
        return attrs


class KenterIntervalSensor(CoordinatorEntity, SensorEntity):
    """Meest recente intervalwaarde (5/15-min kWh) voor levering of teruglevering."""

    def __init__(self, coordinator, mp: dict, direction: str):
        super().__init__(coordinator)
        self._ean       = mp["connectionId"]
        self._mpid      = mp["meteringPointId"]
        self._meter_nr  = mp.get("meterNumber", "")
        self._direction = direction
        self._mp        = mp

        suffix = "interval_delivery" if direction == "delivery" else "interval_return"
        label  = "Interval Delivery"  if direction == "delivery" else "Interval Return"

        display = mp.get("customName") or mp.get("displayName") or self._ean
        self._attr_name      = f"{display} {label}"
        self._attr_unique_id = f"kenter_{self._ean}_{suffix}"
        self._entity_id_val  = f"sensor.{self._ean}_{suffix}"

    @property
    def entity_id(self) -> str:
        return self._entity_id_val

    @entity_id.setter
    def entity_id(self, value):
        pass

    @property
    def device_info(self) -> DeviceInfo:
        return _device_info(self.coordinator, self._ean, self._meter_nr)

    @property
    def _data(self) -> dict:
        return self.coordinator.data.get("ean_data", {}).get(self._ean, {})

    @property
    def native_value(self):
        key = "delivery_last_interval" if self._direction == "delivery" else "return_last_interval"
        return self._data.get(key)

    @property
    def native_unit_of_measurement(self) -> str:
        return "kWh"

    @property
    def device_class(self):
        return SensorDeviceClass.ENERGY

    @property
    def state_class(self):
        # Measurement: dit is verbruik per periode, geen oplopende teller
        return SensorStateClass.MEASUREMENT

    @property
    def extra_state_attributes(self) -> dict:
        d = self._data
        attrs = _common_attributes(self._mp)
        if self._direction == "delivery":
            attrs.update({
                "intervals_today":    d.get("delivery_intervals"),
                "interval_count":     d.get("delivery_interval_count"),
                "contains_estimated": d.get("delivery_has_estimated", False),
            })
        else:
            attrs.update({
                "intervals_today":    d.get("return_intervals"),
                "interval_count":     d.get("return_interval_count"),
                "contains_estimated": d.get("return_has_estimated", False),
            })
        return attrs
