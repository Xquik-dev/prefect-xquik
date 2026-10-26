# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest
from prefect.testing.standard_test_suites.blocks import BlockStandardTestSuite
from typing_extensions import override

from prefect_xquik import XquikCredentials


@pytest.mark.parametrize("block", [XquikCredentials])
class TestXquikCredentialsBlock(BlockStandardTestSuite):
    @override
    @pytest.fixture()
    def block(self, block: type[XquikCredentials]) -> type[XquikCredentials]:
        return block
