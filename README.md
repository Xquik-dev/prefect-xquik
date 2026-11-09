# Prefect Tasks for X (Twitter) Automation, Search & API Workflows

[![Framer builds a tweet ticker with Xquik](https://img.youtube.com/vi/4UOSpoOoC3Y/maxresdefault.jpg)](https://youtu.be/4UOSpoOoC3Y?t=367)\
[Watch Framer build a tweet ticker with Xquik, from 6:07](https://youtu.be/4UOSpoOoC3Y?t=367).
These Prefect tasks call the Xquik API.

Use these Prefect tasks by Xquik for X (Twitter) automation & tweet search.
Run 6 read-only tasks in Prefect 3 with your key in a block.

Xquik is the world's fastest and cheapest X (Twitter) scraper service with the most complete X (Twitter) data.
Most other Apify Actors charge before filtering or deduplication.
Xquik charges only for delivered, unique, filter-matching results and never pads rows.
Xquik is independent and not affiliated with X Corp.

<!-- trust:win:start -->

The Xquik REST API read 45 tweets per second on 2026-10-15. That cost $0.15 per 1,000. The fastest of 4 rival Actors read 12.5 per second. The cheapest cost $0.173 per 1,000. [Compare each run](https://xquik.com/benchmarks#benchmark-x-tweet-scraper).

<!-- trust:win:end -->

## Install the Prefect X (Twitter) tasks

The package needs Python 3.11 or newer.

```bash
pip install prefect-xquik
```

## Store X (Twitter) API credentials

Copy a key from [your Xquik account](https://dashboard.xquik.com/en/account?tab=api-keys), then register the block type.

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

## Run an X (Twitter) monitor flow in Prefect

```python
from prefect import flow
from prefect_xquik import XquikCredentials, get_trends, search_tweets


@flow
async def twitter_signal_flow() -> dict:
    credentials = await XquikCredentials.aload("xquik")

    tweets = await search_tweets(
        credentials,
        query='"prefect" OR "workflow orchestration"',
        query_type="Latest",
        limit=25,
    )
    trends = await get_trends(credentials, woeid=1, count=10)

    return {"tweets": tweets, "trends": trends}
```

## Schedule X (Twitter) automation with Prefect

Serve the flow on a schedule. This run checks for new posts every 15 minutes.

```python
if __name__ == "__main__":
    twitter_signal_flow.serve(name="twitter-monitor", cron="*/15 * * * *")
```

Next, read the [Xquik Prefect guide](https://docs.xquik.com/guides/prefect), the [task table](#tasks) or the [Prefect workflow docs](https://docs.prefect.io/v3/how-to-guides/workflows/write-and-run).

<!-- trust:start -->

## Benchmarks & usage

[![prefect-xquik downloads on PyPI](https://img.shields.io/endpoint?url=https%3A%2F%2Fxquik.com%2Fbadges%2Fpypi-prefect-xquik.json)](https://pypistats.org/packages/prefect-xquik)
[![X (Twitter) API p99 server read time](https://img.shields.io/endpoint?url=https%3A%2F%2Fxquik.com%2Fbadges%2Frest-p99.json)](https://xquik.com/benchmarks#speed)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/13728/badge)](https://www.bestpractices.dev/projects/13728)

- 1,100+ downloads of prefect-xquik on PyPI ([source](https://pypistats.org/packages/prefect-xquik)) <!-- trust:pypi-prefect-xquik 1109 -->
- 5.4 s p99 REST server read time over 7 days, failures included ([source](https://xquik.com/benchmarks#speed)) <!-- trust:rest-p99 5312 -->
- This repo meets the OpenSSF Best Practices passing criteria ([source](https://www.bestpractices.dev/projects/13728)) <!-- trust:openssf-prefect-xquik 1 -->

Checked on 2026-11-08. See each number with its date & source on [xquik.com/benchmarks](https://xquik.com/benchmarks) or as [JSON](https://xquik.com/trust.json).

<!-- trust:end -->

## Tasks

| Workflow step | Prefect task | Xquik endpoint |
| --- | --- | --- |
| Search tweets | `search_tweets` | `GET /x/tweets/search` |
| Read 1 tweet | `get_tweet` | `GET /x/tweets/{id}` |
| Search X (Twitter) profiles | `search_users` | `GET /x/users/search` |
| Read 1 profile | `get_user` | `GET /x/users/{id}` |
| Read a profile timeline | `get_user_tweets` | `GET /x/users/{id}/tweets` |
| Read regional trends | `get_trends` | `GET /x/trends` |

Use the [REST API](https://docs.xquik.com/api-reference/overview) for follower exports or publishing.

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

## Questions

### Do I need an X (Twitter) developer account?

No. Public reads need only an Xquik API key.
Private reads & account actions need a connected X (Twitter) account.

### Is this the official X (Twitter) API?

No. Xquik runs its own REST API.
This package calls that API, not the official X (Twitter) API.

## More Xquik tools

- [X (Twitter) scraper API & MCP server](https://github.com/Xquik-dev/x-twitter-scraper) with REST, MCP & Skill setup.
- X (Twitter) API SDKs for [TypeScript](https://github.com/Xquik-dev/x-twitter-scraper-typescript), [Python](https://github.com/Xquik-dev/x-twitter-scraper-python), [Go](https://github.com/Xquik-dev/x-twitter-scraper-go), [Ruby](https://github.com/Xquik-dev/x-twitter-scraper-ruby), [Java](https://github.com/Xquik-dev/x-twitter-scraper-java), [Kotlin](https://github.com/Xquik-dev/x-twitter-scraper-kotlin), [C#](https://github.com/Xquik-dev/x-twitter-scraper-csharp) & [PHP](https://github.com/Xquik-dev/x-twitter-scraper-php).
- [X (Twitter) CLI](https://github.com/Xquik-dev/x-twitter-scraper-cli) for terminal workflows.
- The [X (Twitter) API alternative skill](https://github.com/Xquik-dev/x-api) & [X (Twitter) advanced search operators](https://github.com/Xquik-dev/x-twitter-advanced-search).
- X (Twitter) agent plugins for [OpenClaw](https://github.com/Xquik-dev/tweetclaw) & [Hermes Agent](https://github.com/Xquik-dev/hermes-tweet).
- The [X (Twitter) API documentation source](https://github.com/Xquik-dev/xquik-docs).
- X (Twitter) integrations for [n8n](https://github.com/Xquik-dev/n8n-nodes-xquik), [Haystack](https://github.com/Xquik-dev/xquik-haystack), [Paperclip](https://github.com/Xquik-dev/paperclip-plugin-xquik), [Terraform](https://github.com/Xquik-dev/terraform-provider-x-twitter-scraper), [Convex](https://github.com/Xquik-dev/xquik-convex), [Supabase](https://github.com/Xquik-dev/xquik-supabase) & [Strapi](https://github.com/Xquik-dev/strapi-plugin-xquik).
- X (Twitter) MCP for [AI agents](https://github.com/Xquik-dev/xquik-mcp), [VS Code](https://github.com/Xquik-dev/xquik-vscode) & [Raycast](https://github.com/Xquik-dev/xquik-raycast).
- [Xquik X (Twitter) API & scraper](https://xquik.com) and the [X (Twitter) API documentation](https://docs.xquik.com/api-reference/overview).

## Develop locally

```bash
uv sync
bin/check-local
```

`bin/check-local` runs the format, lint, type, audit, test & build checks.

## Help & contributing

- Read the [Xquik API reference](https://docs.xquik.com/api-reference/overview).
- Ask usage questions through the [organization support policy](https://github.com/Xquik-dev/.github/blob/main/SUPPORT.md).
- Report vulnerabilities through the [security policy](SECURITY.md).
- Read the [contribution guide](CONTRIBUTING.md).

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.
