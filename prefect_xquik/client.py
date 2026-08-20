# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from typing import Any, Literal
from urllib.parse import quote, urlparse

import httpx

from prefect_xquik._version import __version__

DEFAULT_API_CONTRACT = "2026-04-29"
DEFAULT_BASE_URL = "https://xquik.com/api/v1"
USER_AGENT = f"prefect-xquik/{__version__}"

QueryType = Literal["Latest", "Top"]


class XquikError(RuntimeError):
    """A failed Xquik API request."""

    def __init__(
        self,
        message: str,
        *,
        response_text: str | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.response_text = response_text
        self.status_code = status_code


class XquikClient:
    """Call Xquik Twitter search, profile, timeline, and trend endpoints."""

    def __init__(
        self,
        api_key: str,
        *,
        api_contract: str = DEFAULT_API_CONTRACT,
        base_url: str = DEFAULT_BASE_URL,
        http_client: httpx.AsyncClient | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key is empty. Add an Xquik API key.")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds is invalid. Enter a positive number.")

        self.api_key = _require_text(api_key, "api_key")
        self.api_contract = _require_text(api_contract, "api_contract")
        self.base_url = _normalize_base_url(base_url)
        self.http_client = http_client
        self.timeout = httpx.Timeout(timeout_seconds)

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
            "x-api-key": self.api_key,
            "xquik-api-contract": self.api_contract,
        }

    async def search_tweets(
        self,
        q: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        query_type: QueryType = "Latest",
        since_time: str | None = None,
        until_time: str | None = None,
    ) -> dict[str, Any]:
        query = _require_text(q, "q")
        if query_type not in {"Latest", "Top"}:
            raise ValueError('query_type is invalid. Use "Latest" or "Top".')
        if limit is not None and not 1 <= limit <= 200:
            raise ValueError("limit is invalid. Enter a value from 1 to 200.")

        return await self._get_json(
            "/x/tweets/search",
            params={
                "q": query,
                "cursor": cursor,
                "limit": limit,
                "queryType": query_type,
                "sinceTime": since_time,
                "untilTime": until_time,
            },
        )

    async def get_tweet(self, tweet_id: str) -> dict[str, Any]:
        quoted_id = _quote_path_part(tweet_id, "tweet_id")
        return await self._get_json(f"/x/tweets/{quoted_id}")

    async def search_users(
        self, q: str, *, cursor: str | None = None
    ) -> dict[str, Any]:
        return await self._get_json(
            "/x/users/search",
            params={"q": _require_text(q, "q"), "cursor": cursor},
        )

    async def get_user(self, user_id: str) -> dict[str, Any]:
        quoted_id = _quote_path_part(_strip_at_prefix(user_id), "user_id")
        return await self._get_json(f"/x/users/{quoted_id}")

    async def get_user_tweets(
        self,
        user_id: str,
        *,
        cursor: str | None = None,
        include_parent_tweet: bool = False,
        include_replies: bool = False,
    ) -> dict[str, Any]:
        quoted_id = _quote_path_part(_strip_at_prefix(user_id), "user_id")
        return await self._get_json(
            f"/x/users/{quoted_id}/tweets",
            params={
                "cursor": cursor,
                "includeParentTweet": include_parent_tweet,
                "includeReplies": include_replies,
            },
        )

    async def get_trends(self, *, count: int = 30, woeid: int = 1) -> dict[str, Any]:
        if count < 1 or count > 50:
            raise ValueError("count is invalid. Enter a value from 1 to 50.")
        if woeid < 1:
            raise ValueError("woeid is invalid. Enter a positive location ID.")

        return await self._get_json(
            "/x/trends", params={"count": count, "woeid": woeid}
        )

    async def _get_json(
        self, path: str, *, params: dict[str, object | None] | None = None
    ) -> dict[str, Any]:
        if self.http_client is not None:
            return await self._send_get(self.http_client, path, params=params)

        async with httpx.AsyncClient(
            base_url=self.base_url, timeout=self.timeout
        ) as client:
            return await self._send_get(client, path, params=params)

    async def _send_get(
        self,
        client: httpx.AsyncClient,
        path: str,
        *,
        params: dict[str, object | None] | None,
    ) -> dict[str, Any]:
        try:
            response = await client.get(
                path,
                headers=self.headers,
                params=_clean_params(params or {}),
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise XquikError(
                f"Xquik API request failed (HTTP {exc.response.status_code}). "
                "Inspect response_text.",
                response_text=exc.response.text,
                status_code=exc.response.status_code,
            ) from exc
        except httpx.RequestError as exc:
            raise XquikError(f"Xquik API request failed: {exc}") from exc

        try:
            payload = response.json()
        except json.JSONDecodeError as exc:
            raise XquikError(
                "Xquik returned invalid JSON. Retry or inspect response_text.",
                response_text=response.text,
                status_code=response.status_code,
            ) from exc

        if not isinstance(payload, dict):
            raise XquikError(
                "Xquik returned an unexpected JSON value. Inspect response_text.",
                response_text=response.text,
                status_code=response.status_code,
            )

        return payload


def _clean_params(params: dict[str, object | None]) -> dict[str, str]:
    return {
        key: str(value).lower() if isinstance(value, bool) else str(value)
        for key, value in params.items()
        if value is not None
    }


def _quote_path_part(value: str, name: str) -> str:
    return quote(_require_text(value, name), safe="")


def _require_text(value: str, name: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{name} is empty. Enter a value.")
    return stripped


def _normalize_base_url(value: str) -> str:
    stripped = _require_text(value, "base_url").rstrip("/")
    parsed = urlparse(stripped)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("base_url is invalid. Enter a complete HTTP or HTTPS URL.")
    return stripped


def _strip_at_prefix(user_id: str) -> str:
    return user_id.removeprefix("@")
