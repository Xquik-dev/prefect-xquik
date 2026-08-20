# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: Apache-2.0

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


def test_pyproject_and_package_versions_match() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())

    assert pyproject["project"]["version"] == __version__


def test_build_backend_and_package_path_are_fixed() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())

    assert pyproject["build-system"]["requires"] == ["hatchling==1.31.0"]
    assert pyproject["build-system"]["build-backend"] == "hatchling.build"
    assert pyproject["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"] == [
        "prefect_xquik"
    ]


def test_readme_installs_the_pypi_package() -> None:
    readme = (ROOT / "README.md").read_text()

    assert "pip install prefect-xquik" in readme
    assert "releases/download" not in readme


def test_readme_and_package_metadata_have_affiliation_notices() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    readme = (ROOT / "README.md").read_text()

    assert FULL_AFFILIATION_NOTICE in readme
    assert COMPACT_AFFILIATION_NOTICE in pyproject["project"]["description"]


def test_every_workflow_action_uses_an_immutable_commit() -> None:
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
                f"Workflow action is not pinned in {workflow_path}: {action}"
            )


def test_publish_workflow_requires_the_release_tag_on_main() -> None:
    workflow = (ROOT / ".github" / "workflows" / "publish.yml").read_text()

    assert "workflow_dispatch" not in workflow
    assert "ref: ${{ github.event.release.tag_name }}" in workflow
    assert "refs/tags/${RELEASE_TAG}^{commit}" in workflow
    assert "refs/remotes/origin/main" in workflow
    assert "main branch tip" in workflow
    assert workflow.count("id-token: write") == 1
    assert "attestations: true" in workflow


def test_ci_and_releases_compare_repeated_builds() -> None:
    for workflow_name in ("ci.yml", "publish.yml"):
        workflow = (ROOT / ".github" / "workflows" / workflow_name).read_text()

        assert "run: ./scripts/build_reproducibly.sh" in workflow

    script = (ROOT / "scripts" / "build_reproducibly.sh").read_text()
    assert 'SOURCE_DATE_EPOCH="$(git log -1 --format=%ct)"' in script
    assert 'reproducible_dir="$(mktemp -d)"' in script
    assert 'cmp "$artifact"' in script


def test_user_agent_includes_the_package_version() -> None:
    assert f"prefect-xquik/{__version__}" == USER_AGENT


def test_public_links_use_the_canonical_prefect_guide() -> None:
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


def test_credentials_block_uses_the_public_xquik_icon() -> None:
    assert XquikCredentials._logo_url == XQUIK_ICON_URL


def test_package_keywords_cover_approved_search_terms() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())

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
    }.issubset(set(pyproject["project"]["keywords"]))
