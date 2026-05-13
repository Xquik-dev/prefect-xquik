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
    """Block used to authenticate Xquik API requests."""

    _block_type_name = "Xquik Credentials"
    _documentation_url = "https://docs.xquik.com/api-reference/overview"

    api_key: SecretStr = Field(
        ...,
        description="Xquik API key.",
    )
    base_url: str = Field(
        default=DEFAULT_BASE_URL,
        description="Base URL for the Xquik API.",
    )
    api_contract: str = Field(
        default=DEFAULT_API_CONTRACT,
        description="Xquik API contract date sent with requests.",
    )
    timeout_seconds: float = Field(
        default=30.0,
        description="Request timeout in seconds.",
        gt=0,
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("api_key must not be empty")
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
            raise ValueError("api_contract must not be empty")
        return stripped

    def get_client(self) -> XquikClient:
        """Create an async Xquik client from this block."""

        return XquikClient(
            api_key=self.api_key.get_secret_value(),
            api_contract=self.api_contract,
            base_url=self.base_url,
            timeout_seconds=self.timeout_seconds,
        )
