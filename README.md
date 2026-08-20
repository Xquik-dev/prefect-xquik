# Schedule Twitter search, timelines & X API workflows with Prefect

[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/13728/badge)](https://www.bestpractices.dev/projects/13728)

Run Twitter search, profile, timeline, and trend tasks in Prefect 3 flows. Store
X API keys in Prefect blocks and use native async tasks and retries.

## Pick a task

| Workflow step | Prefect task | Xquik endpoint |
| --- | --- | --- |
| Search tweets | `search_tweets` | `GET /x/tweets/search` |
| Read one tweet | `get_tweet` | `GET /x/tweets/{id}` |
| Search X profiles | `search_users` | `GET /x/users/search` |
| Read one profile | `get_user` | `GET /x/users/{id}` |
| Read a profile timeline | `get_user_tweets` | `GET /x/users/{id}/tweets` |
| Track regional trends | `get_trends` | `GET /x/trends` |

The package includes 6 read-only tasks for social media data pipelines. Use the
[REST API](https://docs.xquik.com/api-reference/overview) for follower exports or publishing.

## Install

```bash
pip install prefect-xquik
```

## Store X API credentials

```bash
prefect block register -m prefect_xquik
```

Create a Prefect block in the UI or with Python:

```python
from prefect_xquik import XquikCredentials

credentials = XquikCredentials(api_key="your_xquik_api_key_here")
credentials.save("xquik", overwrite=True)
```

Keep API keys in Prefect blocks. Never put them in flow source files.

## Create a flow

```python
from prefect import flow
from prefect_xquik import XquikCredentials, get_trends, search_tweets


@flow
async def twitter_signal_flow() -> dict:
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

## Import tasks

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

Tasks return each raw Xquik JSON response as a Python dictionary. Set Prefect
runtime options with `with_options`:

```python
from prefect_xquik import search_tweets

search_recent_tweets = search_tweets.with_options(
    name="Search recent tweets",
    retries=2,
    retry_delay_seconds=10,
)
```

## API contract

The credentials block sends `x-api-key` and `xquik-api-contract: 2026-04-29` headers.

## Documentation

- [Xquik Prefect guide](https://docs.xquik.com/guides/prefect)
- [Xquik API reference](https://docs.xquik.com/api-reference/overview)
- [Prefect integrations guide](https://docs.prefect.io/integrations/integrations)
- [Prefect workflows and tasks](https://docs.prefect.io/v3/how-to-guides/workflows/write-and-run)
- [Organization support policy](https://github.com/Xquik-dev/.github/blob/main/SUPPORT.md)
- [Security policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)

## Develop locally

```bash
uv sync
uv run ruff format --check .
uv run ruff check .
uv run pip-audit
uv run pytest
./scripts/build_reproducibly.sh
uv run twine check dist/*
```

`uv run pytest` requires 100% statement, branch, function, and line coverage.
CI also checks REUSE 3.3 licensing, dependencies, and byte-for-byte builds.

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.
