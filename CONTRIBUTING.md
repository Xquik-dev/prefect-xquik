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

Check endpoint names, parameters, examples, and contract headers against the
Xquik OpenAPI schema or public documentation.

Keep credentials in `XquikCredentials` blocks. Never add runtime secrets to
examples, tests, documentation, or issues.

## Release

Configure this PyPI trusted publisher:

- PyPI project: `prefect-xquik`
- Owner: `Xquik-dev`
- Repository: `prefect-xquik`
- Workflow: `publish.yml`

Activate the publisher before creating a GitHub release. The tag must match the
package version. The workflow checks, builds, and publishes without a stored token.
