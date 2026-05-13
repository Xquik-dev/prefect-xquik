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

Full setup guide: https://docs.xquik.com/guides/prefect

## Install

PyPI publication is pending. Use the pinned GitHub release artifact for now:

```bash
pip install https://github.com/Xquik-dev/prefect-xquik/releases/download/v0.1.3/prefect_xquik-0.1.3-py3-none-any.whl
```

For local development:

```bash
uv sync
uv run ruff format --check .
uv run ruff check .
uv run pytest
uv build
uv run twine check dist/*
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

Store API keys in Prefect blocks, not in flow source files.

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

| Task | Xquik Endpoint |
| --- | --- |
| `search_tweets` | `GET /x/tweets/search` |
| `get_tweet` | `GET /x/tweets/{id}` |
| `search_users` | `GET /x/users/search` |
| `get_user` | `GET /x/users/{id}` |
| `get_user_tweets` | `GET /x/users/{id}/tweets` |
| `get_trends` | `GET /x/trends` |

Tasks return the raw Xquik JSON response as a Python dictionary. Configure
Prefect runtime behavior with `with_options`:

```python
from prefect_xquik import search_tweets

search_recent_tweets = search_tweets.with_options(
    name="Search Recent X Posts",
    retries=2,
    retry_delay_seconds=10,
)
```

## API Contract

The credentials block sends `x-api-key` and the current `xquik-api-contract`
header. The default contract is `2026-04-29`, matching the public OpenAPI
contract used to build this collection.

## Development

```bash
uv sync
uv run ruff format --check .
uv run ruff check .
uv run pytest
uv build
uv run twine check dist/*
```

This repository follows Prefect's external collection layout so it can be moved
under `src/integrations/prefect-xquik` later if Prefect maintainers request it.
