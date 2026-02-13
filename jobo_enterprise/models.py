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


# ── Geocoding models ─────────────────────────────────────────────────


class GeocodedLocation(BaseModel):
    """A resolved/geocoded location."""

    display_name: str
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class GeocodeResultItem(BaseModel):
    """Response from the geocode endpoint."""

    input: str
    succeeded: bool
    locations: List[GeocodedLocation] = Field(default_factory=list)
    method: Optional[str] = None
    error: Optional[str] = None


# ── AutoApply models ─────────────────────────────────────────────────


class FieldAnswerFile(BaseModel):
    """A file upload answer for auto-apply."""

    file_name: str
    content_type: str
    data: str  # Base64 encoded


class FieldAnswer(BaseModel):
    """A field answer for auto-apply."""

    field_id: str
    value: Optional[str] = None
    values: Optional[List[str]] = None
    files: Optional[List[FieldAnswerFile]] = None


class StartAutoApplySessionRequest(BaseModel):
    """Request to start an auto-apply session."""

    apply_url: str


class SetAutoApplyAnswersRequest(BaseModel):
    """Request to set answers for an auto-apply session."""

    session_id: UUID
    answers: List[FieldAnswer]


class ValidationError(BaseModel):
    """Validation error from auto-apply."""

    field_id: str
    message: str


class FieldOption(BaseModel):
    """Option for a select/radio field."""

    value: str
    label: Optional[str] = None


class FieldValidations(BaseModel):
    """Validations for a form field."""

    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None


class FormFieldInfo(BaseModel):
    """Information about a form field in auto-apply."""

    id: str
    type: str
    label: Optional[str] = None
    required: bool = False
    placeholder: Optional[str] = None
    options: Optional[List[FieldOption]] = None
    validations: Optional[FieldValidations] = None


class AutoApplySessionResponse(BaseModel):
    """Response from an auto-apply session operation."""

    session_id: UUID
    provider_id: str
    provider_display_name: str
    success: bool
    status: str
    error: Optional[str] = None
    current_url: Optional[str] = None
    is_terminal: bool = False
    validation_errors: List[ValidationError] = Field(default_factory=list)
    fields: List[FormFieldInfo] = Field(default_factory=list)
