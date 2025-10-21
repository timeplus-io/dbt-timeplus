import pytest
import os
import warnings
from argparse import Namespace
from dbt.tests.fixtures.project import (
    project_root as _project_root,
    profiles_root as _profiles_root,
    shared_data_dir as _shared_data_dir,
    test_data_dir as _test_data_dir,
    TestProjInfo,
)
from dbt.events.logging import setup_event_logger

# Import the standard functional fixtures as a plugin
# Note: fixtures with session scope need to be local
pytest_plugins = ["dbt.tests.fixtures.project"]

# The profile dictionary, used to write out profiles.yml
# dbt will supply a unique schema per test, so we do not specify 'schema' here
@pytest.fixture(scope="class")
def dbt_profile_target():
    return {
        'type': 'timeplus',
        'threads': 1,
        'host': os.getenv('DBT_TEST_HOST', 'localhost'),
        'port': int(os.getenv('DBT_TEST_PORT', '8463')),
        'user': os.getenv('DBT_TEST_USER', 'default'),
        'password': os.getenv('DBT_TEST_PASSWORD', ''),
    }


# Override default schema selection to use a fixed, pre-existing database.
# This avoids requiring CREATE DATABASE privileges in the test environment.
@pytest.fixture(scope="class")
def dbt_profile_data(dbt_profile_target, profiles_config_update):
    schema = os.getenv('DBT_TEST_SCHEMA', 'default')
    profile = {
        "test": {
            "outputs": {
                "default": {
                    **dbt_profile_target,
                    "schema": schema,
                }
            },
            "target": "default",
        },
    }
    if profiles_config_update:
        profile.update(profiles_config_update)
    return profile


# Override the default 'project' fixture to avoid creating/dropping schemas.
@pytest.fixture(scope="class")
def project(
    initialization,
    clean_up_logging,
    _project_root,
    _profiles_root,
    request,
    unique_schema,
    profiles_yml,
    dbt_project_yml,
    packages_yml,
    dependencies_yml,
    selectors_yml,
    adapter,
    project_files,
    _shared_data_dir,
    _test_data_dir,
    logs_dir,
    test_config,
):
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="logbook")
    log_flags = Namespace(
        LOG_PATH=logs_dir,
        LOG_FORMAT="json",
        LOG_FORMAT_FILE="json",
        USE_COLORS=False,
        USE_COLORS_FILE=False,
        LOG_LEVEL="info",
        LOG_LEVEL_FILE="debug",
        DEBUG=False,
        LOG_CACHE_EVENTS=False,
        QUIET=False,
        LOG_FILE_MAX_BYTES=1000000,
    )
    setup_event_logger(log_flags)

    orig_cwd = os.getcwd()
    os.chdir(_project_root)

    # Force schema to a safe, pre-existing database to avoid CREATE DATABASE.
    forced_schema = os.getenv('DBT_TEST_SCHEMA', 'default')

    project = TestProjInfo(
        project_root=_project_root,
        profiles_dir=_profiles_root,
        adapter_type=adapter.type(),
        test_dir=request.fspath.dirname,
        shared_data_dir=_shared_data_dir,
        test_data_dir=_test_data_dir,
        test_schema=forced_schema,
        database=adapter.config.credentials.database,
        test_config=test_config,
    )

    # Do not auto-create or drop schemas; the forced schema must exist already.
    yield project

    os.chdir(orig_cwd)
