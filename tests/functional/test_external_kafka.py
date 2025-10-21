import os
import pytest
from dbt.tests.util import run_dbt


KAFKA_BROKERS = os.getenv("KAFKA_BROKERS")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")


@pytest.mark.skipif(not (KAFKA_BROKERS and KAFKA_TOPIC), reason="Kafka env not configured")
class TestExternalKafkaSink:
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "name": "ext_kafka_project",
        }

    @pytest.fixture(scope="class")
    def models(self):
        # Create external Kafka sink and MV that writes into it from a random source
        mv_sql = (
            f"{{{{ config(materialized='materialized_view',\n"
            f"           into='ext_kafka',\n"
            f"           pre_hook=[\n"
            f"             \"drop view if exists mv_kafka\",\n"
            f"             \"drop stream if exists ext_kafka\",\n"
            f"             \"create external stream ext_kafka (i int, s string) settings type='kafka', brokers='{KAFKA_BROKERS}', topic='{KAFKA_TOPIC}', data_format='JSONEachRow'\",\n"
            f"             \"create random stream if not exists rd(i int, s string)\"\n"
            f"           ]) }}}}\n"
            "select i, s from rd\n"
        )
        return {
            "mv_kafka.sql": mv_sql,
        }

    def test_create_mv_to_kafka(self, project):
        results = run_dbt(["run", "-s", "mv_kafka"])
        assert len(results) == 1
