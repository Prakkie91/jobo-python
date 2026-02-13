"""Sub-client for the Locations/Geocoding endpoints."""

from __future__ import annotations

import httpx

from jobo_enterprise.exceptions import _handle_error
from jobo_enterprise.models import GeocodeResultItem


class LocationsClient:
    """Synchronous sub-client for the Locations/Geocoding endpoints.

    Access via ``client.locations``.
    """

    def __init__(self, http: httpx.Client) -> None:
        self._client = http

    def geocode(self, location: str) -> GeocodeResultItem:
        """Geocode a location string into structured locations with coordinates.

        Args:
            location: The location string to geocode (e.g., "San Francisco, CA" or "London, UK").

        Returns:
            A :class:`GeocodeResultItem` with resolved locations.
        """
        params = {"location": location}
        resp = self._client.get("/api/locations/geocode", params=params)
        if resp.status_code != 200:
            _handle_error(resp)
        return GeocodeResultItem.model_validate(resp.json())


class AsyncLocationsClient:
    """Asynchronous sub-client for the Locations/Geocoding endpoints.

    Access via ``client.locations``.
    """

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._client = http

    async def geocode(self, location: str) -> GeocodeResultItem:
        """Geocode a location string into structured locations with coordinates.

        Args:
            location: The location string to geocode (e.g., "San Francisco, CA" or "London, UK").

        Returns:
            A :class:`GeocodeResultItem` with resolved locations.
        """
        params = {"location": location}
        resp = await self._client.get("/api/locations/geocode", params=params)
        if resp.status_code != 200:
            _handle_error(resp)
        return GeocodeResultItem.model_validate(resp.json())
