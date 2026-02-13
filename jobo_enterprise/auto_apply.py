"""Sub-client for the Auto Apply endpoints."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

import httpx

from jobo_enterprise.exceptions import _handle_error
from jobo_enterprise.models import (
    AutoApplySessionResponse,
    FieldAnswer,
    StartAutoApplySessionRequest,
    SetAutoApplyAnswersRequest,
)


class AutoApplyClient:
    """Synchronous sub-client for the Auto Apply endpoints.

    Access via ``client.auto_apply``.
    """

    def __init__(self, http: httpx.Client) -> None:
        self._client = http

    def start_session(self, apply_url: str) -> AutoApplySessionResponse:
        """Start a new auto-apply session for a job posting.

        Args:
            apply_url: The apply URL from the job listing.

        Returns:
            An :class:`AutoApplySessionResponse` with session details and form fields.
        """
        request = StartAutoApplySessionRequest(apply_url=apply_url)
        resp = self._client.post("/api/auto-apply/start", json=request.model_dump())
        if resp.status_code != 200:
            _handle_error(resp)
        return AutoApplySessionResponse.model_validate(resp.json())

    def set_answers(
        self,
        session_id: UUID,
        answers: List[FieldAnswer],
    ) -> AutoApplySessionResponse:
        """Set answers for an active auto-apply session.

        Args:
            session_id: The session ID from :meth:`start_session`.
            answers: List of field answers.

        Returns:
            An :class:`AutoApplySessionResponse` with updated session state.
        """
        request = SetAutoApplyAnswersRequest(session_id=session_id, answers=answers)
        resp = self._client.post("/api/auto-apply/set-answers", json=request.model_dump())
        if resp.status_code != 200:
            _handle_error(resp)
        return AutoApplySessionResponse.model_validate(resp.json())

    def end_session(self, session_id: UUID) -> bool:
        """End an auto-apply session.

        Args:
            session_id: The session ID to end.

        Returns:
            True if the session was successfully ended, False if not found.
        """
        resp = self._client.delete(f"/api/auto-apply/sessions/{session_id}")
        if resp.status_code == 200:
            return True
        if resp.status_code == 404:
            return False
        _handle_error(resp)
        return False


class AsyncAutoApplyClient:
    """Asynchronous sub-client for the Auto Apply endpoints.

    Access via ``client.auto_apply``.
    """

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._client = http

    async def start_session(self, apply_url: str) -> AutoApplySessionResponse:
        """Start a new auto-apply session for a job posting.

        Args:
            apply_url: The apply URL from the job listing.

        Returns:
            An :class:`AutoApplySessionResponse` with session details and form fields.
        """
        request = StartAutoApplySessionRequest(apply_url=apply_url)
        resp = await self._client.post("/api/auto-apply/start", json=request.model_dump())
        if resp.status_code != 200:
            _handle_error(resp)
        return AutoApplySessionResponse.model_validate(resp.json())

    async def set_answers(
        self,
        session_id: UUID,
        answers: List[FieldAnswer],
    ) -> AutoApplySessionResponse:
        """Set answers for an active auto-apply session.

        Args:
            session_id: The session ID from :meth:`start_session`.
            answers: List of field answers.

        Returns:
            An :class:`AutoApplySessionResponse` with updated session state.
        """
        request = SetAutoApplyAnswersRequest(session_id=session_id, answers=answers)
        resp = await self._client.post("/api/auto-apply/set-answers", json=request.model_dump())
        if resp.status_code != 200:
            _handle_error(resp)
        return AutoApplySessionResponse.model_validate(resp.json())

    async def end_session(self, session_id: UUID) -> bool:
        """End an auto-apply session.

        Args:
            session_id: The session ID to end.

        Returns:
            True if the session was successfully ended, False if not found.
        """
        resp = await self._client.delete(f"/api/auto-apply/sessions/{session_id}")
        if resp.status_code == 200:
            return True
        if resp.status_code == 404:
            return False
        _handle_error(resp)
        return False
