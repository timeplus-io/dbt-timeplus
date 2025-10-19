import pytest
from dbt.tests.util import run_dbt


class TestMaterializedViewMulti:
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "name": "mv_multi_project",
        }

    @pytest.fixture(scope="class")
    def models(self):
        mv1 = (
            "{{ config(materialized='materialized_view',\n"
            "           into='mv_target',\n"
            "           settings='checkpoint_interval=5',\n"
            "           pre_hook=[\n"
            "             \"create random stream if not exists rd1(i int, s string)\",\n"
            "             \"create stream if not exists mv_target(win_start datetime64(3), s string, total int64)\"\n"
            "           ]) }}\n"
            "select window_start as win_start, s, sum(i) as total\n"
            "from tumble(rd1, 2s)\n"
            "group by window_start, s\n"
        )
        mv2 = (
            "{{ config(materialized='materialized_view',\n"
            "           into='mv_target',\n"
            "           settings='checkpoint_interval=5',\n"
            "           pre_hook=[\n"
            "             \"create random stream if not exists rd2(i int, s string)\"\n"
            "           ]) }}\n"
            "select window_start as win_start, s, sum(i) as total\n"
            "from tumble(rd2, 2s)\n"
            "group by window_start, s\n"
        )
        mv_join = (
            "{{ config(materialized='materialized_view',\n"
            "           into='mv_join_target',\n"
            "           pre_hook=[\n"
            "             \"create random stream if not exists left_s(i int, s string)\",\n"
            "             \"create random stream if not exists right_s(i int, s string)\",\n"
            "             \"create stream if not exists mv_join_target(i int, s string)\"\n"
            "           ]) }}\n"
            "select a.i, a.s from left_s as a left join table(right_s) as r on a.i = r.i\n"
        )
        return {
            "mv1.sql": mv1,
            "mv2.sql": mv2,
            "mv_join.sql": mv_join,
        }

    def test_two_mvs_same_target_and_join(self, project):
        results = run_dbt(["run"])  # should create all three MVs
        assert len(results) == 3

