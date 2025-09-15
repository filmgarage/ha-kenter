CHANNEL_MAP = {
    "10180": "consumption",
    "10280": "feed_in",
    "11181": "meter_low",
    "11182": "meter_high",
    "11281": "feed_in_low",
    "11282": "feed_in_high",
    "18280": "billing_feed_in",
    "18181": "billing_low",
    "18182": "billing_high",
    "70180": "gas_supply",
    "70280": "gas_feed_in",
    "71180": "gas_meter",
    "71380": "gas_meter_raw",
    "60100": "heat_temp_in",
    "60110": "heat_temp_out",
    "60180": "heat_energy",
    "80180": "water_supply",
    "80280": "water_return",
}

class KenterSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, meter_id, channel):
        super().__init__(coordinator)
        self._meter = meter_id
        self._ch = channel["channel"]
        self._unit = channel.get("unit")
        self._shortname = CHANNEL_MAP.get(self._ch, f"ch{self._ch}")

    @property
    def name(self):
        return f"Kenter {self._meter} {self._shortname}"

    @property
    def unique_id(self):
        return f"{self._meter}_{self._shortname}"

    @property
    def entity_id(self):
        return f"sensor.kenter_{self._meter}_{self._shortname}"

    @property
    def state(self):
        return self.coordinator.data.get("values", {}).get(f"{self._meter}_{self._ch}")

    @property
    def unit_of_measurement(self):
        return self._unit
