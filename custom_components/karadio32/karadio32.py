import asyncio
import logging
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import TIMEOUT

_LOGGER = logging.getLogger(__name__)


class Karadio32Api:
    """Wrapper for karadio32 HTTP API."""

    def __init__(self, host: str, session):
        """Init wrapper."""
        _LOGGER.info("Initializing KaradioAPI")
        self.session = session
        self.host = host.rstrip("/")

    async def _request(self, params: dict[str, str], raises=False):
        try:
            async with asyncio.timeout(TIMEOUT):
                response = await self.session.get(self.host, params=params)
                return await response.text()
        except Exception:
            if raises:
                raise
            _LOGGER.exception("KaRadio32 connection error")
            return None

    async def setup_check(self):
        await self._request({"version": ""}, raises=True)

    async def info(self) -> dict[str, str]:
        result: dict[str, str] = {}
        response: str = await self._request({"infos": ""})
        
        # Корректная обработка отключенного устройства
        if not response:
            raise UpdateFailed("Device is offline")
            
        for line in response.strip("\n").split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                result[k.strip()] = v.strip()
        return result

    async def _list(self, i: int) -> str:
        return await self._request({"list": str(i)})

    async def source_list(self) -> list[str]:
        result: list[str] = []
        for i in range(254):
            response = await self._list(i)
            if not response:  # Защита от None, если устройство ушло в оффлайн во время чтения списка
                break
                
            c = response.strip()
            if c:
                result.append(c)
            else:
                break
        return result

    async def version(self):
        response = await self._request({"version": ""})
        return response.strip() if response else "Unknown"

    async def start(self):
        await self._request({"start": ""})

    async def stop(self):
        await self._request({"stop": ""})

    async def play(self, station_id: int):
        await self._request({"play": str(station_id)})

    async def next(self):
        await self._request({"next": ""})
        
    async def prev(self):
        await self._request({"prev": ""})

    async def set_volume(self, volume: float):
        level = max(0, min(volume, 1))
        await self._request({"volume": f"{255 * level:.0f}"})
