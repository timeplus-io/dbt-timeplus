{% materialization materialized_view, adapter='timeplus' -%}

  {% set target_relation = this.incorporate(type='view') %}
  {% set into_target = config.get('into', none) %}
  {% set mv_settings = config.get('settings', none) %}

  {% call statement('drop_existing') %}
    drop view if exists {{ target_relation.include(database=False) }}
  {% endcall %}

  {% call statement('create_mv') %}
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

  {{ return({ 'relations': [target_relation] }) }}

{%- endmaterialization %}

