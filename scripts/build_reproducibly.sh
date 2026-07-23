#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

output_dir="${1:-dist}"
SOURCE_DATE_EPOCH="$(git log -1 --format=%ct)"
export SOURCE_DATE_EPOCH

uv build --out-dir "$output_dir"

reproducible_dir="$(mktemp -d)"
uv build --out-dir "$reproducible_dir"

for artifact in "$output_dir"/*; do
  artifact_name="$(basename "$artifact")"
  cmp "$artifact" "$reproducible_dir/$artifact_name"
  printf 'Reproducible: %s\n' "$artifact_name"
done
