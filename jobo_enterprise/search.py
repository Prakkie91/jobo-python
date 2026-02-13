"""Sub-client for the Jobs Search endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import AsyncIterator, Iterator, List, Optional, Union

import httpx

from jobo_enterprise.exceptions import _handle_error
from jobo_enterprise.models import (
    Job,
    JobSearchRequest,
    JobSearchResponse,
)


class JobsSearchClient:
    """Synchronous sub-client for the Jobs Search endpoints.

    Access via ``client.search``.
    """

    def __init__(self, http: httpx.Client) -> None:
        self._client = http

    def search(
        self,
        *,
        q: Optional[str] = None,
        location: Optional[str] = None,
        sources: Optional[str] = None,
        remote: Optional[bool] = None,
        posted_after: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> JobSearchResponse:
        """Search jobs using simple query parameters (GET /api/jobs).

        Args:
            q: Free-text search query.
            location: Location string filter.
            sources: Comma-separated source identifiers.
            remote: ``True`` = remote only, ``False`` = on-site only.
            posted_after: Only jobs posted after this UTC datetime.
            page: Page number (1-indexed).
            page_size: Results per page (1–100).

        Returns:
            A :class:`JobSearchResponse` with jobs and pagination metadata.
        """
        params: dict[str, Union[str, int, bool]] = {}
        if q:
            params["q"] = q
        if location:
            params["location"] = location
        if sources:
            params["sources"] = sources
        if remote is not None:
            params["remote"] = remote
        if posted_after:
            params["posted_after"] = posted_after.isoformat()
        params["page"] = page
        params["page_size"] = page_size

        resp = self._client.get("/api/jobs", params=params)
        if resp.status_code != 200:
            _handle_error(resp)
        return JobSearchResponse.model_validate(resp.json())

    def search_advanced(
        self,
        *,
        queries: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        is_remote: Optional[bool] = None,
        posted_after: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> JobSearchResponse:
        """Search jobs using the advanced body-based endpoint (POST /api/jobs/search).

        Args:
            queries: Multiple search queries.
            locations: Multiple location strings.
            sources: ATS/source identifiers.
            is_remote: ``True`` = remote only, ``False`` = on-site only.
            posted_after: Only jobs posted after this UTC datetime.
            page: Page number (1-indexed).
            page_size: Results per page (1–100).

        Returns:
            A :class:`JobSearchResponse` with jobs and pagination metadata.
        """
        request = JobSearchRequest(
            queries=queries,
            locations=locations,
            sources=sources,
            is_remote=is_remote,
            posted_after=posted_after,
            page=page,
            page_size=page_size,
        )
        resp = self._client.post("/api/jobs/search", json=request.model_dump(exclude_none=True))
        if resp.status_code != 200:
            _handle_error(resp)
        return JobSearchResponse.model_validate(resp.json())

    def iter_jobs(
        self,
        *,
        queries: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        is_remote: Optional[bool] = None,
        posted_after: Optional[datetime] = None,
        page_size: int = 25,
    ) -> Iterator[Job]:
        """Iterate over all search results, automatically handling pagination.

        Uses the advanced search endpoint under the hood.

        Yields:
            Individual :class:`Job` objects.
        """
        page = 1
        while True:
            response = self.search_advanced(
                queries=queries,
                locations=locations,
                sources=sources,
                is_remote=is_remote,
                posted_after=posted_after,
                page=page,
                page_size=page_size,
            )
            yield from response.jobs
            if page >= response.total_pages:
                break
            page += 1


class AsyncJobsSearchClient:
    """Asynchronous sub-client for the Jobs Search endpoints.

    Access via ``client.search``.
    """

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._client = http

    async def search(
        self,
        *,
        q: Optional[str] = None,
        location: Optional[str] = None,
        sources: Optional[str] = None,
        remote: Optional[bool] = None,
        posted_after: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> JobSearchResponse:
        """Search jobs using simple query parameters (GET /api/jobs)."""
        params: dict[str, Union[str, int, bool]] = {}
        if q:
            params["q"] = q
        if location:
            params["location"] = location
        if sources:
            params["sources"] = sources
        if remote is not None:
            params["remote"] = remote
        if posted_after:
            params["posted_after"] = posted_after.isoformat()
        params["page"] = page
        params["page_size"] = page_size

        resp = await self._client.get("/api/jobs", params=params)
        if resp.status_code != 200:
            _handle_error(resp)
        return JobSearchResponse.model_validate(resp.json())

    async def search_advanced(
        self,
        *,
        queries: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        is_remote: Optional[bool] = None,
        posted_after: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> JobSearchResponse:
        """Search jobs using the advanced body-based endpoint (POST /api/jobs/search)."""
        request = JobSearchRequest(
            queries=queries,
            locations=locations,
            sources=sources,
            is_remote=is_remote,
            posted_after=posted_after,
            page=page,
            page_size=page_size,
        )
        resp = await self._client.post("/api/jobs/search", json=request.model_dump(exclude_none=True))
        if resp.status_code != 200:
            _handle_error(resp)
        return JobSearchResponse.model_validate(resp.json())

    async def iter_jobs(
        self,
        *,
        queries: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        is_remote: Optional[bool] = None,
        posted_after: Optional[datetime] = None,
        page_size: int = 25,
    ) -> AsyncIterator[Job]:
        """Iterate over all search results, automatically handling pagination."""
        page = 1
        while True:
            response = await self.search_advanced(
                queries=queries,
                locations=locations,
                sources=sources,
                is_remote=is_remote,
                posted_after=posted_after,
                page=page,
                page_size=page_size,
            )
            for job in response.jobs:
                yield job
            if page >= response.total_pages:
                break
            page += 1
