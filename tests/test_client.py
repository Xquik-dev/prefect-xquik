# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any

import httpx
import pytest

from prefect_xquik import XquikClient, XquikError, __version__
from prefect_xquik.client import DEFAULT_BASE_URL


def test_default_base_url_matches_public_rest_api() -> None:
    client = XquikClient("secret-key")

    assert DEFAULT_BASE_URL == "https://xquik.com/api/v1"
    assert client.base_url == DEFAULT_BASE_URL


@pytest.mark.parametrize(
    ("api_key", "timeout_seconds", "error"),
    [
        (" ", 30, "api_key must not be empty"),
        ("secret-key", 0, "timeout_seconds must be greater than 0"),
    ],
)
def test_client_rejects_invalid_constructor_values(
    api_key: str, timeout_seconds: float, error: str
) -> None:
    with pytest.raises(ValueError, match=error):
        XquikClient(api_key, timeout_seconds=timeout_seconds)


@pytest.mark.asyncio
async def test_search_tweets_sends_expected_headers_and_params() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"tweets": []})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        base_url="https://api.xquik.test", transport=transport
    ) as http_client:
        client = XquikClient(
            "secret-key",
            base_url="https://api.xquik.test",
            http_client=http_client,
        )
        result = await client.search_tweets(
            "prefect",
            limit=25,
            query_type="Top",
            since_time="1710000000",
        )

    assert result == {"tweets": []}
    assert len(requests) == 1
    request = requests[0]
    assert request.headers["x-api-key"] == "secret-key"
    assert request.headers["xquik-api-contract"] == "2026-04-29"
    assert request.headers["accept"] == "application/json"
    assert request.headers["user-agent"] == f"prefect-xquik/{__version__}"
    assert request.url.path == "/x/tweets/search"
    assert request.url.params["q"] == "prefect"
    assert request.url.params["limit"] == "25"
    assert request.url.params["queryType"] == "Top"
    assert request.url.params["sinceTime"] == "1710000000"
    assert "cursor" not in request.url.params


@pytest.mark.asyncio
async def test_get_tweet_url_encodes_path_parts() -> None:
    request_url: str | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal request_url
        request_url = str(request.url)
        return httpx.Response(200, json={"tweet": {"id": "a/b"}})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        base_url="https://api.xquik.test", transport=transport
    ) as http_client:
        client = XquikClient("secret-key", http_client=http_client)
        result = await client.get_tweet("a/b")

    assert result == {"tweet": {"id": "a/b"}}
    assert request_url == "https://api.xquik.test/x/tweets/a%2Fb"


@pytest.mark.asyncio
async def test_get_user_tweets_strips_at_prefix_and_serializes_booleans() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"tweets": []})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        base_url="https://api.xquik.test", transport=transport
    ) as http_client:
        client = XquikClient("secret-key", http_client=http_client)
        result = await client.get_user_tweets(
            "@prefect",
            include_parent_tweet=True,
            include_replies=True,
        )

    assert result == {"tweets": []}
    assert len(requests) == 1
    request = requests[0]
    assert request.url.path == "/x/users/prefect/tweets"
    assert request.url.params["includeParentTweet"] == "true"
    assert request.url.params["includeReplies"] == "true"


@pytest.mark.asyncio
async def test_get_user_and_default_timeline_parameters() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        base_url="https://api.xquik.test", transport=transport
    ) as http_client:
        client = XquikClient("secret-key", http_client=http_client)
        user = await client.get_user("prefect")
        tweets = await client.get_user_tweets("prefect")

    assert user == {}
    assert tweets == {}
    assert [request.url.path for request in requests] == [
        "/x/users/prefect",
        "/x/users/prefect/tweets",
    ]
    assert requests[1].url.params["includeParentTweet"] == "false"
    assert requests[1].url.params["includeReplies"] == "false"


@pytest.mark.parametrize("count", [0, 51])
@pytest.mark.asyncio
async def test_get_trends_validates_count(count: int) -> None:
    client = XquikClient("secret-key")

    with pytest.raises(ValueError, match="count must be between 1 and 50"):
        await client.get_trends(count=count)


@pytest.mark.asyncio
async def test_get_trends_validates_woeid() -> None:
    client = XquikClient("secret-key")

    with pytest.raises(ValueError, match="woeid must be greater than 0"):
        await client.get_trends(woeid=0)


@pytest.mark.asyncio
async def test_internal_http_client_context() -> None:
    client_settings: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"trends": []}, request=request)

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient

    def client_factory(*, base_url: str, timeout: httpx.Timeout) -> httpx.AsyncClient:
        client_settings.update(base_url=base_url, timeout=timeout)
        return async_client(base_url=base_url, timeout=timeout, transport=transport)

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(httpx, "AsyncClient", client_factory)
        client = XquikClient("secret-key", base_url="https://api.xquik.test")
        result = await client.get_trends()

    assert result == {"trends": []}
    assert client_settings["base_url"] == "https://api.xquik.test"
    assert client_settings["timeout"] == httpx.Timeout(30)


@pytest.mark.asyncio
async def test_http_error_raises_xquik_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="rate limited", request=request)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        base_url="https://api.xquik.test", transport=transport
    ) as http_client:
        client = XquikClient("secret-key", http_client=http_client)

        with pytest.raises(XquikError) as exc_info:
            await client.search_users("prefect")

    assert exc_info.value.status_code == 429
    assert exc_info.value.response_text == "rate limited"


@pytest.mark.asyncio
async def test_request_error_raises_xquik_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline", request=request)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        base_url="https://api.xquik.test", transport=transport
    ) as http_client:
        client = XquikClient("secret-key", http_client=http_client)

        with pytest.raises(XquikError, match="Xquik request failed: offline"):
            await client.search_users("prefect")


@pytest.mark.asyncio
async def test_invalid_json_raises_xquik_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not json", request=request)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        base_url="https://api.xquik.test", transport=transport
    ) as http_client:
        client = XquikClient("secret-key", http_client=http_client)

        with pytest.raises(XquikError, match="not valid JSON") as exc_info:
            await client.search_users("prefect")

    assert exc_info.value.status_code == 200
    assert exc_info.value.response_text == "not json"


@pytest.mark.asyncio
async def test_non_object_json_raises_xquik_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[], request=request)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        base_url="https://api.xquik.test", transport=transport
    ) as http_client:
        client = XquikClient("secret-key", http_client=http_client)

        with pytest.raises(XquikError, match="not a JSON object") as exc_info:
            await client.search_users("prefect")

    assert exc_info.value.status_code == 200
    assert exc_info.value.response_text == "[]"


@pytest.mark.parametrize(
    ("method_name", "args", "error"),
    [
        ("search_tweets", ("",), "q must not be empty"),
        ("search_tweets", ("prefect",), 'query_type must be "Latest" or "Top"'),
        ("search_users", ("",), "q must not be empty"),
        ("get_user", ("@",), "user_id must not be empty"),
        ("get_tweet", ("",), "tweet_id must not be empty"),
    ],
)
@pytest.mark.asyncio
async def test_validation_errors(
    method_name: str, args: tuple[str, ...], error: str
) -> None:
    client = XquikClient("secret-key")
    kwargs: dict[str, Any] = {}
    if method_name == "search_tweets" and args == ("prefect",):
        kwargs["query_type"] = "Mixed"

    with pytest.raises(ValueError, match=error):
        await getattr(client, method_name)(*args, **kwargs)


@pytest.mark.parametrize("base_url", ["xquik.test", "https:///path"])
def test_client_rejects_invalid_base_url(base_url: str) -> None:
    with pytest.raises(ValueError, match="base_url must be an HTTP or HTTPS URL"):
        XquikClient("secret-key", base_url=base_url)


@pytest.mark.parametrize("limit", [0, 201])
@pytest.mark.asyncio
async def test_search_tweets_validates_limit(limit: int) -> None:
    client = XquikClient("secret-key")

    with pytest.raises(ValueError, match="limit must be between 1 and 200"):
        await client.search_tweets("prefect", limit=limit)
