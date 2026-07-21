#!/bin/bash -eu

export PYTHONPATH="$SRC/prefect-xquik"

compile_python_fuzzer \
  "$SRC/prefect-xquik/.clusterfuzzlite/fuzz_client_helpers.py" \
  --hidden-import atheris \
  --paths "$SRC/prefect-xquik" \
  --exclude-module prefect \
  --exclude-module pydantic \
  --exclude-module prefect_xquik.credentials \
  --exclude-module prefect_xquik.tasks

cat > "$OUT/fuzz_client_helpers.options" <<'EOF'
[libfuzzer]
max_len = 4096
EOF
