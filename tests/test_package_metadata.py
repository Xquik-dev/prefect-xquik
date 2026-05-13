from __future__ import annotations

from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

from prefect_xquik import __version__
from prefect_xquik.client import USER_AGENT

ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_version_matches_package_version() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())

    assert pyproject["project"]["version"] == __version__


def test_readme_install_url_matches_package_version() -> None:
    readme = (ROOT / "README.md").read_text()

    assert (
        "https://github.com/Xquik-dev/prefect-xquik/releases/download/"
        f"v{__version__}/prefect_xquik-{__version__}-py3-none-any.whl"
    ) in readme


def test_user_agent_matches_package_version() -> None:
    assert f"prefect-xquik/{__version__}" == USER_AGENT
