import os
import pytest
from dbt.tests.util import run_dbt


CH_ADDRESS = os.getenv("CH_ADDRESS")  # e.g., clickhouse:9440 or host:port
CH_DATABASE = os.getenv("CH_DATABASE", "default")
CH_TABLE = os.getenv("CH_TABLE", "ch_sink_table")
CH_USER = os.getenv("CH_USER", "default")
CH_PASSWORD = os.getenv("CH_PASSWORD", "")
CH_SECURE = os.getenv("CH_SECURE", "false")
CH_CA_CERT = os.getenv("CH_CA_CERT", "")


@pytest.mark.skipif(not CH_ADDRESS, reason="ClickHouse env not configured")
class TestExternalClickHouseTable:
    @pytest.fixture(scope="class")
    def project_config_update(self):
        secure_clause = f", secure='{CH_SECURE}'" if CH_SECURE else ""
        ca_clause = f", ssl_ca_cert_file = '{CH_CA_CERT}'" if CH_CA_CERT else ""
        prehook = [
            "drop external table if exists sink_ch_ext",
            (
                "create external table sink_ch_ext settings type='clickhouse', "
                f"address = '{CH_ADDRESS}', database='{CH_DATABASE}', table='{CH_TABLE}', user='{CH_USER}', password='{CH_PASSWORD}'{secure_clause}{ca_clause}"
            ),
            "create stream if not exists source(ts datetime64(3), c int32, j string)",
        ]
        return {
            "name": "ext_clickhouse_project",
            "models": {
                "+materialized": "materialized_view",
                "+into": "sink_ch_ext",
                "+pre_hook": prehook,
            },
        }

    @pytest.fixture(scope="class")
    def models(self):
        mv_sql = (
            "select ts, c as c, j, _tp_time as event_ts from source\n"
        )
        return {"mv_clickhouse.sql": mv_sql}

    def test_create_mv_to_clickhouse(self, project):
        results = run_dbt(["run", "-s", "mv_clickhouse"])
        assert len(results) == 1
