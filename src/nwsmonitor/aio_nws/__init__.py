import aiohttp
import aiofiles
import pandas as pd
import json
import datetime
import logging
from dataclasses import dataclass
from geopy import Nominatim, Location
from typing import Optional, NamedTuple, Any, Union, Literal, List, Tuple

USER_AGENT = "(NWSMonitor/debug, nategreenwell@live.com)"
BASE_URL_IEM = "https://mesonet.agron.iastate.edu"
BASE_API_PATH_IEM = "/api/1"
BASE_URL_NWS = "https://api.weather.gov"
NWS_DATA_FORMAT = "application/ld+json"
_log = logging.getLogger(__name__)


@dataclass
class ActiveAlertsCount:
    total: int = 0
    land: int = 0
    marine: int = 0
    regions: dict = None
    areas: dict = None
    zones: dict = None

    def __init__(
        self,
        total: int = 0,
        land: int = 0,
        marine: int = 0,
        regions: dict = None,
        areas: dict = None,
        zones: dict = None,
    ) -> None:
        self.total = total
        self.land = land
        self.marine = marine
        if regions is None:
            self.regions = {}
        else:
            self.regions = regions
        if areas is None:
            self.areas = {}
        else:
            self.areas = areas
        if zones is None:
            self.zones = {}
        else:
            self.zones = zones

    def __repr__(self) -> str:
        return f"Total alerts: {self.total}. Land alerts: {self.land}. Marine alerts: {self.marine}."

    def __str__(self) -> str:
        return repr(self)


class Point(NamedTuple):
    lat: float
    lon: float


async def check_status(response: aiohttp.ClientResponse) -> None:
    if response.status not in {200, 301}:
        details = await response.json()
        headers = response.headers
        raise RuntimeError(f"Status {response.status}. {details=}; {headers=}")


async def fetch(
    client: aiohttp.ClientSession,
    api_call: str,
    accept: Optional[str] = None,
    **kwargs,
) -> Any:
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    _log.debug(f"Fetching {client._base_url}{api_call} with {headers=}")
    async with client.get(
        api_call, params=kwargs, headers=headers, raise_for_status=check_status
    ) as resp:
        _log.debug(f"Response headers: {resp.headers}")
        try:
            return await resp.json()
        except aiohttp.ClientResponseError:
            return await resp.text()


def locate(address: str) -> Tuple[Point, Location]:
    geolocator = Nominatim(user_agent=USER_AGENT)
    location = geolocator.geocode(address, country_codes="us")
    if location is None:
        raise RuntimeError(f"Could not geolocate {address} within the US.")
    return Point(location.latitude, location.longitude), location


async def afos(
    cccc: Optional[str] = None,
    pil: Optional[str] = None,
    date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    params = dict()
    if not (cccc or pil):
        raise ValueError("Either cccc or pil must be set.")

    if cccc:
        params["cccc"] = cccc

    if pil:
        params["pil"] = pil

    if date:
        params["date"] = date.isoformat()

    async with aiohttp.ClientSession(
        base_url=BASE_URL_IEM, raise_for_status=True
    ) as session:
        data = await fetch(session, f"{BASE_API_PATH_IEM}/nws/afos/list.json", **params)
        if not isinstance(data, dict):
            raise RuntimeError(f"Expected a dict, got {type(data).__name__}.")
        return pd.DataFrame(data["data"])


async def nwstext(pid: str) -> str:
    async with aiohttp.ClientSession(
        base_url=BASE_URL_IEM, raise_for_status=True
    ) as session:
        data = await fetch(session, f"{BASE_API_PATH_IEM}/nwstext/{pid}")
        return data


async def active_alerts_count() -> ActiveAlertsCount:
    async with aiohttp.ClientSession(
        base_url=BASE_URL_NWS, raise_for_status=check_status
    ) as session:
        data = await fetch(session, f"/alerts/active/count")
        return ActiveAlertsCount(
            data["total"],
            data["land"],
            data["marine"],
            data["regions"],
            data["areas"],
            data["zones"],
        )


async def alerts(
    *,
    active: bool = True,
    start: Optional[datetime.datetime] = None,
    end: Optional[datetime.datetime] = None,
    status: Optional[
        List[Literal["actual", "exercise", "system", "test", "draft"]]
    ] = None,
    message_type: Optional[List[Literal["alert", "update", "cancel"]]] = None,
    event: Optional[List[str]] = None,
    code: Optional[List[str]] = None,
    area: Optional[List[str]] = None,
    point: Optional[Tuple[float, float]] = None,
    region: Optional[List[Literal["AL", "AT", "GL", "GM", "PA", "PI"]]] = None,
    region_type: Optional[Literal["land", "marine"]] = None,
    zone: Optional[List[str]] = None,
    urgency: Optional[
        List[Literal["Immediate", "Expected", "Future", "Past", "Unknown"]]
    ] = None,
    severity: Optional[
        List[Literal["Extreme", "Severe", "Moderate", "Minor", "Unknown"]]
    ] = None,
    certainty: Optional[
        List[Literal["Observed", "Likely", "Possible", "Unlikely", "Unknown"]]
    ] = None,
    limit: int = 500,
    cursor: Optional[str] = None,
    **kwargs,
) -> pd.DataFrame:
    params = {}
    if active:
        api_call = "/alerts/active"
    else:
        api_call = "/alerts"
        if start:
            if start.tzinfo is None:
                raise ValueError("A time zone must be specified.")
            params["start"] = start.isoformat()
        if end:
            if end.tzinfo is None:
                raise ValueError("A time zone must be specified.")
            params["end"] = end.isoformat()

    if status:
        params["status"] = status
    if message_type:
        params["message_type"] = message_type
    if event:
        params["event"] = event
    if code:
        params["code"] = code
    if area:
        params["area"] = area
    if point:
        params["point"] = point
    if region:
        params["region"] = region
    if region_type:
        params["region_type"] = region
    if zone:
        params["zone"] = zone
    if urgency:
        params["urgency"] = urgency
    if severity:
        params["severity"] = severity
    if certainty:
        params["certainty"] = certainty
    if limit:
        params["limit"] = limit
    if cursor:
        params["cursor"] = cursor

    async with aiohttp.ClientSession(
        base_url=BASE_URL_NWS, raise_for_status=check_status
    ) as session:
        data = await fetch(session, api_call, NWS_DATA_FORMAT, **params)
        return pd.DataFrame(data["@graph"])


async def alerts_for_location(address: str, **kwargs) -> pd.DataFrame:
    point = locate(address)[0]
    return await alerts(point=point, **kwargs)


async def glossary() -> pd.DataFrame:
    async with aiohttp.ClientSession(
        base_url=BASE_URL_NWS, raise_for_status=check_status
    ) as session:
        data = await fetch(session, "/glossary")
        return pd.DataFrame(data["glossary"])


async def point_forecast(
    point: Tuple[float, float], units: Optional[Literal["us", "si"]] = "us"
) -> Tuple[Any, pd.DataFrame]:
    async with aiohttp.ClientSession(
        base_url=BASE_URL_NWS, raise_for_status=check_status
    ) as session:
        html_point = f"{point[0]},{point[1]}"
        data = await fetch(session, f"/points/{html_point}", NWS_DATA_FORMAT)
        wfo = data["cwa"]
        x = data["gridX"]
        y = data["gridY"]
        gridpoint = f"/gridpoints/{wfo}/{x},{y}"
        forecast = await fetch(
            session, f"{gridpoint}/forecast", NWS_DATA_FORMAT, units=units
        )
        stations = await fetch(session, f"{gridpoint}/stations", NWS_DATA_FORMAT)
        stations = pd.DataFrame(stations["@graph"])
        station = stations["stationIdentifier"][0]
        obs = await fetch(
            session,
            f"/stations/{station}/observations/latest",
            NWS_DATA_FORMAT,
            require_qc="false",
        )
        return obs, pd.DataFrame(forecast["periods"])


async def get_forecast(
    address: str, units: Optional[Literal["us", "si"]] = "us"
) -> Tuple[Any, pd.DataFrame, Location]:
    point, location = locate(address)
    return await point_forecast(point, units) + (location,)


async def ffg(address: str, valid: Optional[datetime.datetime] = None) -> pd.DataFrame:
    params = {}
    point = locate(address)[0]
    params["lon"] = point.lon
    params["lat"] = point.lat
    if valid:
        if valid.tzinfo is None:
            raise ValueError("A time zone must be specified.")
        params["valid"] = valid.isoformat()
    async with aiohttp.ClientSession(
        base_url=BASE_URL_IEM, raise_for_status=True
    ) as session:
        data = await fetch(session, f"{BASE_API_PATH_IEM}/ffg_bypoint.json", **params)
        return pd.DataFrame(data["ffg"])
