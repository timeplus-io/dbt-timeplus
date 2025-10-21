{% macro timeplus__load_csv_rows(model, agate_table) %}
  {% set cols_sql = get_seed_column_quoted_csv(model, agate_table.column_names) %}
  {% set data_sql = adapter.get_csv_data(agate_table) %}

  {% set sql -%}
      insert into {{ this.render() }} ({{ cols_sql }}) format CSV
      {{ data_sql }}
  {%- endset %}

  {% do adapter.add_query(sql, bindings=agate_table, abridge_sql_log=True) %}
{% endmacro %}

{% macro timeplus__create_csv_table(model, agate_table) %}
  {%- set column_override = model['config'].get('column_types', {}) -%}
  {%- set quote_seed_column = model['config'].get('quote_columns', None) -%}

  {% set sql %}
    create stream {{ this.render() }} (
      {%- for col_name in agate_table.column_names -%}
        {%- set inferred_type = adapter.convert_type(agate_table, loop.index0) -%}
        {%- set type = column_override.get(col_name, inferred_type) -%}
        {%- set column_name = (col_name | string) -%}
          {{ adapter.quote_seed_column(column_name, quote_seed_column) }} {{ type }} {%- if not loop.last%},{%- endif %}
      {%- endfor -%}
    )
  {% endset %}

  {# Ensure idempotency: drop any existing stream before creating #}
  {% call statement('drop_seed_if_exists') -%}
    drop stream if exists {{ this.render() }}
  {%- endcall %}

  {% call statement('_') -%}
    {{ sql }}
  {%- endcall %}

  {{ return(sql) }}
{% endmacro %}
