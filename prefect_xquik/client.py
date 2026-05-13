from __future__ import annotations

from typing import Any, Literal
from urllib.parse import quote

import httpx

DEFAULT_API_CONTRACT = "2026-04-29"
DEFAULT_BASE_URL = "https://api.xquik.com"
USER_AGENT = "prefect-xquik/0.1.0"

QueryType = Literal["Latest", "Top"]


class XquikError(RuntimeError):
    """Raised when an Xquik request fails."""

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
    """Async client for selected Xquik REST API endpoints."""

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
            raise ValueError("api_key must not be empty")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than 0")

        self.api_key = api_key
        self.api_contract = api_contract
        self.base_url = base_url.rstrip("/")
        self.http_client = http_client
        self.timeout = httpx.Timeout(timeout_seconds)

    @property
    def headers(self) -> dict[str, str]:
        return {
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
            raise ValueError('query_type must be "Latest" or "Top"')
        if limit is not None and not 1 <= limit <= 200:
            raise ValueError("limit must be between 1 and 200")

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
            raise ValueError("count must be between 1 and 50")
        if woeid < 1:
            raise ValueError("woeid must be greater than 0")

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
                f"Xquik request failed with status {exc.response.status_code}",
                response_text=exc.response.text,
                status_code=exc.response.status_code,
            ) from exc
        except httpx.RequestError as exc:
            raise XquikError(f"Xquik request failed: {exc}") from exc

        return response.json()


def _clean_params(params: dict[str, object | None]) -> dict[str, str]:
    cleaned: dict[str, str] = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, bool):
            cleaned[key] = "true" if value else "false"
        else:
            cleaned[key] = str(value)
    return cleaned


def _quote_path_part(value: str, name: str) -> str:
    return quote(_require_text(value, name), safe="")


def _require_text(value: str, name: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{name} must not be empty")
    return stripped


def _strip_at_prefix(user_id: str) -> str:
    return user_id.removeprefix("@")
