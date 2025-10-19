import pytest
from dbt.tests.util import run_dbt


class TestMaterializedView:
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "name": "mv_project",
            "models": {"+materialized": "view"},
        }

    @pytest.fixture(scope="class")
    def models(self):
        # A model that builds a materialized view; create a random source + target via pre-hook
        mv_sql = (
            "{{ config(materialized='materialized_view',\n"
            "           into='mv_target',\n"
            "           settings='checkpoint_interval=5',\n"
            "           pre_hook=[\n"
            "             \"create random stream if not exists rd(i int, s string)\",\n"
            "             \"create stream if not exists mv_target(win_start datetime64(3), s string, total int64)\"\n"
            "           ]) }}\n"
            "select window_start as win_start, s, sum(i) as total\n"
            "from tumble(rd, 2s)\n"
            "group by window_start, s\n"
        )

        return {
            "mv.sql": mv_sql,
        }

    def test_create_materialized_view(self, project):
        # Build only the mv model; DDL should complete immediately
        results = run_dbt(["run", "-s", "mv"])
        assert len(results) == 1
