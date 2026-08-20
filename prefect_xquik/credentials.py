# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from prefect.blocks.abstract import CredentialsBlock
from pydantic import Field, SecretStr, field_validator

from prefect_xquik.client import (
    DEFAULT_API_CONTRACT,
    DEFAULT_BASE_URL,
    XquikClient,
    _normalize_base_url,
)


class XquikCredentials(CredentialsBlock):
    """Store credentials for Xquik API requests."""

    _block_type_name = "Xquik API Credentials"
    _documentation_url = "https://docs.xquik.com/guides/prefect"
    _logo_url = "https://xquik.com/icon.svg"

    api_key: SecretStr = Field(
        ...,
        description="API key for Xquik requests.",
    )
    base_url: str = Field(
        default=DEFAULT_BASE_URL,
        description="Base URL for Xquik API requests.",
    )
    api_contract: str = Field(
        default=DEFAULT_API_CONTRACT,
        description="API contract date sent with each Xquik request.",
    )
    timeout_seconds: float = Field(
        default=30.0,
        description="Seconds to wait before a request times out.",
        gt=0,
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("api_key is empty. Add an Xquik API key.")
        return value

    @field_validator("base_url")
    @classmethod
    def normalize_base_url(cls, value: str) -> str:
        return _normalize_base_url(value)

    @field_validator("api_contract")
    @classmethod
    def validate_api_contract(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("api_contract is empty. Enter a contract date.")
        return stripped

    def get_client(self) -> XquikClient:
        """Create an async Xquik API client from this block."""

        return XquikClient(
            api_key=self.api_key.get_secret_value(),
            api_contract=self.api_contract,
            base_url=self.base_url,
            timeout_seconds=self.timeout_seconds,
        )
