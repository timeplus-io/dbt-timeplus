import pytest

from dbt.tests.adapter.basic.test_base import BaseSimpleMaterializations
from dbt.tests.adapter.basic.test_singular_tests import BaseSingularTests
from dbt.tests.adapter.basic.test_singular_tests_ephemeral import BaseSingularTestsEphemeral
from dbt.tests.adapter.basic.test_empty import BaseEmpty
from dbt.tests.adapter.basic.test_ephemeral import BaseEphemeral
from dbt.tests.adapter.basic.test_incremental import BaseIncremental
from dbt.tests.adapter.basic.test_generic_tests import BaseGenericTests
from dbt.tests.adapter.basic.test_snapshot_check_cols import BaseSnapshotCheckCols
from dbt.tests.adapter.basic.test_snapshot_timestamp import BaseSnapshotTimestamp
from dbt.tests.adapter.basic.test_adapter_methods import BaseAdapterMethod

@pytest.mark.skip(reason="Proton streams are streaming by default; base suite assumes bounded table semantics.")
class TestSimpleMaterializationsMyAdapter(BaseSimpleMaterializations):
    pass


class TestSingularTestsMyAdapter(BaseSingularTests):
    pass


@pytest.mark.skip(reason="Ephemeral not supported on Timeplus/Proton.")
class TestSingularTestsEphemeralMyAdapter(BaseSingularTestsEphemeral):
    pass


class TestEmptyMyAdapter(BaseEmpty):
    pass


@pytest.mark.skip(reason="Ephemeral not supported on Timeplus/Proton.")
class TestEphemeralMyAdapter(BaseEphemeral):
    pass


@pytest.mark.skip(reason="Incremental uses bounded-by-default semantics in base suite; Proton is streaming by default.")
class TestIncrementalMyAdapter(BaseIncremental):
    pass


class TestGenericTestsMyAdapter(BaseGenericTests):
    pass


class TestSnapshotCheckColsMyAdapter(BaseSnapshotCheckCols):
    pass


class TestSnapshotTimestampMyAdapter(BaseSnapshotTimestamp):
    pass


class TestBaseAdapterMethod(BaseAdapterMethod):
    pass
