# Contributing

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

Before changing endpoint names, parameters, examples, or API contract headers,
verify the behavior against the Xquik OpenAPI contract or public docs.

Keep credentials in `XquikCredentials` blocks. Do not add API keys or other
runtime secrets to examples, tests, docs, or issue text.

## Release

PyPI publishing uses GitHub trusted publishing. Configure a PyPI pending
publisher for:

- PyPI project: `prefect-xquik`
- Owner: `Xquik-dev`
- Repository: `prefect-xquik`
- Workflow: `publish.yml`

After the pending publisher is active, publish a GitHub release for a tag that
matches the package version. The release workflow runs the same checks as CI,
builds the wheel and sdist, verifies metadata, and publishes to PyPI without a
stored PyPI token.
