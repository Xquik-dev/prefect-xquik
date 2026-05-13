from __future__ import annotations

from prefect import flow

from prefect_xquik import XquikCredentials, get_trends, search_tweets


@flow
async def social_signal_flow() -> dict[str, object]:
    credentials = XquikCredentials.load("xquik")

    tweets = await search_tweets(
        credentials,
        query='"prefect" OR "workflow orchestration"',
        query_type="Latest",
        limit=25,
    )
    trends = await get_trends(credentials, woeid=1, count=10)

    return {"tweets": tweets, "trends": trends}
