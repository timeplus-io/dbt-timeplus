{% macro engine_value() %}
  {%- set engine = config.get('engine', validator=validation.any[basestring]) -%}
  {%- if engine is not none -%}
    {{ engine }}
  {%- endif -%}
{%- endmacro -%}

{% macro partition_cols(label) %}
  {%- set cols = config.get('partition_by', validator=validation.any[list, basestring]) -%}
  {%- if cols is not none %}
    {%- if cols is string -%}
      {{ label }} {{ cols }}
    {%- else -%}
      {{ label }} {{ cols | join(", ") }}
    {%- endif -%}
  {%- endif %}
{%- endmacro -%}

{% macro order_cols(label) %}
  {%- set cols = config.get('order_by', validator=validation.any[list, basestring]) -%}
  {%- if cols is not none %}
    {%- if cols is string -%}
      {{ label }} {{ cols }}
    {%- else -%}
      {{ label }} {{ cols | join(", ") }}
    {%- endif -%}
  {%- else %}
    {{ label }} id
  {%- endif %}
{%- endmacro -%}
{% macro timeplus__create_table_as(temporary, relation, sql) -%}
  {%- set sql_header = config.get('sql_header', none) -%}

  {{ sql_header if sql_header is not none }}

  {%- set schema = adapter.get_select_schema(sql) -%}
  {%- set col_defs = [] -%}
  {%- for c in schema -%}
    {%- do col_defs.append(c.name ~ ' ' ~ c.type) -%}
  {%- endfor -%}

  {% if temporary -%}
    {% call statement('create_temp_stream') %}
      create temporary stream {{ relation.name }} (
        {{ col_defs | join(',\n        ') }}
      )
    {% endcall %}
  {%- else %}
    {% call statement('create_stream') %}
      create stream if not exists {{ relation.include(database=False) }} (
        {{ col_defs | join(',\n        ') }}
      )
      {%- set eng = engine_value() -%}
      {%- if eng %}
      engine = {{ eng }}
      {%- endif %}
      {{ order_cols(label="order by") }}
      {{ partition_cols(label="partition by") }}
    {% endcall %}
  {%- endif %}

  {% call statement('insert_into_stream') %}
    insert into {{ relation.include(database=False) }}
    {{ sql }}
  {% endcall %}

  {{ return('select 1') }}
{%- endmacro %}

{% macro timeplus__create_view_as(relation, sql) -%}
  {%- set sql_header = config.get('sql_header', none) -%}

  {{ sql_header if sql_header is not none }}

  create view {{ relation.include(database=False) }}
  as (
    {{ sql }}
  )
{%- endmacro %}

{% macro timeplus__list_schemas(database) %}
  {% call statement('list_schemas', fetch_result=True, auto_begin=False) %}
    select name from system.databases
  {% endcall %}
  {{ return(load_result('list_schemas').table) }}
{% endmacro %}

{% macro timeplus__create_schema(relation) -%}
  {#- Avoid unnecessary errors if using built-in 'default' database -#}
  {%- if relation.schema and relation.schema | lower != 'default' -%}
    {%- call statement('create_schema') -%}
      create database if not exists {{ relation.without_identifier().include(database=False) }}
    {% endcall %}
  {%- endif -%}
{% endmacro %}

{% macro timeplus__drop_schema(relation) -%}
  {#- Never drop the built-in 'default' database from tests -#}
  {%- if relation.schema and relation.schema | lower != 'default' -%}
    {%- call statement('drop_schema') -%}
      drop database if exists {{ relation.without_identifier().include(database=False) }} cascade
    {%- endcall -%}
  {%- endif -%}
{% endmacro %}

{% macro timeplus__list_relations_without_caching(schema_relation) %}
  {% call statement('list_relations_without_caching', fetch_result=True) -%}
    select
      null as db,
      name as name,
      database as schema,
      if(engine not in ('MaterializedView', 'View'), 'table', 'view') as type
    from system.tables as t
    where schema = '{{ schema_relation.schema }}'
  {% endcall %}
  {{ return(load_result('list_relations_without_caching').table) }}
{% endmacro %}

{% macro timeplus__get_columns_in_relation(relation) -%}
  {% call statement('get_columns_in_relation', fetch_result=True) %}
    select
      name,
      type,
      position
    from system.columns
    where
      table = '{{ relation.identifier }}'
    {% if relation.schema %}
      and database = '{{ relation.schema }}'
    {% endif %}
    order by position
  {% endcall %}
  {% do return(load_result('get_columns_in_relation').table) %}
{% endmacro %}

{% macro timeplus__drop_relation(relation) -%}
  {% call statement('drop_relation', auto_begin=False) -%}
    drop stream if exists {{ relation }}
  {%- endcall %}
{% endmacro %}

{% macro timeplus__rename_relation(from_relation, to_relation) -%}
  {% call statement('drop_relation') %}
    drop stream if exists {{ to_relation }}
  {% endcall %}
  {% call statement('rename_relation') %}
    rename stream {{ from_relation }} to {{ to_relation }}
  {% endcall %}
{% endmacro %}

{% macro timeplus__truncate_relation(relation) -%}
  {% call statement('truncate_relation') -%}
    truncate stream {{ relation }}
  {%- endcall %}
{% endmacro %}

{% macro timeplus__make_temp_relation(base_relation, suffix) %}
  {% set tmp_identifier = base_relation.identifier ~ suffix %}
  {% set tmp_relation = base_relation.incorporate(
                              path={"identifier": tmp_identifier, "schema": None}) -%}
  {% do return(tmp_relation) %}
{% endmacro %}


{% macro timeplus__generate_database_name(custom_database_name=none, node=none) -%}
  {% do return(None) %}
{%- endmacro %}

{% macro timeplus__current_timestamp() -%}
  now()
{%- endmacro %}

{% macro timeplus__get_columns_in_query(select_sql) %}
  {% call statement('get_columns_in_query', fetch_result=True, auto_begin=False) -%}
    select * from (
        {{ select_sql }}
    ) as __dbt_sbq
    limit 0
  {% endcall %}

  {{ return(load_result('get_columns_in_query').table.columns | map(attribute='name') | list) }}
{% endmacro %}

{% macro timeplus__alter_column_type(relation, column_name, new_column_type) -%}
  {% call statement('alter_column_type') %}
    alter stream {{ relation }} modify column {{ adapter.quote(column_name) }} {{ new_column_type }}
  {% endcall %}
{% endmacro %}
