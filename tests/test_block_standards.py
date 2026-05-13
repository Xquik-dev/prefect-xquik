from __future__ import annotations

import pytest
from prefect.testing.standard_test_suites import BlockStandardTestSuite

from prefect_xquik import XquikCredentials


@pytest.mark.parametrize("block", [XquikCredentials])
class TestAllBlocksAdhereToStandards(BlockStandardTestSuite):
    @pytest.fixture
    def block(self, block: type[XquikCredentials]) -> type[XquikCredentials]:
        return block
