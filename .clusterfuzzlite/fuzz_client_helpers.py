from __future__ import annotations

import sys
from collections.abc import Callable, Sequence
from contextlib import AbstractContextManager, suppress
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import NoReturn, Protocol, cast


class _Atheris(Protocol):
    def instrument_imports(self) -> AbstractContextManager[None]: ...

    def Setup(self, argv: Sequence[str], callback: Callable[[bytes], None]) -> None: ...

    def Fuzz(self) -> NoReturn: ...


atheris = cast(_Atheris, import_module("atheris"))

# Load the client module without executing package imports for Prefect blocks.
# Frozen modules live under _MEIPASS; source runs resolve from the repository.
bundle_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
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
