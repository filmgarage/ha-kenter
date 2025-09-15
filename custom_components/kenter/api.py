import aiohttp
import async_timeout
import logging
from .const import TOKEN_URL, API_URL

_LOGGER = logging.getLogger(__name__)

class KenterAPI:
    def __init__(self, client_id, client_secret, session: aiohttp.ClientSession):
        self._client_id = client_id
        self._client_secret = client_secret
        self._session = session
        self._token = None

    async def _get_token(self):
        """Fetch a new token (valid 1h)."""
        data = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "client_credentials",
            "scope": "meetdata.read"
        }
        async with async_timeout.timeout(10):
            resp = await self._session.post(TOKEN_URL, data=data)
            resp.raise_for_status()
            js = await resp.json()
            self._token = js["access_token"]

    async def _headers(self):
        if not self._token:
            await self._get_token()
        return {"Authorization": f"Bearer {self._token}"}

    async def get_meters(self):
        headers = await self._headers()
        async with self._session.get(f"{API_URL}/meters", headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_measurements_day(self, connection_id, meter_id, year, month, day):
        headers = await self._headers()
        url = f"{API_URL}/measurements/connections/{connection_id}/metering-points/{meter_id}/days/{year}/{month}/{day}"
        async with self._session.get(url, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
