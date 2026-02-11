"""Official Python client for the Jobo Enterprise Jobs API."""

from jobo_enterprise.client import JoboClient, AsyncJoboClient
from jobo_enterprise.models import (
    Job,
    JobCompany,
    JobLocation,
    JobCompensation,
    LocationFilter,
    JobFeedRequest,
    JobFeedResponse,
    ExpiredJobIdsResponse,
    JobSearchRequest,
    JobSearchResponse,
)
from jobo_enterprise.exceptions import (
    JoboError,
    JoboAuthenticationError,
    JoboRateLimitError,
    JoboValidationError,
    JoboServerError,
)

__version__ = "1.0.0"

__all__ = [
    "JoboClient",
    "AsyncJoboClient",
    "Job",
    "JobCompany",
    "JobLocation",
    "JobCompensation",
    "LocationFilter",
    "JobFeedRequest",
    "JobFeedResponse",
    "ExpiredJobIdsResponse",
    "JobSearchRequest",
    "JobSearchResponse",
    "JoboError",
    "JoboAuthenticationError",
    "JoboRateLimitError",
    "JoboValidationError",
    "JoboServerError",
]
