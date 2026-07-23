# Schedule Tweet Search, Timelines & X Data Workflows with Prefect

[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/13728/badge)](https://www.bestpractices.dev/projects/13728)

Run Xquik reads in Prefect 3 flows. Use reusable credentials, async tasks, and Prefect retries.

## Available Tasks

| Customer question | Prefect task | Xquik endpoint |
| --- | --- | --- |
| How can I schedule tweet searches? | `search_tweets` | `GET /x/tweets/search` |
| How can I retrieve one post? | `get_tweet` | `GET /x/tweets/{id}` |
| How can I search public users? | `search_users` | `GET /x/users/search` |
| How can I enrich records with profiles? | `get_user` | `GET /x/users/{id}` |
| How can I snapshot a profile timeline? | `get_user_tweets` | `GET /x/users/{id}/tweets` |
| How can I watch regional trends? | `get_trends` | `GET /x/trends` |

This package exposes 6 read-only tasks.
Use the [REST API](https://docs.xquik.com/api-reference/overview) for follower exports or writes.

## Install

```bash
pip install prefect-xquik
```

## Register Blocks

```bash
prefect block register -m prefect_xquik
```

Create a block in the Prefect UI or with Python:

```python
from prefect_xquik import XquikCredentials

credentials = XquikCredentials(api_key="your_xquik_api_key_here")
credentials.save("xquik", overwrite=True)
```

Store API keys in Prefect blocks, not in flow source files.

## Create a Flow

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

## Import Tasks

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

The credentials block sends `x-api-key` and `xquik-api-contract: 2026-04-29`.

## Documentation

- [Xquik Prefect guide](https://docs.xquik.com/guides/prefect)
- [Xquik API reference](https://docs.xquik.com/api-reference/overview)
- [Prefect integrations guide](https://docs.prefect.io/integrations/integrations)
- [Prefect workflows and tasks](https://docs.prefect.io/v3/how-to-guides/workflows/write-and-run)

## Development

```bash
uv sync
uv run ruff format --check .
uv run ruff check .
uv run pip-audit
uv run pytest
./scripts/build_reproducibly.sh
uv run twine check dist/*
```

`uv run pytest` enforces 100% statement, branch, function, and line coverage.
CI also verifies REUSE 3.3 licensing and dependency audits.
CI builds every distribution twice and compares each byte.

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.
