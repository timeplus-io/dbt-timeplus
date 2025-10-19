{% materialization materialized_view, adapter='timeplus' -%}

  {%- set sql_header = config.get('sql_header', none) -%}
  {{ sql_header if sql_header is not none }}

  {% set target_relation = this.incorporate(type='view') %}
  {% set into_target = config.get('into', none) %}
  {% set mv_settings = config.get('settings', none) %}

  {{ run_hooks(pre_hooks, inside_transaction=False) }}
  {{ run_hooks(pre_hooks, inside_transaction=True) }}

  {% call statement('drop_existing') %}
    drop view if exists {{ target_relation.include(database=False) }}
  {% endcall %}

  {% call statement('main') %}
    create materialized view {{ target_relation.include(database=False) }}
    {%- if into_target %}
    into {{ into_target }}
    {%- endif %}
    as
    {{ sql }}
    {%- if mv_settings %}
    settings {{ mv_settings }}
    {%- endif %}
  {% endcall %}

  {{ run_hooks(post_hooks, inside_transaction=True) }}
  {% do adapter.commit() %}
  {{ run_hooks(post_hooks, inside_transaction=False) }}

  {{ return({ 'relations': [target_relation] }) }}

{%- endmaterialization %}
