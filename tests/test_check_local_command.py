# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash") or "/bin/bash"
SCRIPT = r"""#!/usr/bin/env bash
name=$(basename "$0")
if [ "${1:-}" = --version ]; then
 [ "$CHECK_CASE" != no-codeql ] || exit 1
 echo 2.27.2
 exit
fi
event="$name${UV_PYTHON:+ $UV_PYTHON}"
printf '%s\n' "$event" >> "$CHECK_EVENTS"
[ "$CHECK_CASE$name" != changedcodeql-security ] || touch "$CHECK_DIRTY"
[ "$CHECK_CASE" != "$event" ]
"""
STUB = r"""record() {
 printf '%s\n' "$1" >> "$CHECK_EVENTS"
 [ "$CHECK_CASE" != "$1" ]
}
dirty() { [ "$CHECK_CASE" = dirty ] || [ -e "$CHECK_DIRTY" ]; }
git() {
 case "$1 $2" in
  'rev-parse HEAD') echo abc123;;
  'status --porcelain') if dirty; then echo ' M README.md'; fi;;
  'grep -nP')
   printf '%s\n' ignores >> "$CHECK_EVENTS"
   [ "$CHECK_CASE" = ignores ] || return 1
   echo a.py:1:x;;
  *) exit 99;;
 esac
}
gh() {
 [ "$1 $2" = 'api --silent' ] || exit 99
 case "$3" in
  repos/Xquik-dev/prefect-xquik/commits/abc123) [ "$CHECK_CASE" != unpushed ];;
  repos/Xquik-dev/prefect-xquik/statuses/abc123)
   [ "$4 $6 $7 $8" = '-f -f context=xquik-local-checks -f' ] || exit 99
   [ "$#" = 9 ] || exit 99
   printf '%s: %s\n' "${5#state=}" "${9#description=}" >> "$CHECK_STATUSES";;
  *) exit 99;;
 esac
}
uv() {
 if [ "$*" = 'tool run --from reuse==6.2.0 reuse lint' ]; then
  record reuse
  return
 fi
 environment=$UV_PROJECT_ENVIRONMENT
 [ "$environment" != "${environment%/venv-$UV_PYTHON}" ] || exit 99
 case "$*" in
  'sync --locked --dev') record "sync $UV_PYTHON";;
  'run --no-sync ruff format --check .') record "format $UV_PYTHON";;
  'run --no-sync ruff check --ignore-noqa .') record "lint $UV_PYTHON";;
  'run --no-sync mypy --any-exprs-report '*)
   mkdir -p "$5"
   anys=0
   [ "$CHECK_CASE" != "any $UV_PYTHON" ] || anys=1
   printf 'Total %s 10 90.00%%\n' "$anys" > "$5/any-exprs.txt"
   record "types $UV_PYTHON";;
  'run --no-sync pip-audit') record "audit $UV_PYTHON";;
  'run --no-sync pytest')
   echo "===== 46 passed in 1.00s ====="
   record "test $UV_PYTHON";;
  'run --no-sync twine check '*) record "metadata $UV_PYTHON";;
  *) exit 99;;
 esac
}
export -f record dirty git gh uv
runner=$1; shift
bash "$runner" "$@"
"""
STEPS = [
    "sync",
    "format",
    "lint",
    "types",
    "audit",
    "test",
    "build_reproducibly.sh",
    "metadata",
]
UV = ("UV_PYTHON", "UV_PROJECT_ENVIRONMENT")
VERSIONS = ["3.10", "3.11", "3.12", "3.13"]
CHECKS = [
    "reuse",
    "ignores",
    *[f"{step} {version}" for version in VERSIONS for step in STEPS],
    "codeql-security",
]
PENDING = (
    "pending: Running licensing, lint, types, audit, tests, build & CodeQL "
    "on 4 Python versions."
)
PASSED = (
    "REUSE, format, lint, types, audit, tests (184 passed in 4 runs), "
    "reproducible build & metadata, CodeQL 2.27.2."
)


def run_checks(
    tmp_path: Path, case: str, *arguments: str
) -> tuple[int, list[str], list[str], list[str]]:
    project = tmp_path / "project"
    for folder in ("bin", "scripts"):
        (project / folder).mkdir(parents=True)
    runner = project / "bin/check-local"
    runner.write_bytes((ROOT / "bin/check-local").read_bytes())
    for name in ("codeql-security", "build_reproducibly.sh"):
        (project / "scripts" / name).write_text(SCRIPT)
        (project / "scripts" / name).chmod(0o755)
    events, statuses = tmp_path / "events", tmp_path / "statuses"
    events.touch()
    statuses.touch()
    result = subprocess.run(
        [BASH, "-c", STUB, "check-local-test", str(runner), *arguments],
        env={
            **{key: value for key, value in os.environ.items() if key not in UV},
            "CHECK_CASE": case,
            "CHECK_EVENTS": str(events),
            "CHECK_STATUSES": str(statuses),
            "CHECK_DIRTY": str(tmp_path / "dirty"),
        },
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout + result.stderr).splitlines()
    return (
        result.returncode,
        events.read_text().splitlines(),
        statuses.read_text().splitlines(),
        output,
    )


def test_success_status_lists_the_checks_that_passed(tmp_path: Path) -> None:
    status, events, statuses, output = run_checks(tmp_path, "ready")
    assert status == 0, output
    assert events == CHECKS
    assert statuses == [PENDING, f"success: Passed {PASSED}"]
    assert output[-1] == f"All local checks passed. They were {PASSED}"


@pytest.mark.parametrize(
    ("case", "ran", "failed"),
    [
        ("reuse", 1, "Licensing with REUSE lint"),
        ("ignores", 2, "Type ignore comments"),
        ("sync 3.10", 3, "Install locked dependencies on Python 3.10"),
        ("format 3.10", 4, "Format check on Python 3.10"),
        ("types 3.10", 6, "Type check on Python 3.10"),
        ("lint 3.11", 13, "Lint on Python 3.11"),
        ("any 3.12", 22, "Type check on Python 3.12"),
        ("audit 3.12", 23, "Dependency audit on Python 3.12"),
        ("test 3.13", 32, "Tests on Python 3.13"),
        (
            "build_reproducibly.sh 3.13",
            33,
            "Reproducible build and metadata on Python 3.13",
        ),
        ("metadata 3.13", 34, "Reproducible build and metadata on Python 3.13"),
        (
            "codeql-security",
            35,
            "Static analysis with CodeQL 2.27.2 security-extended queries",
        ),
        ("changed", 35, "Final tree check"),
    ],
)
def test_failed_check_posts_failure_and_stops(
    tmp_path: Path, case: str, ran: int, failed: str
) -> None:
    status, events, statuses, _ = run_checks(tmp_path, case)
    assert status != 0
    assert events == CHECKS[:ran]
    assert statuses == [PENDING, f"failure: Failed at {failed}."]


def test_unusable_codeql_fails_before_any_check(tmp_path: Path) -> None:
    status, events, statuses, _ = run_checks(tmp_path, "no-codeql")
    assert status == 1
    assert events == []
    assert statuses == [PENDING, "failure: Failed at CodeQL CLI."]


@pytest.mark.parametrize(
    ("case", "arguments", "reason"),
    [
        ("ready", ["--no-status"], "--no-status was passed."),
        ("dirty", [], "the tree has uncommitted changes."),
        (
            "unpushed",
            [],
            "GitHub does not have HEAD, or gh is signed out. Push first.",
        ),
    ],
)
def test_status_is_posted_only_for_a_clean_pushed_commit(
    tmp_path: Path, case: str, arguments: list[str], reason: str
) -> None:
    status, events, statuses, output = run_checks(tmp_path, case, *arguments)
    assert status == 0, output
    assert events == CHECKS
    assert statuses == []
    assert output[0] == f"==> Commit status not posted because {reason}"


def test_unknown_option_stops_before_any_check(tmp_path: Path) -> None:
    status, events, statuses, output = run_checks(tmp_path, "ready", "--skip")
    assert status == 2
    assert events == []
    assert statuses == []
    assert output == [
        "check-local: unknown option --skip. Use --no-status or no option."
    ]
