# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import sys
from pathlib import Path

from pydantic import JsonValue, TypeAdapter

from prefect_xquik import __version__
from prefect_xquik.client import USER_AGENT
from prefect_xquik.credentials import XquikCredentials

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]
TOML_VALUE: TypeAdapter[JsonValue] = TypeAdapter(JsonValue)
PREFECT_GUIDE_URL = "https://docs.xquik.com/guides/prefect"
XQUIK_ICON_URL = "https://xquik.com/icon.svg"
FULL_AFFILIATION_NOTICE = (
    "Xquik is an independent third-party service. Not affiliated with X Corp. "
    '"Twitter" and "X" are trademarks of X Corp.'
)
COMPACT_AFFILIATION_NOTICE = "Not affiliated with X Corp."


def pyproject_value(*keys: str) -> JsonValue:
    document: dict[str, object] = tomllib.loads((ROOT / "pyproject.toml").read_text())
    value = TOML_VALUE.validate_python(document)
    for key in keys:
        assert isinstance(value, dict)
        value = value[key]
    return value


def test_pyproject_and_package_versions_match() -> None:
    assert pyproject_value("project", "version") == __version__


def test_build_backend_and_package_path_are_fixed() -> None:
    wheel = pyproject_value("tool", "hatch", "build", "targets", "wheel")

    assert pyproject_value("build-system", "requires") == ["hatchling==1.32.4"]
    assert pyproject_value("build-system", "build-backend") == "hatchling.build"
    assert isinstance(wheel, dict)
    assert wheel["packages"] == ["prefect_xquik"]


def test_readme_installs_the_pypi_package() -> None:
    readme = (ROOT / "README.md").read_text()

    assert "pip install prefect-xquik" in readme
    assert "releases/download" not in readme


def test_readme_and_package_metadata_have_affiliation_notices() -> None:
    description = pyproject_value("project", "description")
    readme = (ROOT / "README.md").read_text()

    assert FULL_AFFILIATION_NOTICE in readme
    assert isinstance(description, str)
    assert COMPACT_AFFILIATION_NOTICE in description


def test_repository_has_no_github_actions_workflows() -> None:
    assert not (ROOT / ".github" / "workflows").exists()


def test_build_script_compares_repeated_builds() -> None:
    script = (ROOT / "scripts" / "build_reproducibly.sh").read_text()
    assert 'SOURCE_DATE_EPOCH="$(git log -1 --format=%ct)"' in script
    assert 'reproducible_dir="$(mktemp -d)"' in script
    assert 'cmp "$artifact"' in script


def test_user_agent_includes_the_package_version() -> None:
    assert f"prefect-xquik/{__version__}" == USER_AGENT


def test_public_links_use_the_canonical_prefect_guide() -> None:
    urls = pyproject_value("project", "urls")
    readme = (ROOT / "README.md").read_text()

    assert isinstance(urls, dict)
    assert urls["Documentation"] == PREFECT_GUIDE_URL
    assert urls["Homepage"] == PREFECT_GUIDE_URL
    assert (
        urls["Xquik API Reference"] == "https://docs.xquik.com/api-reference/overview"
    )
    assert PREFECT_GUIDE_URL in readme
    assert str(XquikCredentials._documentation_url) == PREFECT_GUIDE_URL


def test_credentials_block_uses_the_public_xquik_icon() -> None:
    assert str(XquikCredentials._logo_url) == XQUIK_ICON_URL


def test_package_keywords_cover_approved_search_terms() -> None:
    keywords = pyproject_value("project", "keywords")

    assert isinstance(keywords, list)
    assert {
        "data-pipelines",
        "prefect-collection",
        "prefect-integration",
        "social-media-api",
        "tweet-search",
        "twitter-api",
        "twitter-search",
        "workflow-orchestration",
        "xquik",
    }.issubset(set(keywords))
