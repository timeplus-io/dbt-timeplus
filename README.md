<p align="center">
  <img src="etc/dbt-logo-full.svg" alt="dbt logo" width="300"/>
</p>

# dbt-timeplus

This plugin ports [dbt](https://getdbt.com) functionality to [Timeplus Proton](https://github.com/timeplus-io/proton).


### Installation

Use your favorite Python package manager to install the app from PyPI, e.g.

```bash
pip install dbt-timeplus
```

### Development
Follow the [dbt Documentation](https://docs.getdbt.com/docs/core/pip-install) to install dbt with pip.
```shell
python3.10 -m venv proton-dbt-env
source proton-dbt-env/bin/activate
# Installs matching versions for local dev/tests
pip install -r dev_requirements.txt
```
Then run `pip install -e .` to install the current dev code.

Testing:
- `pytest tests/unit` runs fast unit tests (no DB needed).
- Functional tests require a running Timeplus endpoint. Export env vars or use `tests/test.env`:
  - `DBT_TEST_HOST` (default `localhost`)
  - `DBT_TEST_PORT` (default `8463`)
  - `DBT_TEST_USER` (default `default`)
  - `DBT_TEST_PASSWORD` (default empty)
  - `DBT_TEST_SCHEMA` (default `default`)
- Run `pytest tests/functional` for functional tests.
- Run `pytest tests/integration/timeplus.dbtspec` for integration tests.

#### External sinks (Kafka / ClickHouse)
- If you run Kafka/ClickHouse locally (e.g., via Docker Compose), set the relevant environment variables for your setup, then run `pytest -k external` to execute only those tests. See `tests/test.env.sample` for the full variable list.

Note: host:port values depend on your environment and are not enforced by the adapter. Use the ports your services expose.

Typical defaults:
- ClickHouse native: `9000` (plain), `9440` (TLS). HTTP: `8123/8443`.
- Kafka brokers: `9092` (plain), others depending on your deployment.

Tip: copy `tests/test.env.sample` to `tests/test.env` and edit for local runs (pytest-dotenv loads it automatically).

### Compatibility

- Python: 3.10, 3.11, 3.12
- dbt-core: 1.10.x (pinned to `1.10.13`)
- proton-driver: `>=0.2.13`

### Supported features

- [x] Table materialization
- [x] View materialization
- [x] Incremental materialization
- [x] Seeds
- [x] Sources
- [x] Docs generate
- [x] Tests
- [x] Snapshots (experimental)
- [ ] Ephemeral materialization

# Usage Notes

### Database

The dbt model `database.schema.table` is not compatible with Timeplus because Timeplus does not support a `schema`.
So we use a simple model `schema.table`, where `schema` is the Timeplus database.

### Bounded vs streaming queries

Timeplus streams are streaming by default. To avoid long-running queries in dbt models and tests, wrap streaming sources with `table(...)` when selecting, for example:

```
select window_end, cid, count() as cnt
from tumble(table(car_live_data), 1s)
group by window_end, cid
```

This produces a bounded snapshot for deterministic builds.

### Model Configuration

| Option       | Description                                                                                                                                          | Default                                      |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------|
| engine       | Stream engine used when creating streams                                                                                                             | `Stream(1, 1, rand())`                       |
| order_by     | Column(s) or expression(s) used for ordering                                                                                                         | `to_start_of_hour(_tp_time)`                 |
| partition_by | Partition expression for stream                                                                                                                      | `to_YYYYMMDD(_tp_time)`                      |

### Example Profile

```
your_profile_name:
  target: dev
  outputs:
    dev:
      type: timeplus
      schema: [database name] # default default
      host: [db.url.timeplus] # default localhost

      # optional
      port: [port]  # default 8463
      user: [user]
      password: [abc123]
      verify: [verify] # default False
      secure: [secure] # default False
      connect_timeout: [10] # default 10
      send_receive_timeout: [300] # default 300
      sync_request_timeout: [5] # default 5
      compress_block_size: [1048576] # default 1048576
      compression: ['lz4'] # default '' (disable)
```

### Materialized views

Create a materialized view that writes into a target stream and optionally applies settings:

```
{{ config(materialized='materialized_view', into='mv_target', settings='checkpoint_interval=5') }}
select window_start as win_start, s, sum(i) as total
from tumble(table(rd), 2s)
group by window_start, s
```

### External sinks (Kafka / ClickHouse)

The adapter includes tests/examples for Kafka and ClickHouse sinks. Export the environment variables shown above and run `pytest -k external` to execute only those tests.

### Release and versioning

- Package name: `dbt-timeplus` (renamed from `dbt-proton`).
- Adapter version mirrors dbt minor (`1.10.*`).
- The bundled macro package version in `dbt/include/timeplus/dbt_project.yml` is kept in sync as a convention.
