from dbt.adapters.timeplus.impl import ProtonAdapter


def test_simple():
    assert ProtonAdapter.date_function()=='now()'
