"""Official Python client for the Jobo Enterprise API."""

from jobo_enterprise.client import JoboClient, AsyncJoboClient
from jobo_enterprise.feed import JobsFeedClient, AsyncJobsFeedClient
from jobo_enterprise.search import JobsSearchClient, AsyncJobsSearchClient
from jobo_enterprise.locations import LocationsClient, AsyncLocationsClient
from jobo_enterprise.auto_apply import AutoApplyClient, AsyncAutoApplyClient
from jobo_enterprise.models import (
    # Jobs
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
    # Geocoding
    GeocodeResultItem,
    GeocodedLocation,
    # AutoApply
    AutoApplySessionResponse,
    FieldAnswer,
    FieldAnswerFile,
    FormFieldInfo,
    FieldOption,
    FieldValidations,
    ValidationError,
)
from jobo_enterprise.exceptions import (
    JoboError,
    JoboAuthenticationError,
    JoboRateLimitError,
    JoboValidationError,
    JoboServerError,
)

__version__ = "2.0.0"

__all__ = [
    # Main clients
    "JoboClient",
    "AsyncJoboClient",
    # Sub-clients
    "JobsFeedClient",
    "AsyncJobsFeedClient",
    "JobsSearchClient",
    "AsyncJobsSearchClient",
    "LocationsClient",
    "AsyncLocationsClient",
    "AutoApplyClient",
    "AsyncAutoApplyClient",
    # Job models
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
    # Geocoding models
    "GeocodeResultItem",
    "GeocodedLocation",
    # AutoApply models
    "AutoApplySessionResponse",
    "FieldAnswer",
    "FieldAnswerFile",
    "FormFieldInfo",
    "FieldOption",
    "FieldValidations",
    "ValidationError",
    # Exceptions
    "JoboError",
    "JoboAuthenticationError",
    "JoboRateLimitError",
    "JoboValidationError",
    "JoboServerError",
]
