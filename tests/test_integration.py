"""Integration tests that call the live Jobo Enterprise API.

Requires the JOBO_API_KEY environment variable to be set.
Tests are skipped gracefully when the key is not available (local dev).
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import pytest

from jobo_enterprise.client import AsyncJoboClient, JoboClient
from jobo_enterprise.exceptions import JoboAuthenticationError
from jobo_enterprise.models import Job

API_KEY = os.environ.get("JOBO_API_KEY")
BASE_URL = os.environ.get("JOBO_BASE_URL", "https://jobs-api.jobo.world")

requires_api_key = pytest.mark.skipif(not API_KEY, reason="JOBO_API_KEY not set")


# ── Sync client: Feed ────────────────────────────────────────────────


@requires_api_key
class TestSyncFeed:
    def test_get_jobs_feed_returns_jobs(self, client: JoboClient):
        response = client.get_jobs_feed(batch_size=5)

        assert response is not None
        assert len(response.jobs) > 0
        assert len(response.jobs) <= 5

        job = response.jobs[0]
        assert job.id is not None
        assert job.title
        assert job.description
        assert job.listing_url
        assert job.source
        assert job.company is not None
        assert job.company.name

    def test_get_jobs_feed_with_location_filter(self, client: JoboClient):
        from jobo_enterprise.models import LocationFilter

        response = client.get_jobs_feed(
            locations=[LocationFilter(country="US")],
            batch_size=5,
        )

        assert response is not None
        assert len(response.jobs) > 0

    def test_get_jobs_feed_pagination(self, client: JoboClient):
        first = client.get_jobs_feed(batch_size=2)
        assert len(first.jobs) > 0

        if not first.has_more:
            pytest.skip("Dataset too small to test pagination")

        assert first.next_cursor

        second = client.get_jobs_feed(cursor=first.next_cursor, batch_size=2)
        assert second is not None
        assert len(second.jobs) > 0
        assert second.jobs[0].id != first.jobs[0].id

    def test_iter_jobs_feed_yields_jobs(self, client: JoboClient):
        jobs: list[Job] = []
        for job in client.iter_jobs_feed(batch_size=3):
            jobs.append(job)
            if len(jobs) >= 5:
                break

        assert len(jobs) > 0


# ── Sync client: Expired ─────────────────────────────────────────────


@requires_api_key
class TestSyncExpired:
    def test_get_expired_job_ids_returns_response(self, client: JoboClient):
        response = client.get_expired_job_ids(
            expired_since=datetime.now(timezone.utc) - timedelta(days=6),
            batch_size=5,
        )

        assert response is not None
        assert response.job_ids is not None


# ── Sync client: Search ──────────────────────────────────────────────


@requires_api_key
class TestSyncSearch:
    def test_search_jobs_returns_results(self, client: JoboClient):
        response = client.search_jobs(q="software engineer", page_size=5)

        assert response is not None
        assert len(response.jobs) > 0
        assert response.total > 0
        assert response.total_pages >= 1
        assert response.page == 1

    def test_search_jobs_advanced_returns_results(self, client: JoboClient):
        response = client.search_jobs_advanced(
            queries=["data engineer"],
            page_size=5,
        )

        assert response is not None
        assert len(response.jobs) > 0
        assert response.total > 0

    def test_search_jobs_advanced_with_location(self, client: JoboClient):
        response = client.search_jobs_advanced(
            queries=["developer"],
            locations=["New York"],
            page_size=5,
        )

        assert response is not None
        # May return 0 for very specific filters, but should not throw

    def test_iter_search_jobs_yields_jobs(self, client: JoboClient):
        jobs: list[Job] = []
        for job in client.iter_search_jobs(queries=["engineer"], page_size=3):
            jobs.append(job)
            if len(jobs) >= 5:
                break

        assert len(jobs) > 0


# ── Sync client: Job model validation ────────────────────────────────


@requires_api_key
class TestSyncJobModel:
    def test_job_has_expected_fields(self, client: JoboClient):
        response = client.search_jobs(q="engineer", page_size=1)
        assert len(response.jobs) > 0

        job = response.jobs[0]
        assert job.id is not None
        assert job.title
        assert job.company is not None
        assert job.company.id is not None
        assert job.company.name
        assert job.description
        assert job.listing_url
        assert job.apply_url
        assert job.source
        assert job.source_id
        assert job.created_at is not None
        assert job.updated_at is not None
        assert isinstance(job.is_remote, bool)
        assert isinstance(job.locations, list)


# ── Async client ─────────────────────────────────────────────────────


@requires_api_key
@pytest.mark.asyncio
class TestAsyncClient:
    async def test_get_jobs_feed(self, async_client: AsyncJoboClient):
        response = await async_client.get_jobs_feed(batch_size=5)

        assert response is not None
        assert len(response.jobs) > 0

        job = response.jobs[0]
        assert job.id is not None
        assert job.title

    async def test_search_jobs(self, async_client: AsyncJoboClient):
        response = await async_client.search_jobs(q="engineer", page_size=5)

        assert response is not None
        assert len(response.jobs) > 0
        assert response.total > 0

    async def test_search_jobs_advanced(self, async_client: AsyncJoboClient):
        response = await async_client.search_jobs_advanced(
            queries=["developer"],
            page_size=5,
        )

        assert response is not None
        assert len(response.jobs) > 0

    async def test_iter_jobs_feed(self, async_client: AsyncJoboClient):
        jobs: list[Job] = []
        async for job in async_client.iter_jobs_feed(batch_size=3):
            jobs.append(job)
            if len(jobs) >= 5:
                break

        assert len(jobs) > 0

    async def test_get_expired_job_ids(self, async_client: AsyncJoboClient):
        response = await async_client.get_expired_job_ids(
            expired_since=datetime.now(timezone.utc) - timedelta(days=6),
            batch_size=5,
        )

        assert response is not None
        assert response.job_ids is not None


# ── Error handling (always runs, no API key needed) ──────────────────


class TestErrorHandling:
    def test_invalid_api_key_raises_authentication_error(self):
        with JoboClient(api_key="invalid-key-12345", base_url=BASE_URL) as bad_client:
            with pytest.raises(JoboAuthenticationError):
                bad_client.get_jobs_feed(batch_size=1)

    @pytest.mark.asyncio
    async def test_invalid_api_key_raises_authentication_error_async(self):
        bad_client = AsyncJoboClient(api_key="invalid-key-12345", base_url=BASE_URL)
        try:
            with pytest.raises(JoboAuthenticationError):
                await bad_client.get_jobs_feed(batch_size=1)
        finally:
            await bad_client.close()
