# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any

import pytest

from prefect_xquik import (
    XquikCredentials,
    get_trends,
    get_tweet,
    get_user,
    get_user_tweets,
    search_tweets,
    search_users,
)


class FakeXquikClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    async def search_tweets(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("search_tweets", args, kwargs))
        return {"tweets": []}

    async def get_tweet(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("get_tweet", args, kwargs))
        return {"tweet": {"id": args[0]}}

    async def search_users(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("search_users", args, kwargs))
        return {"users": []}

    async def get_user(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("get_user", args, kwargs))
        return {"user": {"id": args[0]}}

    async def get_user_tweets(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("get_user_tweets", args, kwargs))
        return {"tweets": []}

    async def get_trends(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("get_trends", args, kwargs))
        return {"trends": []}


@pytest.fixture
def credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[XquikCredentials, FakeXquikClient]:
    fake_client = FakeXquikClient()
    monkeypatch.setattr(XquikCredentials, "get_client", lambda self: fake_client)
    return XquikCredentials(api_key="secret-key"), fake_client


@pytest.mark.asyncio
async def test_search_tweets_task(
    credentials: tuple[XquikCredentials, FakeXquikClient],
) -> None:
    block, fake_client = credentials

    result = await search_tweets.fn(
        block,
        "prefect",
        limit=10,
        query_type="Top",
    )

    assert result == {"tweets": []}
    assert fake_client.calls == [
        (
            "search_tweets",
            ("prefect",),
            {
                "cursor": None,
                "limit": 10,
                "query_type": "Top",
                "since_time": None,
                "until_time": None,
            },
        )
    ]


@pytest.mark.asyncio
async def test_lookup_tasks(
    credentials: tuple[XquikCredentials, FakeXquikClient],
) -> None:
    block, fake_client = credentials

    tweet = await get_tweet.fn(block, "123")
    users = await search_users.fn(block, "prefect")
    user = await get_user.fn(block, "@prefect")

    assert tweet == {"tweet": {"id": "123"}}
    assert users == {"users": []}
    assert user == {"user": {"id": "@prefect"}}
    assert fake_client.calls == [
        ("get_tweet", ("123",), {}),
        ("search_users", ("prefect",), {"cursor": None}),
        ("get_user", ("@prefect",), {}),
    ]


@pytest.mark.asyncio
async def test_user_tweets_and_trends_tasks(
    credentials: tuple[XquikCredentials, FakeXquikClient],
) -> None:
    block, fake_client = credentials

    tweets = await get_user_tweets.fn(
        block,
        "@prefect",
        include_parent_tweet=True,
        include_replies=True,
    )
    trends = await get_trends.fn(block, count=5, woeid=1)

    assert tweets == {"tweets": []}
    assert trends == {"trends": []}
    assert fake_client.calls == [
        (
            "get_user_tweets",
            ("@prefect",),
            {
                "cursor": None,
                "include_parent_tweet": True,
                "include_replies": True,
            },
        ),
        ("get_trends", (), {"count": 5, "woeid": 1}),
    ]
