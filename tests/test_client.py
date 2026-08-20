# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any

import httpx
import pytest

from prefect_xquik import XquikClient, XquikError, __version__
from prefect_xquik.client import DEFAULT_BASE_URL

Handler = Callable[[httpx.Request], httpx.Response]
LIMIT_ERROR = "limit is invalid. Enter a value from 1 to 200."
COUNT_ERROR = "count is invalid. Enter a value from 1 to 50."
WOEID_ERROR = "woeid is invalid. Enter a positive location ID."


@asynccontextmanager
async def mock_client(handler: Handler) -> AsyncIterator[XquikClient]:
    async with httpx.AsyncClient(
        base_url="https://api.xquik.test",
        transport=httpx.MockTransport(handler),
    ) as http_client:
        yield XquikClient("secret-key", http_client=http_client)


def test_client_uses_public_rest_api_by_default() -> None:
    assert DEFAULT_BASE_URL == "https://xquik.com/api/v1"
    assert XquikClient("secret-key").base_url == DEFAULT_BASE_URL


@pytest.mark.parametrize(
    ("api_key", "kwargs", "error"),
    [
        (" ", {}, "api_key is empty. Add an Xquik API key."),
        (
            "secret-key",
            {"timeout_seconds": 0},
            "timeout_seconds is invalid. Enter a positive number.",
        ),
        (
            "secret-key",
            {"base_url": "xquik.test"},
            "base_url is invalid. Enter a complete HTTP or HTTPS URL.",
        ),
        (
            "secret-key",
            {"base_url": "https:///path"},
            "base_url is invalid. Enter a complete HTTP or HTTPS URL.",
        ),
    ],
)
def test_client_explains_invalid_constructor_values(
    api_key: str,
    kwargs: dict[str, Any],
    error: str,
) -> None:
    with pytest.raises(ValueError, match=error):
        XquikClient(api_key, **kwargs)


@pytest.mark.asyncio
async def test_twitter_search_sends_contract_headers_and_query_params() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"tweets": []})

    async with mock_client(handler) as client:
        result = await client.search_tweets(
            "prefect", limit=25, query_type="Top", since_time="1710000000"
        )

    request = requests[0]
    assert result == {"tweets": []}
    assert len(requests) == 1
    assert request.headers["x-api-key"] == "secret-key"
    assert request.headers["xquik-api-contract"] == "2026-04-29"
    assert request.headers["accept"] == "application/json"
    assert request.headers["user-agent"] == f"prefect-xquik/{__version__}"
    assert request.url.path == "/x/tweets/search"
    assert dict(request.url.params) == {
        "q": "prefect",
        "limit": "25",
        "queryType": "Top",
        "sinceTime": "1710000000",
    }


@pytest.mark.asyncio
async def test_tweet_lookup_encodes_the_id_as_one_path_segment() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"tweet": {"id": "a/b"}})

    async with mock_client(handler) as client:
        result = await client.get_tweet("a/b")

    assert result == {"tweet": {"id": "a/b"}}
    assert str(requests[0].url) == "https://api.xquik.test/x/tweets/a%2Fb"


@pytest.mark.asyncio
async def test_user_routes_remove_at_prefixes_and_send_default_flags() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={})

    async with mock_client(handler) as client:
        user = await client.get_user("prefect")
        tweets = await client.get_user_tweets(
            "@prefect", include_parent_tweet=True, include_replies=True
        )
        defaults = await client.get_user_tweets("prefect")

    assert user == tweets == defaults == {}
    assert [request.url.path for request in requests] == [
        "/x/users/prefect",
        "/x/users/prefect/tweets",
        "/x/users/prefect/tweets",
    ]
    assert dict(requests[1].url.params) == {
        "includeParentTweet": "true",
        "includeReplies": "true",
    }
    assert dict(requests[2].url.params) == {
        "includeParentTweet": "false",
        "includeReplies": "false",
    }


@pytest.mark.asyncio
async def test_client_creates_an_http_session_when_none_is_supplied() -> None:
    client_settings: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"trends": []}, request=request)

    async_client = httpx.AsyncClient

    def client_factory(*, base_url: str, timeout: httpx.Timeout) -> httpx.AsyncClient:
        client_settings.update(base_url=base_url, timeout=timeout)
        return async_client(
            base_url=base_url,
            timeout=timeout,
            transport=httpx.MockTransport(handler),
        )

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(httpx, "AsyncClient", client_factory)
        result = await XquikClient(
            "secret-key", base_url="https://api.xquik.test"
        ).get_trends()

    assert result == {"trends": []}
    assert client_settings == {
        "base_url": "https://api.xquik.test",
        "timeout": httpx.Timeout(30),
    }


@pytest.mark.asyncio
async def test_http_status_error_preserves_status_and_response_text() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="rate limited", request=request)

    async with mock_client(handler) as client:
        with pytest.raises(XquikError) as exc_info:
            await client.search_users("prefect")

    assert exc_info.value.status_code == 429
    assert exc_info.value.response_text == "rate limited"


@pytest.mark.asyncio
async def test_connection_error_identifies_the_failed_xquik_request() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline", request=request)

    async with mock_client(handler) as client:
        with pytest.raises(XquikError, match="Xquik API request failed: offline"):
            await client.search_users("prefect")


@pytest.mark.parametrize(
    ("payload", "message", "response_text"),
    [("not json", "invalid JSON", "not json"), ([], "unexpected JSON", "[]")],
)
@pytest.mark.asyncio
async def test_invalid_response_explains_how_to_inspect_the_payload(
    payload: str | list[object],
    message: str,
    response_text: str,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if isinstance(payload, str):
            return httpx.Response(200, text=payload, request=request)
        return httpx.Response(200, json=payload, request=request)

    async with mock_client(handler) as client:
        with pytest.raises(XquikError, match=message) as exc_info:
            await client.search_users("prefect")

    assert exc_info.value.status_code == 200
    assert exc_info.value.response_text == response_text


@pytest.mark.parametrize(
    ("method_name", "args", "kwargs", "error"),
    [
        ("search_tweets", ("",), {}, "q is empty. Enter a value."),
        (
            "search_tweets",
            ("prefect",),
            {"query_type": "Mixed"},
            'query_type is invalid. Use "Latest" or "Top".',
        ),
        ("search_tweets", ("prefect",), {"limit": 0}, LIMIT_ERROR),
        ("search_tweets", ("prefect",), {"limit": 201}, LIMIT_ERROR),
        ("search_users", ("",), {}, "q is empty. Enter a value."),
        ("get_user", ("@",), {}, "user_id is empty. Enter a value."),
        ("get_tweet", ("",), {}, "tweet_id is empty. Enter a value."),
        ("get_trends", (), {"count": 0}, COUNT_ERROR),
        ("get_trends", (), {"count": 51}, COUNT_ERROR),
        ("get_trends", (), {"woeid": 0}, WOEID_ERROR),
    ],
)
@pytest.mark.asyncio
async def test_public_methods_return_actionable_validation_errors(
    method_name: str,
    args: tuple[str, ...],
    kwargs: dict[str, Any],
    error: str,
) -> None:
    with pytest.raises(ValueError, match=error):
        await getattr(XquikClient("secret-key"), method_name)(*args, **kwargs)
