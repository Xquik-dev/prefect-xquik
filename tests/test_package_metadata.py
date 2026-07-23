from __future__ import annotations

import re
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
XQUIK_ICON_URL = "https://xquik.com/icon.svg"
FULL_AFFILIATION_NOTICE = (
    "Xquik is an independent third-party service. Not affiliated with X Corp. "
    '"Twitter" and "X" are trademarks of X Corp.'
)
COMPACT_AFFILIATION_NOTICE = "Not affiliated with X Corp."
ACTION_REFERENCE = re.compile(r"[^@\s]+@[0-9a-f]{40}")


def test_pyproject_version_matches_package_version() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())

    assert pyproject["project"]["version"] == __version__


def test_readme_uses_pypi_install() -> None:
    readme = (ROOT / "README.md").read_text()

    assert "pip install prefect-xquik" in readme
    assert "releases/download" not in readme


def test_public_metadata_has_affiliation_notices() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    readme = (ROOT / "README.md").read_text()

    assert FULL_AFFILIATION_NOTICE in readme
    assert COMPACT_AFFILIATION_NOTICE in pyproject["project"]["description"]


def test_workflow_actions_are_pinned_to_commit_shas() -> None:
    for workflow_path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        action_lines = [
            line.strip()
            for line in workflow_path.read_text().splitlines()
            if line.strip().startswith("uses:")
        ]
        assert action_lines
        for action_line in action_lines:
            action = action_line.removeprefix("uses:").partition("#")[0].strip()
            assert ACTION_REFERENCE.fullmatch(action), (
                f"Unpinned action in {workflow_path}: {action}"
            )


def test_publish_workflow_requires_exact_release_tag_on_main() -> None:
    workflow = (ROOT / ".github" / "workflows" / "publish.yml").read_text()

    assert "workflow_dispatch" not in workflow
    assert "ref: ${{ github.event.release.tag_name }}" in workflow
    assert "refs/tags/${RELEASE_TAG}^{commit}" in workflow
    assert "refs/remotes/origin/main" in workflow
    assert "default branch tip" in workflow
    assert workflow.count("id-token: write") == 1
    assert "attestations: true" in workflow


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


def test_block_logo_url_uses_public_xquik_icon() -> None:
    assert XquikCredentials._logo_url == XQUIK_ICON_URL


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
