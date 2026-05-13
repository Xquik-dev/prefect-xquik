from __future__ import annotations

from typing import Any

from prefect import task

from prefect_xquik.client import QueryType
from prefect_xquik.credentials import XquikCredentials


@task
async def search_tweets(
    credentials: XquikCredentials,
    query: str,
    *,
    cursor: str | None = None,
    limit: int | None = None,
    query_type: QueryType = "Latest",
    since_time: str | None = None,
    until_time: str | None = None,
) -> dict[str, Any]:
    """Search public tweets."""

    client = credentials.get_client()
    return await client.search_tweets(
        query,
        cursor=cursor,
        limit=limit,
        query_type=query_type,
        since_time=since_time,
        until_time=until_time,
    )


@task
async def get_tweet(
    credentials: XquikCredentials,
    tweet_id: str,
) -> dict[str, Any]:
    """Look up a tweet by ID."""

    client = credentials.get_client()
    return await client.get_tweet(tweet_id)


@task
async def search_users(
    credentials: XquikCredentials,
    query: str,
    *,
    cursor: str | None = None,
) -> dict[str, Any]:
    """Search public users."""

    client = credentials.get_client()
    return await client.search_users(query, cursor=cursor)


@task
async def get_user(
    credentials: XquikCredentials,
    user_id: str,
) -> dict[str, Any]:
    """Look up a user by username or user ID."""

    client = credentials.get_client()
    return await client.get_user(user_id)


@task
async def get_user_tweets(
    credentials: XquikCredentials,
    user_id: str,
    *,
    cursor: str | None = None,
    include_parent_tweet: bool = False,
    include_replies: bool = False,
) -> dict[str, Any]:
    """Fetch tweets for a user."""

    client = credentials.get_client()
    return await client.get_user_tweets(
        user_id,
        cursor=cursor,
        include_parent_tweet=include_parent_tweet,
        include_replies=include_replies,
    )


@task
async def get_trends(
    credentials: XquikCredentials,
    *,
    count: int = 30,
    woeid: int = 1,
) -> dict[str, Any]:
    """Fetch trending topics."""

    client = credentials.get_client()
    return await client.get_trends(count=count, woeid=woeid)
