# Contributing

Run all commands from the repository root.

```bash
uv sync
uv run ruff format --check .
uv run ruff check .
uv run pytest
uv build
uv run twine check dist/*
```

Before changing endpoint names, parameters, examples, or API contract headers,
verify the behavior against the Xquik OpenAPI contract or public docs.

Keep credentials in `XquikCredentials` blocks. Do not add API keys or other
runtime secrets to examples, tests, docs, or issue text.
