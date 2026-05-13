# Prefect tasks for Xquik X/Twitter data workflows

<p align="center">
    <a href="https://github.com/Xquik-dev/prefect-xquik/actions/workflows/ci.yml" alt="CI status">
        <img alt="CI" src="https://img.shields.io/github/actions/workflow/status/Xquik-dev/prefect-xquik/ci.yml?branch=main&label=CI&color=0052FF&labelColor=090422" />
    </a>
    <a href="https://github.com/Xquik-dev/prefect-xquik/releases" alt="GitHub release">
        <img alt="GitHub Release" src="https://img.shields.io/github/v/release/Xquik-dev/prefect-xquik?color=0052FF&labelColor=090422" />
    </a>
    <a href="https://github.com/Xquik-dev/prefect-xquik/blob/main/LICENSE" alt="Apache-2.0 license">
        <img alt="License" src="https://img.shields.io/github/license/Xquik-dev/prefect-xquik?color=0052FF&labelColor=090422" />
    </a>
    <a href="https://docs.xquik.com/guides/prefect" alt="Xquik Prefect guide">
        <img alt="Docs" src="https://img.shields.io/badge/docs-Prefect_guide-0052FF?labelColor=090422" />
    </a>
    <a href="https://docs.prefect.io/" alt="Prefect 3 documentation">
        <img alt="Prefect 3" src="https://img.shields.io/badge/Prefect-3.x-0052FF?labelColor=090422" />
    </a>
</p>

<p align="center">
    <a href="https://docs.xquik.com/guides/prefect">Prefect Guide</a>
    ·
    <a href="https://github.com/Xquik-dev/prefect-xquik/releases">Releases</a>
    ·
    <a href="https://docs.xquik.com/api-reference/overview">Xquik API Reference</a>
    ·
    <a href="https://docs.prefect.io/">Prefect Docs</a>
</p>

<p align="center">
    <strong>Guide:</strong>
    <a href="https://docs.xquik.com/guides/prefect">https://docs.xquik.com/guides/prefect</a>
</p>

Run scheduled X/Twitter data reads in Prefect 3 flows with a reusable
`XquikCredentials` block, async tasks, retries, and normal Prefect deployment
patterns.

Use `prefect-xquik` when a workflow needs public X/Twitter signals for research,
monitoring, enrichment, dashboards, or alerts without maintaining scraper code in
each flow.

## What You Can Schedule

| Workflow Need | Prefect Task | Xquik Endpoint |
| --- | --- | --- |
| Search recent or top posts | `search_tweets` | `GET /x/tweets/search` |
| Look up a specific post | `get_tweet` | `GET /x/tweets/{id}` |
| Search public users | `search_users` | `GET /x/users/search` |
| Look up a user profile | `get_user` | `GET /x/users/{id}` |
| Fetch a user's timeline | `get_user_tweets` | `GET /x/users/{id}/tweets` |
| Read regional or global trends | `get_trends` | `GET /x/trends` |

## Install

PyPI publication is pending. Use the pinned GitHub release artifact for now:

```bash
pip install https://github.com/Xquik-dev/prefect-xquik/releases/download/v0.1.4/prefect_xquik-0.1.4-py3-none-any.whl
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

## Task Imports

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

The credentials block sends `x-api-key` and the current `xquik-api-contract`
header. The default contract is `2026-04-29`, matching the public OpenAPI
contract used to build this collection.

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
uv run pytest
uv build
uv run twine check dist/*
```

This repository follows Prefect's external collection layout so it can be moved
under `src/integrations/prefect-xquik` later if Prefect maintainers request it.
