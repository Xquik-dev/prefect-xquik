from __future__ import annotations

from prefect_xquik._version import __version__
from prefect_xquik.client import XquikClient, XquikError
from prefect_xquik.credentials import XquikCredentials
from prefect_xquik.tasks import (
    get_trends,
    get_tweet,
    get_user,
    get_user_tweets,
    search_tweets,
    search_users,
)

__all__ = [
    "XquikClient",
    "XquikCredentials",
    "XquikError",
    "__version__",
    "get_trends",
    "get_tweet",
    "get_user",
    "get_user_tweets",
    "search_tweets",
    "search_users",
]
