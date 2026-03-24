import logging
from datetime import timedelta, date

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, PLATFORMS
from .api import KenterAPI

_LOGGER = logging.getLogger(__name__)

CH_DELIVERY_STAND    = "11180"
CH_RETURN_STAND      = "11280"
CH_DELIVERY_INTERVAL = "10180"
CH_RETURN_INTERVAL   = "10280"

WANTED_CHANNELS = {CH_DELIVERY_STAND, CH_RETURN_STAND,
                   CH_DELIVERY_INTERVAL, CH_RETURN_INTERVAL}

# Metingen met deze origin/status negeren
INVALID_ORIGINS  = {"Invalid"}
INVALID_STATUSES = {"Invalid"}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    api = KenterAPI(entry.data["client_id"], entry.data["client_secret"], session)

    async def async_update_data():
        today     = date.today()
        yesterday = today - timedelta(days=1)

        try:
            connections = await api.get_meters()
        except Exception as e:
            raise UpdateFailed(f"Error fetching meters: {e}") from e

        # Meetveld herkennen: relatedMeteringPointId is gevuld (verwijst naar meetplaats)
        # Meetplaats: relatedMeteringPointId is leeg/None
        physical_points = []
        for connection in connections:
            conn_id = connection["connectionId"]
            for mp in connection.get("meteringPoints", []):
                if not mp.get("relatedMeteringPointId"):
                    # Meetplaats (virtueel punt) → overslaan
                    continue
                channels = {ch["channel"] for ch in mp.get("channels", [])}
                if not channels & WANTED_CHANNELS:
                    continue

                md = mp.get("masterData", [{}])[0]
                # customName heeft prioriteit, anders adres
                display_name = (md.get("customName") or
                                f"{md.get('address', '')} {md.get('city', '')}".strip())

                # Verzamel de bijgewerkte dag-URLs uit meetdata_updates
                update_urls = [u["url"] for u in mp.get("meetdata_updates", [])]

                physical_points.append({
                    "connectionId":           conn_id,
                    "meteringPointId":        mp["meteringPointId"],
                    "relatedMeteringPointId": mp.get("relatedMeteringPointId", ""),
                    "meterNumber":            mp.get("meterNumber", ""),
                    "address":               md.get("address", ""),
                    "city":                  md.get("city", ""),
                    "customName":            md.get("customName"),
                    "displayName":           display_name,
                    "status":               md.get("status", ""),
                    "bpName":               md.get("bpName", ""),
                    "channels":             channels,
                    "update_urls":          update_urls,
                })

        ean_data = {}
        for mp in physical_points:
            conn  = mp["connectionId"]
            mpid  = mp["meteringPointId"]
            ean   = mp["connectionId"]

            # Gebruik meetdata_updates om te weten welke dagen beschikbaar zijn.
            # Die URLs bevatten het pad /days/{year}/{month}/{day} — parse de datum eruit.
            update_dates = _parse_update_dates(mp["update_urls"])

            # Tellerstand: meest recente datum uit updates, met fallback naar gisteren/vandaag
            stand_dates = sorted(update_dates, reverse=True) if update_dates else [yesterday, today]

            # Interval: altijd vandaag proberen (kan deels beschikbaar zijn)
            today_meas = await _fetch_day(api, conn, mpid, today)

            # Tellerstand ophalen van meest recente beschikbare dag
            del_stand = ret_stand = stand_date = None
            for d in stand_dates:
                meas = await _fetch_day(api, conn, mpid, d)
                ds = _extract_stand(meas, CH_DELIVERY_STAND)
                rs = _extract_stand(meas, CH_RETURN_STAND)
                if ds is not None or rs is not None:
                    del_stand  = ds
                    ret_stand  = rs
                    stand_date = d.isoformat()
                    break

            # Intervaldata van vandaag
            del_ivsum, del_ivcnt, del_estimated = _extract_intervals(
                today_meas, CH_DELIVERY_INTERVAL)
            ret_ivsum, ret_ivcnt, ret_estimated = _extract_intervals(
                today_meas, CH_RETURN_INTERVAL)

            # Geschatte stand: tellerstand van gisteren + intervallen van vandaag
            def estimated_stand(stand, stand_d, iv_sum):
                if stand is None:
                    return None
                if iv_sum is not None and stand_d == yesterday.isoformat():
                    return round(stand + iv_sum, 3)
                return stand  # stand is al van vandaag

            # Laatste enkele intervalwaarde (meest recente periode)
            def last_interval(measurements, channel):
                for ch in measurements:
                    if str(ch.get("channelId") or ch.get("channel")) != channel:
                        continue
                    mlist = ch.get("Measurements") or ch.get("measurements") or []
                    for m in reversed(mlist):
                        if m.get("origin") in INVALID_ORIGINS:
                            continue
                        if m.get("status") in INVALID_STATUSES:
                            continue
                        v = m.get("value")
                        if v is not None:
                            return float(v)
                return None

            ean_data[ean] = {
                "delivery_last_interval":    last_interval(today_meas, CH_DELIVERY_INTERVAL),
                "return_last_interval":      last_interval(today_meas, CH_RETURN_INTERVAL),
                "delivery_confirmed":       del_stand,
                "delivery_confirmed_date":  stand_date,
                "delivery_intervals":       del_ivsum,
                "delivery_interval_count":  del_ivcnt,
                "delivery_has_estimated":   del_estimated,
                "delivery_estimated":       estimated_stand(del_stand, stand_date, del_ivsum),
                "return_confirmed":         ret_stand,
                "return_confirmed_date":    stand_date,
                "return_intervals":         ret_ivsum,
                "return_interval_count":    ret_ivcnt,
                "return_has_estimated":     ret_estimated,
                "return_estimated":         estimated_stand(ret_stand, stand_date, ret_ivsum),
            }

        return {"meters": physical_points, "ean_data": ean_data}

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="kenter",
        update_method=async_update_data,
        update_interval=timedelta(minutes=5),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


def _parse_update_dates(urls: list) -> list:
    """Haal datums op uit meetdata_updates URL's: /days/{year}/{month}/{day}."""
    result = []
    for url in urls:
        parts = url.rstrip("/").split("/")
        try:
            # Zoek 'days' in het pad
            idx = parts.index("days")
            y, m, d = int(parts[idx+1]), int(parts[idx+2]), int(parts[idx+3])
            result.append(date(y, m, d))
        except (ValueError, IndexError):
            pass
    return result


def _extract_stand(measurements: list, channel: str):
    """Geeft de laatste geldige meterstand voor een kanaal, of None."""
    for ch in measurements:
        if str(ch.get("channelId") or ch.get("channel")) != channel:
            continue
        mlist = ch.get("Measurements") or ch.get("measurements") or []
        # Meest recente geldige meting (van achteren af)
        for m in reversed(mlist):
            if m.get("origin") in INVALID_ORIGINS:
                continue
            if m.get("status") in INVALID_STATUSES:
                continue
            v = m.get("value")
            if v is not None:
                return float(v)
    return None


def _extract_intervals(measurements: list, channel: str):
    """
    Telt geldige intervalwaarden op.
    Geeft (som, aantal, bevat_estimated) terug.
    """
    for ch in measurements:
        if str(ch.get("channelId") or ch.get("channel")) != channel:
            continue
        mlist = ch.get("Measurements") or ch.get("measurements") or []
        values = []
        has_estimated = False
        for m in mlist:
            if m.get("origin") in INVALID_ORIGINS:
                continue
            if m.get("status") in INVALID_STATUSES:
                continue
            if m.get("origin") == "Estimated":
                has_estimated = True
            v = m.get("value")
            if v is not None:
                values.append(float(v))
        if values:
            return round(sum(values), 3), len(values), has_estimated
    return None, 0, False


async def _fetch_day(api, conn_id, mpid, day):
    """Haal metingen op voor één dag. Geeft lege lijst terug bij fouten."""
    try:
        return await api.get_measurements_day(
            conn_id, mpid, day.year, day.month, day.day
        )
    except Exception as e:
        _LOGGER.debug("Fout bij ophalen %s op %s: %s", mpid, day, e)
        return []


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
