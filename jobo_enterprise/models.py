"""Pydantic models for the Jobo Enterprise Jobs API."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class JobCompany(BaseModel):
    """Company associated with a job listing."""

    id: UUID
    name: str


class JobLocation(BaseModel):
    """Geographic location of a job."""

    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class JobCompensation(BaseModel):
    """Compensation details for a job."""

    min: Optional[float] = Field(None, alias="min")
    max: Optional[float] = Field(None, alias="max")
    currency: Optional[str] = None
    period: Optional[str] = None
    raw_text: Optional[str] = None
    is_estimated: bool = False


class Job(BaseModel):
    """A job listing returned by the API."""

    id: UUID
    title: str
    company: JobCompany
    description: str
    listing_url: str
    apply_url: str
    locations: List[JobLocation] = Field(default_factory=list)
    compensation: Optional[JobCompensation] = None
    employment_type: Optional[str] = None
    workplace_type: Optional[str] = None
    experience_level: Optional[str] = None
    source: str
    source_id: str
    created_at: datetime
    updated_at: datetime
    date_posted: Optional[datetime] = None
    valid_through: Optional[datetime] = None
    is_remote: bool = False


class LocationFilter(BaseModel):
    """Structured location filter for the feed endpoint."""

    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None


class JobFeedRequest(BaseModel):
    """Request body for the jobs feed endpoint (POST /api/feed/jobs)."""

    locations: Optional[List[LocationFilter]] = None
    sources: Optional[List[str]] = None
    is_remote: Optional[bool] = None
    posted_after: Optional[datetime] = None
    cursor: Optional[str] = None
    batch_size: int = Field(default=1000, ge=1, le=1000)


class JobFeedResponse(BaseModel):
    """Response from the jobs feed endpoint."""

    jobs: List[Job] = Field(default_factory=list)
    next_cursor: Optional[str] = None
    has_more: bool = False


class ExpiredJobIdsResponse(BaseModel):
    """Response from the expired job IDs endpoint."""

    job_ids: List[UUID] = Field(default_factory=list)
    next_cursor: Optional[str] = None
    has_more: bool = False


class JobSearchRequest(BaseModel):
    """Request body for the advanced search endpoint (POST /api/jobs/search)."""

    queries: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    is_remote: Optional[bool] = None
    posted_after: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=100)


class JobSearchResponse(BaseModel):
    """Response from the search endpoints."""

    jobs: List[Job] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 25
    total_pages: int = 0
