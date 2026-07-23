# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: Apache-2.0

test:
    uv run pytest

lint:
    uv run ruff check .

format:
    uv run ruff format .
