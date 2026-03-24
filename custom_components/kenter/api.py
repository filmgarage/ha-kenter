import asyncio
import logging
import time

import aiohttp

from .const import TOKEN_URL, API_URL

_LOGGER = logging.getLogger(__name__)


class KenterAPI:
    def __init__(self, client_id: str, client_secret: str, session: aiohttp.ClientSession):
        self._client_id = client_id
        self._client_secret = client_secret
        self._session = session
        self._token: str | None = None
        self._token_expires_at: float = 0

    async def _get_token(self):
        """Fetch a new OAuth token."""
        data = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "client_credentials",
            "scope": "meetdata.read",
        }
        async with asyncio.timeout(10):
            resp = await self._session.post(TOKEN_URL, data=data)
            resp.raise_for_status()
            js = await resp.json()
            self._token = js["access_token"]
            # Ververs token 60s vóór verlopen
            expires_in = js.get("expires_in", 3600)
            self._token_expires_at = time.monotonic() + expires_in - 60

    async def _headers(self) -> dict:
        """Geef auth headers terug; ververs token als nodig."""
        if not self._token or time.monotonic() >= self._token_expires_at:
            await self._get_token()
        return {"Authorization": f"Bearer {self._token}"}

    async def get_meters(self) -> list:
        headers = await self._headers()
        async with self._session.get(f"{API_URL}/meters", headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_measurements_day(
        self, connection_id: str, meter_id: str, year: int, month: int, day: int
    ) -> list:
        headers = await self._headers()
        url = (
            f"{API_URL}/measurements/connections/{connection_id}"
            f"/metering-points/{meter_id}/days/{year}/{month}/{day}"
        )
        async with self._session.get(url, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
