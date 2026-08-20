# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest
from pydantic import ValidationError

from prefect_xquik import XquikCredentials


def test_credentials_create_a_configured_client() -> None:
    credentials = XquikCredentials(
        api_key="secret-key",
        api_contract=" 2026-04-29 ",
        base_url="https://api.xquik.test/",
        timeout_seconds=5,
    )

    client = credentials.get_client()

    assert client.api_key == "secret-key"
    assert client.api_contract == "2026-04-29"
    assert client.base_url == "https://api.xquik.test"
    assert client.timeout.connect == 5


def test_credentials_use_the_public_rest_api_by_default() -> None:
    credentials = XquikCredentials(api_key="secret-key")

    assert credentials.base_url == "https://xquik.com/api/v1"


def test_credentials_explain_how_to_fix_an_empty_api_key() -> None:
    with pytest.raises(ValidationError, match="api_key is empty"):
        XquikCredentials(api_key=" ")


def test_credentials_explain_how_to_fix_an_invalid_base_url() -> None:
    with pytest.raises(ValidationError, match="base_url is invalid"):
        XquikCredentials(api_key="secret-key", base_url="xquik.test")


def test_credentials_explain_how_to_fix_an_empty_contract() -> None:
    with pytest.raises(ValidationError, match="api_contract is empty"):
        XquikCredentials(api_key="secret-key", api_contract=" ")
