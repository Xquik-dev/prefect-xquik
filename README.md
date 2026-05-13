# prefect-xquik

Prefect collection for Xquik read workflows.

Use this collection to run X/Twitter data jobs from Prefect flows with a
reusable credentials block. It wraps the Xquik REST API endpoints that are most
useful for scheduled research, social monitoring, and enrichment workflows:

- Search tweets
- Look up a tweet
- Search users
- Look up a user
- Fetch a user's tweets
- Fetch trends

## Install

PyPI publication is pending. Use the pinned GitHub release artifact for now:

```bash
pip install https://github.com/Xquik-dev/prefect-xquik/releases/download/v0.1.1/prefect_xquik-0.1.1-py3-none-any.whl
```

For local development:

```bash
uv sync
uv run pytest
```

## Register Blocks

```bash
prefect block register -m prefect_xquik
```

Create a block in the Prefect UI or with Python:

```python
from prefect_xquik import XquikCredentials

credentials = XquikCredentials(api_key="<xquik-api-key>")
credentials.save("xquik", overwrite=True)
```

## Example Flow

```python
from prefect import flow
from prefect_xquik import XquikCredentials, get_trends, search_tweets


@flow
async def social_signal_flow() -> dict:
    credentials = XquikCredentials.load("xquik")

    tweets = await search_tweets(
        credentials,
        query='"prefect" OR "workflow orchestration"',
        query_type="Latest",
        limit=25,
    )
    trends = await get_trends(credentials, woeid=1, count=10)

    return {"tweets": tweets, "trends": trends}
```

## Tasks

```python
from prefect_xquik import (
    get_trends,
    get_tweet,
    get_user,
    get_user_tweets,
    search_tweets,
    search_users,
)
```

All tasks accept an `XquikCredentials` block as the first argument.

## API Contract

The credentials block sends `x-api-key` and the current `xquik-api-contract`
header. The default contract is `2026-04-29`, matching the public OpenAPI
contract used to build this collection.

## Development

```bash
uv sync
uv run ruff format .
uv run ruff check .
uv run pytest
```

This repository follows Prefect's external collection layout so it can be moved
under `src/integrations/prefect-xquik` later if Prefect maintainers request it.
