# Kenter Channel Mapping

This document provides an overview of the most common **channelId** values from the Kenter API  
and the **shortnames** that are used in Home Assistant for entity IDs.

Entity IDs in Home Assistant follow this pattern:

`sensor.kenter_<meterid>_<shortname>`

---

## 📊 Mapping Table

| ChannelId | Description (API)                            | Shortname        | Unit   |
|-----------|----------------------------------------------|------------------|--------|
| **Electricity** ||||
| 10180     | Supply of electrical energy                  | `consumption`    | kWh    |
| 10280     | Feed-in / generation of electrical energy    | `feed_in`        | kWh    |
| 11181     | Meter reading delivery low rate              | `meter_low`      | kWh    |
| 11182     | Meter reading delivery high rate             | `meter_high`     | kWh    |
| 11281     | Meter reading feed-in low rate               | `feed_in_low`    | kWh    |
| 11282     | Meter reading feed-in high rate              | `feed_in_high`   | kWh    |
| 18280     | Feed-in for billing                          | `billing_feed_in`| kWh    |
| 18181     | Low tariff supply for billing                | `billing_low`    | kWh    |
| 18182     | High tariff supply for billing               | `billing_high`   | kWh    |
| **Gas** ||||
| 70180     | Derived supply volume                        | `gas_supply`     | m³     |
| 70280     | Derived feed-in volume                       | `gas_feed_in`    | m³     |
| 71180     | Gas meter reading supply (derived)           | `gas_meter`      | m³     |
| 71380     | Gas meter reading supply (non-derived)       | `gas_meter_raw`  | m³     |
| **Heat** ||||
| 60100     | Heat temperature supply                      | `heat_temp_in`   | °C     |
| 60110     | Heat temperature return                      | `heat_temp_out`  | °C     |
| 60180     | Supplied heat energy                         | `heat_energy`    | GJ     |
| **Water** ||||
| 80180     | Water volume supply                          | `water_supply`   | m³     |
| 80280     | Water volume return                          | `water_return`   | m³     |

---

## ℹ️ Notes

- If a channelId is **not** in this list, the integration will automatically create a sensor with the shortname `ch<channelId>`.  
  Example: `sensor.kenter_00012345_ch99999`.  
- You can extend this list with new channels if Kenter adds more options to the API in the future.
