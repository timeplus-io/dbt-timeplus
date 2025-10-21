{% macro timeplus_setup_kafka_clickhouse(
    database='default',
    kafka_brokers='kafka:29092',
    kafka_topic='e2e_events',
    ch_address='clickhouse:9000',
    ch_database='default',
    ch_table='e2e_aggregation_results'
) %}
  {#
    Create an end-to-end pipeline in Timeplus:
      - Kafka external stream reading JSONEachRow
      - Aggregation stream + MV to populate it
      - ClickHouse external table (sink)
      - MV to write aggregations into ClickHouse
      - A simple analytics view

    Usage:
      dbt run-operation timeplus_setup_kafka_clickhouse \
        --args "{database: default, kafka_brokers: 'kafka:29092', kafka_topic: 'e2e_events', ch_address: 'clickhouse:9000', ch_database: 'default', ch_table: 'e2e_aggregation_results'}"
  #}

  {% set db = database %}

  {# Optionally create database if not default (avoids privilege errors) #}
  {% if db is not none and db | lower != 'default' %}
    {% call statement('maybe_create_db') %}
      create database if not exists {{ adapter.quote(db) }}
    {% endcall %}
  {% endif %}

  {# Drop objects if they exist (views first) #}
  {% call statement('drop_view_user_activity') %}
    drop view if exists {{ adapter.quote(db) }}.user_activity_summary
  {% endcall %}
  {% call statement('drop_view_to_clickhouse') %}
    drop view if exists {{ adapter.quote(db) }}.to_clickhouse_mv
  {% endcall %}
  {% call statement('drop_view_event_aggs') %}
    drop view if exists {{ adapter.quote(db) }}.event_aggregations_mv
  {% endcall %}

  {% call statement('drop_stream_clickhouse_results') %}
    drop stream if exists {{ adapter.quote(db) }}.clickhouse_results
  {% endcall %}
  {% call statement('drop_stream_event_aggs') %}
    drop stream if exists {{ adapter.quote(db) }}.event_aggregations
  {% endcall %}
  {% call statement('drop_stream_kafka') %}
    drop stream if exists {{ adapter.quote(db) }}.kafka_events_stream
  {% endcall %}

  {# Kafka external stream #}
  {% call statement('create_kafka_ext') %}
    create external stream if not exists {{ adapter.quote(db) }}.kafka_events_stream (
      event_id string,
      user_id string,
      event_type string,
      amount float64,
      timestamp datetime64(3),
      metadata__source string,
      metadata__region string
    ) settings type='kafka', brokers='{{ kafka_brokers }}', topic='{{ kafka_topic }}', data_format='JSONEachRow'
  {% endcall %}

  {# Aggregation stream #}
  {% call statement('create_agg_stream') %}
    create stream if not exists {{ adapter.quote(db) }}.event_aggregations (
      win_start datetime64(3),
      win_end datetime64(3),
      user_id string,
      event_type string,
      region string,
      event_count uint64,
      total_amount float64,
      avg_amount float64,
      min_amount float64,
      max_amount float64,
      _tp_time datetime64(3) default now64(3) codec(DoubleDelta, LZ4)
    )
  {% endcall %}

  {# Aggregation MV #}
  {% call statement('create_agg_mv') %}
    create materialized view if not exists {{ adapter.quote(db) }}.event_aggregations_mv
    into {{ adapter.quote(db) }}.event_aggregations as
    select
      window_start as win_start,
      window_end as win_end,
      user_id,
      event_type,
      metadata__region as region,
      count() as event_count,
      sum(amount) as total_amount,
      avg(amount) as avg_amount,
      min(amount) as min_amount,
      max(amount) as max_amount,
      now64(3) as _tp_time
    from tumble({{ adapter.quote(db) }}.kafka_events_stream, timestamp, interval 10 second)
    group by window_start, window_end, user_id, event_type, metadata__region
  {% endcall %}

  {# ClickHouse external table (sink) #}
  {% call statement('create_ch_ext') %}
    create external table if not exists {{ adapter.quote(db) }}.clickhouse_results
    settings type='clickhouse', address='{{ ch_address }}', database='{{ ch_database }}', table='{{ ch_table }}'
  {% endcall %}

  {# MV that writes to ClickHouse #}
  {% call statement('create_sink_mv') %}
    create materialized view if not exists {{ adapter.quote(db) }}.to_clickhouse_mv
    into {{ adapter.quote(db) }}.clickhouse_results as
    select
      win_start,
      win_end,
      user_id,
      event_type,
      region,
      event_count,
      total_amount,
      avg_amount,
      min_amount,
      max_amount,
      now64(3) as inserted_at
    from {{ adapter.quote(db) }}.event_aggregations
    where event_count > 0
  {% endcall %}

  {# Simple analytics view #}
  {% call statement('create_analytics_view') %}
    create view if not exists {{ adapter.quote(db) }}.user_activity_summary as
    select
      user_id,
      count(distinct event_type) as unique_event_types,
      sum(event_count) as total_events,
      sum(total_amount) as total_spent,
      avg(avg_amount) as avg_transaction_amount,
      max(max_amount) as highest_transaction,
      count(distinct region) as active_regions,
      max(win_end) as last_activity
    from {{ adapter.quote(db) }}.event_aggregations
    where win_end >= now() - interval 1 hour
    group by user_id
    order by total_spent desc
  {% endcall %}

  {{ return('ok') }}
{% endmacro %}
