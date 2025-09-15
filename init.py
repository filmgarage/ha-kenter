import logging
from datetime import timedelta, date

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, PLATFORMS
from .api import KenterAPI

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    session = hass.helpers.aiohttp_client.async_get_clientsession(hass)
    api = KenterAPI(entry.data["client_id"], entry.data["client_secret"], session)

    async def async_update_data():
        """Fetch latest data."""
        today = date.today()
        meters = await api.get_meters()
        values = {}

        for m in meters:
            conn = m["connectionId"]
            mpid = m["meteringPointId"]
            try:
                measurements = await api.get_measurements_day(
                    conn, mpid, today.year, today.month, today.day
                )
                for ch in measurements:
                    cid = ch["channelId"]
                    if ch["Measurements"]:
                        latest = ch["Measurements"][-1]["value"]
                        values[f"{mpid}_{cid}"] = latest
            except Exception as e:
                _LOGGER.warning("Error fetching measurements for %s: %s", mpid, e)

        return {"meters": meters, "values": values}

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="kenter",
        update_method=async_update_data,
        update_interval=timedelta(hours=1),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
