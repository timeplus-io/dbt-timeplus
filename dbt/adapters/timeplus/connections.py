from typing import Optional, Any, Tuple

import agate
import time
import dbt.exceptions
import sys

from dataclasses import dataclass
from contextlib import contextmanager

from proton_driver import Client, errors

from dbt.adapters.contracts.connection import Connection, Credentials
from dbt.adapters.sql import SQLConnectionManager
import logging
from dbt.version import __version__ as dbt_version
logger = logging.getLogger("dbt.adapters.timeplus")


@dataclass
class ProtonCredentials(Credentials):
    host: str = 'localhost'
    port: Optional[int] = None
    user: Optional[str] = 'default'
    database: Optional[str] = 'default'
    schema: Optional[str] = 'default'
    password: str = ''
    cluster: Optional[str] = None
    secure: bool = False
    verify: bool = False
    connect_timeout: int = 10
    send_receive_timeout: int = 300
    sync_request_timeout: int = 5
    compress_block_size: int = 1048576
    compression: str = ''

    @property
    def type(self):
        return 'timeplus'

    @property
    def unique_field(self):
        return self.host

    def __post_init__(self):
        # keep provided schema; default database can be 'default'
        if self.database is None:
            self.database = 'default'

    def _connection_keys(self):
        return ('host', 'port', 'user', 'schema', 'secure', 'verify')


class ProtonConnectionManager(SQLConnectionManager):
    TYPE = 'timeplus'

    @contextmanager
    def exception_handler(self, sql):
        try:
            yield

        except Exception as exp:
            logger.debug('Error running SQL: %s', sql)
            if isinstance(exp, dbt.exceptions.DbtRuntimeError):
                raise
            raise dbt.exceptions.DbtRuntimeError('Timeplus exception:  ' + str(exp)) from exp

    @classmethod
    def open(cls, connection):
        if connection.state == 'open':
            logger.debug('Connection is already open, skipping open.')
            return connection

        credentials = cls.get_credentials(connection.credentials)
        kwargs = {}

        try:
            handle = Client(
                host=credentials.host,
                port=credentials.port,
                database=credentials.database,
                user=credentials.user,
                password=credentials.password,
                client_name=f'dbt-{dbt_version}',
                secure=credentials.secure,
                verify=credentials.verify,
                connect_timeout=credentials.connect_timeout,
                send_receive_timeout=credentials.send_receive_timeout,
                sync_request_timeout=credentials.sync_request_timeout,
                compress_block_size=credentials.compress_block_size,
                compression=False if credentials.compression == '' else credentials.compression,
                **kwargs,
            )
            connection.handle = handle
            connection.state = 'open'
        except Exception as e:
            logger.debug('Got an error when attempting to open a Timeplus connection: %s', str(e))
            connection.handle = None
            connection.state = 'fail'
            raise dbt.exceptions.FailedToConnectException(str(e))

        return connection

    def cancel(self, connection):
        connection_name = connection.name

        logger.debug("Cancelling query '%s'", connection_name)

        connection.handle.disconnect()

        logger.debug("Cancel query '%s'", connection_name)

    @classmethod
    def get_table_from_response(cls, response, columns) -> agate.Table:
        from dbt_common.clients.agate_helper import table_from_data_flat

        column_names = [x[0] for x in columns]

        data = []
        for row in response:
            data.append(dict(zip(column_names, row)))

        return table_from_data_flat(data, column_names)

    def execute(
        self, sql: str, auto_begin: bool = False, fetch: bool = False, limit: Optional[int] = None
    ) -> Tuple[str, agate.Table]:
        sql = self._add_query_comment(sql)
        conn = self.get_thread_connection()
        client = conn.handle

        with self.exception_handler(sql):
            #sys.stdout.write("Jove TEMP LOG "+sql+"\n")
            logger.debug("On %s: %s", conn.name, f"{sql}...")

            pre = time.time()

            response, columns = client.execute(sql, with_column_types=True)

            status = self.get_status(client)

            logger.debug('SQL status: %s in %.2f seconds', status, (time.time() - pre))

            if fetch:
                table = self.get_table_from_response(response, columns)
            else:
                from dbt_common.clients.agate_helper import empty_table

                table = empty_table()
            return status, table

    def add_query(
        self,
        sql: str,
        auto_begin: bool = True,
        bindings: Optional[Any] = None,
        abridge_sql_log: bool = False,
    ) -> Tuple[Connection, Any]:
        sql = self._add_query_comment(sql)
        conn = self.get_thread_connection()
        client = conn.handle

        with self.exception_handler(sql):
            logger.debug("On %s: %s", conn.name, f"{sql}...")

            pre = time.time()
            client.execute(sql)

            status = self.get_status(client)

            logger.debug('SQL status: %s in %.2f seconds', status, (time.time() - pre))

    @classmethod
    def get_credentials(cls, credentials):
        return credentials

    @classmethod
    def get_status(cls, cursor):
        return 'OK'

    @classmethod
    def get_response(cls, cursor):
        return 'OK'

    def begin(self):
        pass

    def commit(self):
        pass
