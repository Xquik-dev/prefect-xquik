# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections.abc import Awaitable

from prefect import flow

from prefect_xquik import XquikCredentials, get_trends, search_tweets


@flow()
async def twitter_signal_flow() -> dict[str, object]:
    loading: Awaitable[XquikCredentials] = XquikCredentials.aload("xquik")
    credentials = await loading

    searching: Awaitable[object] = search_tweets(
        credentials,
        query='"prefect" OR "workflow orchestration"',
        query_type="Latest",
        limit=25,
    )
    tweets = await searching
    trending: Awaitable[object] = get_trends(credentials, woeid=1, count=10)
    trends = await trending

    return {"tweets": tweets, "trends": trends}
