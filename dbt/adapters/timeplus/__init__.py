from dbt.adapters.timeplus.connections import ProtonConnectionManager  # noqa
from dbt.adapters.timeplus.connections import ProtonCredentials
from dbt.adapters.timeplus.relation import ProtonRelation  # noqa
from dbt.adapters.timeplus.column import ProtonColumn  # noqa
from dbt.adapters.timeplus.impl import ProtonAdapter

from dbt.adapters.base import AdapterPlugin
from dbt.include import timeplus


Plugin = AdapterPlugin(
    adapter=ProtonAdapter,
    credentials=ProtonCredentials,
    include_path=timeplus.PACKAGE_PATH)
