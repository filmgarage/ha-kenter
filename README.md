# Kenter Metering integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)

This custom integration connects Home Assistant with the **Kenter Metering API**  
and creates sensors for each available meter and channel.

## Features
- Automatic token handling (no manual refresh required).
- Fetches your meter list daily.
- Fetches measurement data hourly.
- Creates sensors with entity IDs like:  

`sensor.kenter_<meterid>_<shortname>`

- Units are automatically set from the API (kWh, m³, etc.).

## Installation

### HACS (preferred)
1. Go to HACS → Integrations → Custom Repositories.
2. Add your repo URL (`https://github.com/filmgarage/ha-kenter`) as type *Integration*.
3. Search for "Kenter Metering" in HACS and install.
4. Restart Home Assistant.

### Manual
1. Copy the `kenter` folder into `config/custom_components/`.
2. Restart Home Assistant.

## Configuration
1. Go to Home Assistant → Settings → Devices & Services → Add Integration.
2. Search for **Kenter Metering**.
3. Enter your `client_id` and `client_secret` from the Kenter customer portal.
4. Done ✅

## Example sensors
- `sensor.kenter_00099999_consumption` → Supply of electrical energy
- `sensor.kenter_00099999_feed_in` → Feed-in / generation of electricity

## Notes
- Token is refreshed automatically (expires every hour).
- Meter list is refreshed once per day.
- Data is retrieved per day (recommended by Kenter API).

---

### Disclaimer
This integration is not affiliated with or endorsed by Kenter B.V.
