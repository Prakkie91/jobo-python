"""Exception types for the Jobo Enterprise client."""

from __future__ import annotations

from typing import Any, Optional


class JoboError(Exception):
    """Base exception for all Jobo client errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        detail: Optional[str] = None,
        response_body: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail
        self.response_body = response_body


class JoboAuthenticationError(JoboError):
    """Raised when the API key is missing or invalid (401)."""


class JoboRateLimitError(JoboError):
    """Raised when the rate limit is exceeded (429)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class JoboValidationError(JoboError):
    """Raised when the request is invalid (400)."""


class JoboServerError(JoboError):
    """Raised when the server returns a 5xx error."""
