<p align="center">
  <img src="https://raw.githubusercontent.com/timeplus-io/dbt-proton/master/etc/dbt-logo-full.svg" alt="dbt logo" width="300"/>
</p>

# dbt-proton

This plugin ports [dbt](https://getdbt.com) functionality to [Timeplus Proton](https://github.com/timeplus-io/proton).


### Installation

Use your favorite Python package manager to install the app from PyPI, e.g.

```bash
pip install dbt-proton
```

### Development
Follow the [dbt Documentation](https://docs.getdbt.com/docs/core/pip-install) to install dbt with pip.
```shell
python3.10 -m venv proton-dbt-env
source proton-dbt-env/bin/activate
pip install dbt-core
pip install -r dev_requirements.txt
```
Then run `pip install -e .` to install the current dev code.
Run `pytest tests/unit/test_adapter.py` to run basic tests.
Run `pytest tests/integration/proton.dbtspec` to run integration tests.

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
So we use a simple model `schema.table`, where `schema` is the Timeplus' database.

### Model Configuration

| Option         | Description                                                                                                                                          | Required?                         |
|----------------|------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|
| engine         | The table engine (type of stream) to use when creating tables                                                                                         | Optional (default: `Stream()`) |
| order_by     | A tuple of column names or arbitrary expressions. This allows you to create a small sparse index that helps find data faster.                        | Optional (default: `tuple()`)     |
| partition_by | A partition is a logical combination of records in a table by a specified criterion. The partition key can be any expression from the table columns. | Optional                          |

### Example Profile

```
your_profile_name:
  target: dev
  outputs:
    dev:
      type: proton
      schema: [database name] # default default
      host: [db.url.proton] # default localhost

      # optional
      port: [port]  # default 8463
      user: [user]
      password: [abc123]
      cluster: [cluster name]
      verify: [verify] # default False
      secure: [secure] # default False
      connect_timeout: [10] # default 10
      send_receive_timeout: [300] # default 300
      sync_request_timeout: [5] # default 5
      compress_block_size: [1048576] # default 1048576
      compression: ['lz4'] # default '' (disable)
```
