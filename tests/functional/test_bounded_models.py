import pytest
from dbt.tests.util import run_dbt


class TestBoundedTableAndIncremental:
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "name": "bounded_project",
        }

    @pytest.fixture(scope="class")
    def seeds(self):
        seed = """
id,name
1,Alice
2,Bob
3,Carol
""".lstrip()
        return {"base.csv": seed}

    @pytest.fixture(scope="class")
    def models(self):
        table_sql = (
            """
            {{ config(materialized='table',
                      pre_hook=["drop stream if exists " ~ target.schema ~ ".table_bounded"]) }}
            select * from table({{ ref('base') }})
            """.lstrip()
        )
        inc_sql = (
            """
            {{ config(materialized='incremental', unique_key='id',
                      pre_hook=["drop stream if exists " ~ target.schema ~ ".inc_bounded"]) }}
            select * from table({{ ref('base') }})
            """.lstrip()
        )
        return {
            "table_bounded.sql": table_sql,
            "inc_bounded.sql": inc_sql,
        }

    def test_bounded_table_and_incremental(self, project):
        results = run_dbt(["seed"])
        assert len(results) == 1

        # Build table model
        results = run_dbt(["run", "-s", "table_bounded"])
        assert len(results) == 1

        # Build incremental model (single run)
        results = run_dbt(["run", "-s", "inc_bounded"])
        assert len(results) == 1
