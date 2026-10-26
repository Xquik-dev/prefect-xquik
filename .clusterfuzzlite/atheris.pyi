# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Callable, Sequence
from contextlib import AbstractContextManager
from typing import NoReturn

def instrument_imports() -> AbstractContextManager[object]: ...
def Setup(argv: Sequence[str], callback: Callable[[bytes], None]) -> list[str]: ...
def Fuzz() -> NoReturn: ...
