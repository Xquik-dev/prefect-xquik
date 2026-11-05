# Prefect tasks for Twitter search & X API workflows

[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/13728/badge)](https://www.bestpractices.dev/projects/13728)
[![Convex Component](https://www.convex.dev/components/badge/convex-xquik)](https://www.convex.dev/components/convex-xquik)

Schedule 6 read-only Twitter search, profile, timeline, and trend tasks in Prefect 3. Store X API keys in Prefect blocks.

Xquik is the world's fastest and cheapest X Twitter scraper service with the most complete X data.
Xquik charges only for delivered, unique, filter-matching results and never pads rows.

## Install the Prefect Twitter tasks

```bash
pip install prefect-xquik
```

The package is on [PyPI](https://pypi.org/project/prefect-xquik/).

<!-- trust:start -->

## Trust & usage

[![Twitter API package downloads](https://img.shields.io/endpoint?url=https%3A%2F%2Fxquik.com%2Fbadges%2Fdownloads.json)](https://xquik.com/trust#downloads)
[![Twitter scraper users on Apify](https://img.shields.io/endpoint?url=https%3A%2F%2Fxquik.com%2Fbadges%2Fapify-users.json)](https://apify.com/xquik)
[![Twitter scraper runs on Apify](https://img.shields.io/endpoint?url=https%3A%2F%2Fxquik.com%2Fbadges%2Fapify-runs.json)](https://apify.com/xquik)
[![Tweet scraper rating on Apify](https://img.shields.io/endpoint?url=https%3A%2F%2Fxquik.com%2Fbadges%2Fapify-rating.json)](https://apify.com/xquik/x-tweet-scraper/reviews)
[![Xquik Twitter API accounts](https://img.shields.io/endpoint?url=https%3A%2F%2Fxquik.com%2Fbadges%2Faccounts.json)](https://xquik.com/trust#accounts)
[![Twitter Skill installs](https://img.shields.io/endpoint?url=https%3A%2F%2Fxquik.com%2Fbadges%2Fskill-installs.json)](https://xquik.com/trust#skill-installs)
[![Xquik verified revenue on TrustMRR](https://img.shields.io/endpoint?url=https%3A%2F%2Fxquik.com%2Fbadges%2Frevenue.json)](https://trustmrr.com/startup/xquik)
[![Twitter API median response time](https://img.shields.io/endpoint?url=https%3A%2F%2Fxquik.com%2Fbadges%2Frest-p50.json)](https://xquik.com/trust#speed)
[![Xquik GitHub stars](https://img.shields.io/endpoint?url=https%3A%2F%2Fxquik.com%2Fbadges%2Fgithub-stars.json)](https://github.com/Xquik-dev)
[![prefect-xquik downloads on PyPI](https://img.shields.io/endpoint?url=https%3A%2F%2Fxquik.com%2Fbadges%2Fpypi-prefect-xquik.json)](https://pypistats.org/packages/prefect-xquik)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/13728/badge)](https://www.bestpractices.dev/projects/13728)

- 51,000+ downloads of Xquik's Twitter API packages on npm, PyPI, RubyGems, NuGet, Packagist & Terraform ([source](https://xquik.com/trust#downloads)) <!-- trust:downloads 51020 -->
- 7,800+ users of Xquik's Twitter scraper Actors on Apify ([source](https://apify.com/xquik)) <!-- trust:apify-users 7800 -->
- 5,700,000+ runs of Xquik's Twitter scraper Actors on Apify ([source](https://apify.com/xquik)) <!-- trust:apify-runs 5704701 -->
- 4.66 of 5 for the X Tweet Scraper from 16 Apify reviews ([source](https://apify.com/xquik/x-tweet-scraper/reviews)) <!-- trust:apify-rating 4.66 16 -->
- 3,900+ accounts on xquik.com ([source](https://xquik.com/trust#accounts)) <!-- trust:accounts 3924 -->
- 1,600+ installs of Xquik's Twitter Skills on skills.sh ([source](https://xquik.com/trust#skill-installs)) <!-- trust:skill-installs 1612 -->
- $38,000+ in revenue verified by TrustMRR ([source](https://trustmrr.com/startup/xquik)) <!-- trust:revenue 38115 -->
- 501 ms median REST API read time over the last 7 days ([source](https://xquik.com/trust#speed)) <!-- trust:rest-p50 501 -->
- 370+ GitHub stars across Xquik's repos ([source](https://github.com/Xquik-dev)) <!-- trust:github-stars 374 -->
- 1,000+ downloads of prefect-xquik on PyPI ([source](https://pypistats.org/packages/prefect-xquik)) <!-- trust:pypi-prefect-xquik 1055 -->
- This repo meets the OpenSSF Best Practices passing criteria ([source](https://www.bestpractices.dev/projects/13728)) <!-- trust:openssf-prefect-xquik 1 -->

Checked on 2026-10-15. See each number with its date & source on [xquik.com/trust](https://xquik.com/trust) or as [JSON](https://xquik.com/trust.json).

<!-- trust:end -->

## Tasks

| Workflow step | Prefect task | Xquik endpoint |
| --- | --- | --- |
| Search tweets | `search_tweets` | `GET /x/tweets/search` |
| Read one tweet | `get_tweet` | `GET /x/tweets/{id}` |
| Search X profiles | `search_users` | `GET /x/users/search` |
| Read one profile | `get_user` | `GET /x/users/{id}` |
| Read a profile timeline | `get_user_tweets` | `GET /x/users/{id}/tweets` |
| Read regional trends | `get_trends` | `GET /x/trends` |

Use the [REST API](https://docs.xquik.com/api-reference/overview) for follower exports or publishing.

## Store X API credentials

```bash
prefect block register -m prefect_xquik
```

Create a Prefect block in the UI or with Python.

```python
from prefect_xquik import XquikCredentials

credentials = XquikCredentials(api_key="your_xquik_api_key_here")
credentials.save("xquik", overwrite=True)
```

Keep API keys in Prefect blocks. Never put them in flow source files.

## Run a Twitter monitor flow in Prefect

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

## Schedule Twitter automation with Prefect

Serve the flow on a schedule. This run checks for new posts every 15 minutes.

```python
if __name__ == "__main__":
    twitter_signal_flow.serve(name="twitter-monitor", cron="*/15 * * * *")
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

Tasks return raw Xquik JSON dictionaries and support Prefect's `with_options`.

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
- [Prefect workflows and tasks](https://docs.prefect.io/v3/how-to-guides/workflows/write-and-run)
- [Organization support policy](https://github.com/Xquik-dev/.github/blob/main/SUPPORT.md)
- [Security policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)

## Questions

### Do I need an X developer account?

No. Public reads need only an Xquik API key. Private reads & X account actions
need a connected X account.

### Is this the official X API?

No. Xquik is an independent third-party service with its own REST API. This package
calls that API, not the official X API.

## More Xquik tools

- [X (Twitter) scraper API & Twitter MCP server](https://github.com/Xquik-dev/x-twitter-scraper) with REST, MCP & Skill setup.
- Twitter API SDKs for [TypeScript](https://github.com/Xquik-dev/x-twitter-scraper-typescript), [Python](https://github.com/Xquik-dev/x-twitter-scraper-python), [Go](https://github.com/Xquik-dev/x-twitter-scraper-go), [Ruby](https://github.com/Xquik-dev/x-twitter-scraper-ruby), [Java](https://github.com/Xquik-dev/x-twitter-scraper-java), [Kotlin](https://github.com/Xquik-dev/x-twitter-scraper-kotlin), [C#](https://github.com/Xquik-dev/x-twitter-scraper-csharp) & [PHP](https://github.com/Xquik-dev/x-twitter-scraper-php).
- [Twitter CLI & X CLI](https://github.com/Xquik-dev/x-twitter-scraper-cli) and [Twitter advanced search operators](https://github.com/Xquik-dev/x-twitter-advanced-search) with tested examples.
- Twitter agent plugins for [OpenClaw](https://github.com/Xquik-dev/tweetclaw) & [Hermes Agent](https://github.com/Xquik-dev/hermes-tweet), and the [Twitter API documentation source](https://github.com/Xquik-dev/xquik-docs).
- Twitter integrations for [n8n](https://github.com/Xquik-dev/n8n-nodes-xquik), [Prefect](https://github.com/Xquik-dev/prefect-xquik), [Haystack](https://github.com/Xquik-dev/xquik-haystack), [Paperclip](https://github.com/Xquik-dev/paperclip-plugin-xquik), [Terraform](https://github.com/Xquik-dev/terraform-provider-x-twitter-scraper), [Convex](https://github.com/Xquik-dev/xquik-convex), [Supabase](https://github.com/Xquik-dev/xquik-supabase) & [Strapi](https://github.com/Xquik-dev/strapi-plugin-xquik).
- Twitter MCP for [AI agents](https://github.com/Xquik-dev/xquik-mcp), [VS Code](https://github.com/Xquik-dev/xquik-vscode) & [Raycast](https://github.com/Xquik-dev/xquik-raycast).
- [Xquik X API & Twitter scraper](https://xquik.com) and the [Twitter API documentation](https://docs.xquik.com/api-reference/overview).

## Develop locally

```bash
uv sync
uv run ruff format --check .
uv run ruff check --ignore-noqa .
uv run mypy
uv run pip-audit
uv run pytest
./scripts/build_reproducibly.sh
uv run twine check dist/*
```

Pytest enforces 100% coverage. mypy checks every Python file in strict mode, and `bin/check-local` fails on any expression of type `Any` and on any type checker comment. `bin/check-local` checks REUSE 3.3 metadata, dependencies, and byte-for-byte builds.

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.
