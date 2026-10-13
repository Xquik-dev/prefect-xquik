# Contribute

Run all commands from the repository root.

```bash
uv sync
uv run ruff format --check .
uv run ruff check .
uv run pip-audit
uv run pytest
./scripts/build_reproducibly.sh
uv run twine check dist/*
```

`bin/check-local` runs these checks on Python 3.10 to 3.13, then REUSE lint and
CodeQL. Run it before you open a pull request.

Check endpoint names, parameters, examples, and contract headers against the
Xquik OpenAPI schema or public documentation.

Keep credentials in `XquikCredentials` blocks. Never add runtime secrets to
examples, tests, documentation, or issues.

## Release

Bump the version in `pyproject.toml` and `prefect_xquik/_version.py`. Add its
section to `CHANGELOG.md`, and merge the change to `main`.

Then run `bin/release-local` on a clean `main`. It runs `bin/check-local`,
builds twice, uploads to PyPI, tags the commit, and creates the GitHub release.
It reads the PyPI token from the Keychain item that `PYPI_KEYCHAIN_SERVICE`
names.

`bin/release-local --dry-run` previews a release. It uploads, tags, and
releases nothing.
