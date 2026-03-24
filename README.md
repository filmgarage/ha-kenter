# ha-kenter

Home Assistant custom integration for [Kenter](https://www.kenter.nu) metering data via the Kenter Meetdata API.

## What it does

Creates sensors in Home Assistant for each electricity connection you have access to in the Kenter portal. Per connection you get four entities grouped under one device:

| Entity | Description | State class |
|--------|-------------|-------------|
| `sensor.{ean}_energy` | Cumulative delivery stand (kWh) | `total_increasing` |
| `sensor.{ean}_return` | Cumulative return stand (kWh) | `total_increasing` |
| `sensor.{ean}_interval_delivery` | Most recent delivery interval (kWh) | `measurement` |
| `sensor.{ean}_interval_return` | Most recent return interval (kWh) | `measurement` |

The cumulative sensors combine the confirmed meter reading with today's interval data to give the best available current estimate. Entity IDs are based on the EAN number and never change.

## Requirements

- Kenter account with API access enabled
- API client credentials (CLIENT ID + PASSWORD) from the Kenter portal via Account → API-clients → Toevoegen

## Installation

1. Copy the `custom_components/kenter` folder to your HA `config/custom_components/` directory
2. Restart Home Assistant
3. Go to Settings → Integrations → Add integration → search for **Kenter**
4. Enter your CLIENT ID and PASSWORD

## Configuration

The integration polls the Kenter API every 15 minutes by default. To change this, edit `update_interval` in `__init__.py`.

## Sensor attributes

All sensors include:

| Attribute | Description |
|-----------|-------------|
| `ean` | EAN connection number |
| `meter_number` | Physical meter serial number |
| `metering_point_id` | Kenter internal metering point ID |
| `related_metering_point_id` | Parent metering place ID |
| `status` | Connection status (Actief / In storing / In behandeling) |
| `client_name` | Account name in Kenter portal |

Cumulative sensors additionally include `confirmed_stand`, `confirmed_date`, `intervals_today`, `interval_count` and `contains_estimated` (true when Kenter used estimated data due to a fault).

## Notes

- Only physical meters (meetveld) are included; virtual billing points (meetplaats) are excluded
- Kenter provides interval data per 15 minutes with a short delay
- Data is available for the past 36 months via the API
