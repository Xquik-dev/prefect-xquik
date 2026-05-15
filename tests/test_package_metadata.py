from __future__ import annotations

from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

from prefect_xquik import __version__
from prefect_xquik.client import USER_AGENT
from prefect_xquik.credentials import XquikCredentials

ROOT = Path(__file__).resolve().parents[1]
PREFECT_GUIDE_URL = "https://docs.xquik.com/guides/prefect"


def test_pyproject_version_matches_package_version() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())

    assert pyproject["project"]["version"] == __version__


def test_readme_uses_pypi_install() -> None:
    readme = (ROOT / "README.md").read_text()

    assert "pip install prefect-xquik" in readme
    assert "releases/download" not in readme


def test_user_agent_matches_package_version() -> None:
    assert f"prefect-xquik/{__version__}" == USER_AGENT


def test_prefect_guide_url_is_canonical() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    readme = (ROOT / "README.md").read_text()

    assert pyproject["project"]["urls"]["Documentation"] == PREFECT_GUIDE_URL
    assert pyproject["project"]["urls"]["Homepage"] == PREFECT_GUIDE_URL
    assert (
        pyproject["project"]["urls"]["Xquik API Reference"]
        == "https://docs.xquik.com/api-reference/overview"
    )
    assert PREFECT_GUIDE_URL in readme
    assert XquikCredentials._documentation_url == PREFECT_GUIDE_URL


def test_package_keywords_cover_discovery_terms() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())

    assert {
        "data-pipelines",
        "prefect-collection",
        "prefect-integration",
        "twitter-api",
        "workflow-orchestration",
        "x-twitter",
        "xquik",
    }.issubset(set(pyproject["project"]["keywords"]))
