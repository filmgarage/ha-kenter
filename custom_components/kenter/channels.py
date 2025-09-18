"""Channel ID to shortname mapping for Kenter integration."""

CHANNEL_MAP = {
    # Electricity
    "10180": "consumption",       # Supply of electrical energy (kWh)
    "10280": "feed_in",           # Feed-in / generation of electrical energy (kWh)
    "11181": "meter_low",         # Meter reading delivery low rate (kWh)
    "11182": "meter_high",        # Meter reading delivery high rate (kWh)
    "11281": "feed_in_low",       # Meter reading feed-in low rate (kWh)
    "11282": "feed_in_high",      # Meter reading feed-in high rate (kWh)
    "18280": "billing_feed_in",   # Feed-in for billing (kWh)
    "18181": "billing_low",       # Low tariff supply for billing (kWh)
    "18182": "billing_high",      # High tariff supply for billing (kWh)

    # Gas
    "70180": "gas_supply",        # Derived supply volume (m³)
    "70280": "gas_feed_in",       # Derived feed-in volume (m³)
    "71180": "gas_meter",         # Gas meter reading supply (derived, m³)
    "71380": "gas_meter_raw",     # Gas meter reading supply (non-derived, m³)

    # Heat
    "60100": "heat_temp_in",      # Heat temperature supply (°C)
    "60110": "heat_temp_out",     # Heat temperature return (°C)
    "60180": "heat_energy",       # Supplied heat energy (GJ)

    # Water
    "80180": "water_supply",      # Water volume supply (m³)
    "80280": "water_return",      # Water volume return (m³)
}
