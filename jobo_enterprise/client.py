"""Synchronous and asynchronous clients for the Jobo Enterprise Jobs API."""

from __future__ import annotations

from datetime import datetime
from typing import AsyncIterator, Iterator, List, Optional, Union
from uuid import UUID

import httpx

from jobo_enterprise.exceptions import (
    JoboAuthenticationError,
    JoboError,
    JoboRateLimitError,
    JoboServerError,
    JoboValidationError,
)
from jobo_enterprise.models import (
    ExpiredJobIdsResponse,
    Job,
    JobFeedRequest,
    JobFeedResponse,
    JobSearchRequest,
    JobSearchResponse,
    LocationFilter,
)

_DEFAULT_BASE_URL = "https://jobs-api.jobo.world"
_DEFAULT_TIMEOUT = 30.0
_USER_AGENT = "jobo-python/1.0.0"


def _handle_error(response: httpx.Response) -> None:
    """Raise a typed exception based on the HTTP status code."""
    status = response.status_code
    try:
        body = response.json()
    except Exception:
        body = response.text

    detail = body.get("detail", "") if isinstance(body, dict) else str(body)
    message = f"HTTP {status}: {detail}" if detail else f"HTTP {status}"

    if status == 401:
        raise JoboAuthenticationError(message, status_code=status, detail=detail, response_body=body)
    if status == 429:
        retry_after = response.headers.get("Retry-After")
        raise JoboRateLimitError(
            message,
            status_code=status,
            detail=detail,
            response_body=body,
            retry_after=int(retry_after) if retry_after else None,
        )
    if status == 400:
        raise JoboValidationError(message, status_code=status, detail=detail, response_body=body)
    if status >= 500:
        raise JoboServerError(message, status_code=status, detail=detail, response_body=body)

    raise JoboError(message, status_code=status, detail=detail, response_body=body)


class JoboClient:
    """Synchronous client for the Jobo Enterprise Jobs API.

    Args:
        api_key: Your Jobo Enterprise API key.
        base_url: API base URL. Defaults to ``https://jobs-api.jobo.world``.
        timeout: Request timeout in seconds. Defaults to 30.
        httpx_client: Optional pre-configured ``httpx.Client`` instance.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = _DEFAULT_TIMEOUT,
        httpx_client: Optional[httpx.Client] = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._client = httpx_client or httpx.Client(
            base_url=self._base_url,
            timeout=timeout,
            headers={
                "X-Api-Key": api_key,
                "User-Agent": _USER_AGENT,
                "Accept": "application/json",
            },
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> "JoboClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    # ── Feed endpoints ──────────────────────────────────────────────

    def get_jobs_feed(
        self,
        *,
        locations: Optional[List[LocationFilter]] = None,
        sources: Optional[List[str]] = None,
        is_remote: Optional[bool] = None,
        posted_after: Optional[datetime] = None,
        cursor: Optional[str] = None,
        batch_size: int = 1000,
    ) -> JobFeedResponse:
        """Fetch a single batch of jobs from the feed.

        Args:
            locations: Structured location filters. Job matches ANY provided location.
            sources: ATS/source identifiers (e.g. ``"greenhouse"``, ``"workday"``).
            is_remote: ``True`` = remote only, ``False`` = on-site only, ``None`` = all.
            posted_after: Only jobs posted after this UTC datetime.
            cursor: Pagination cursor from a previous response.
            batch_size: Number of jobs per batch (1–1000). Defaults to 1000.

        Returns:
            A :class:`JobFeedResponse` with jobs, cursor, and pagination flag.
        """
        request = JobFeedRequest(
            locations=locations,
            sources=sources,
            is_remote=is_remote,
            posted_after=posted_after,
            cursor=cursor,
            batch_size=batch_size,
        )
        resp = self._client.post("/api/feed/jobs", json=request.model_dump(exclude_none=True))
        if resp.status_code != 200:
            _handle_error(resp)
        return JobFeedResponse.model_validate(resp.json())

    def iter_jobs_feed(
        self,
        *,
        locations: Optional[List[LocationFilter]] = None,
        sources: Optional[List[str]] = None,
        is_remote: Optional[bool] = None,
        posted_after: Optional[datetime] = None,
        batch_size: int = 1000,
    ) -> Iterator[Job]:
        """Iterate over all jobs in the feed, automatically handling pagination.

        Yields:
            Individual :class:`Job` objects.
        """
        cursor: Optional[str] = None
        while True:
            response = self.get_jobs_feed(
                locations=locations,
                sources=sources,
                is_remote=is_remote,
                posted_after=posted_after,
                cursor=cursor,
                batch_size=batch_size,
            )
            yield from response.jobs
            if not response.has_more:
                break
            cursor = response.next_cursor

    def get_expired_job_ids(
        self,
        *,
        expired_since: datetime,
        cursor: Optional[str] = None,
        batch_size: int = 1000,
    ) -> ExpiredJobIdsResponse:
        """Fetch a single batch of expired job IDs.

        Args:
            expired_since: UTC timestamp. Max 7 days in the past.
            cursor: Pagination cursor from a previous response.
            batch_size: Number of IDs per batch (1–10000). Defaults to 1000.

        Returns:
            An :class:`ExpiredJobIdsResponse` with job IDs and pagination info.
        """
        params: dict[str, Union[str, int]] = {
            "expired_since": expired_since.isoformat(),
            "batch_size": batch_size,
        }
        if cursor:
            params["cursor"] = cursor
        resp = self._client.get("/api/feed/jobs/expired", params=params)
        if resp.status_code != 200:
            _handle_error(resp)
        return ExpiredJobIdsResponse.model_validate(resp.json())

    def iter_expired_job_ids(
        self,
        *,
        expired_since: datetime,
        batch_size: int = 1000,
    ) -> Iterator[UUID]:
        """Iterate over all expired job IDs, automatically handling pagination.

        Yields:
            Individual job UUIDs.
        """
        cursor: Optional[str] = None
        while True:
            response = self.get_expired_job_ids(
                expired_since=expired_since,
                cursor=cursor,
                batch_size=batch_size,
            )
            yield from response.job_ids
            if not response.has_more:
                break
            cursor = response.next_cursor

    # ── Search endpoints ────────────────────────────────────────────

    def search_jobs(
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

    def search_jobs_advanced(
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

    def iter_search_jobs(
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
            response = self.search_jobs_advanced(
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


class AsyncJoboClient:
    """Asynchronous client for the Jobo Enterprise Jobs API.

    Args:
        api_key: Your Jobo Enterprise API key.
        base_url: API base URL. Defaults to ``https://jobs-api.jobo.world``.
        timeout: Request timeout in seconds. Defaults to 30.
        httpx_client: Optional pre-configured ``httpx.AsyncClient`` instance.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = _DEFAULT_TIMEOUT,
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._client = httpx_client or httpx.AsyncClient(
            base_url=self._base_url,
            timeout=timeout,
            headers={
                "X-Api-Key": api_key,
                "User-Agent": _USER_AGENT,
                "Accept": "application/json",
            },
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncJoboClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    # ── Feed endpoints ──────────────────────────────────────────────

    async def get_jobs_feed(
        self,
        *,
        locations: Optional[List[LocationFilter]] = None,
        sources: Optional[List[str]] = None,
        is_remote: Optional[bool] = None,
        posted_after: Optional[datetime] = None,
        cursor: Optional[str] = None,
        batch_size: int = 1000,
    ) -> JobFeedResponse:
        """Fetch a single batch of jobs from the feed."""
        request = JobFeedRequest(
            locations=locations,
            sources=sources,
            is_remote=is_remote,
            posted_after=posted_after,
            cursor=cursor,
            batch_size=batch_size,
        )
        resp = await self._client.post("/api/feed/jobs", json=request.model_dump(exclude_none=True))
        if resp.status_code != 200:
            _handle_error(resp)
        return JobFeedResponse.model_validate(resp.json())

    async def iter_jobs_feed(
        self,
        *,
        locations: Optional[List[LocationFilter]] = None,
        sources: Optional[List[str]] = None,
        is_remote: Optional[bool] = None,
        posted_after: Optional[datetime] = None,
        batch_size: int = 1000,
    ) -> AsyncIterator[Job]:
        """Iterate over all jobs in the feed, automatically handling pagination."""
        cursor: Optional[str] = None
        while True:
            response = await self.get_jobs_feed(
                locations=locations,
                sources=sources,
                is_remote=is_remote,
                posted_after=posted_after,
                cursor=cursor,
                batch_size=batch_size,
            )
            for job in response.jobs:
                yield job
            if not response.has_more:
                break
            cursor = response.next_cursor

    async def get_expired_job_ids(
        self,
        *,
        expired_since: datetime,
        cursor: Optional[str] = None,
        batch_size: int = 1000,
    ) -> ExpiredJobIdsResponse:
        """Fetch a single batch of expired job IDs."""
        params: dict[str, Union[str, int]] = {
            "expired_since": expired_since.isoformat(),
            "batch_size": batch_size,
        }
        if cursor:
            params["cursor"] = cursor
        resp = await self._client.get("/api/feed/jobs/expired", params=params)
        if resp.status_code != 200:
            _handle_error(resp)
        return ExpiredJobIdsResponse.model_validate(resp.json())

    async def iter_expired_job_ids(
        self,
        *,
        expired_since: datetime,
        batch_size: int = 1000,
    ) -> AsyncIterator[UUID]:
        """Iterate over all expired job IDs, automatically handling pagination."""
        cursor: Optional[str] = None
        while True:
            response = await self.get_expired_job_ids(
                expired_since=expired_since,
                cursor=cursor,
                batch_size=batch_size,
            )
            for job_id in response.job_ids:
                yield job_id
            if not response.has_more:
                break
            cursor = response.next_cursor

    # ── Search endpoints ────────────────────────────────────────────

    async def search_jobs(
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

    async def search_jobs_advanced(
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

    async def iter_search_jobs(
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
            response = await self.search_jobs_advanced(
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
