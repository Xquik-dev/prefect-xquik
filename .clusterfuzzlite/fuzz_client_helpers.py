# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import sys
from contextlib import suppress
from pathlib import Path
from types import ModuleType

import atheris

meipass: object = getattr(sys, "_MEIPASS", None)
bundle_root = (
    Path(meipass) if isinstance(meipass, str) else Path(__file__).resolve().parents[1]
)
package = ModuleType("prefect_xquik")
package.__package__ = "prefect_xquik"
package.__path__ = [str(bundle_root / "prefect_xquik")]
sys.modules["prefect_xquik"] = package

with atheris.instrument_imports():
    from prefect_xquik.client import (
        _clean_params,
        _normalize_base_url,
        _quote_path_part,
        _strip_at_prefix,
    )


def fuzz_client_helpers(data: bytes) -> None:
    if len(data) > 4096:
        return

    text = data.decode("utf-8", errors="replace")
    selector = data[0] if data else 0

    _clean_params(
        {
            "text": text,
            "number": selector,
            "flag": bool(selector & 1),
            "missing": None,
        }
    )
    _strip_at_prefix(text)

    with suppress(ValueError):
        _quote_path_part(text, "value")

    with suppress(ValueError):
        _normalize_base_url(text)

    _normalize_base_url(f"https://example.com/{text}")


atheris.Setup(sys.argv, fuzz_client_helpers)
atheris.Fuzz()
