#!/usr/bin/env sh

# Создаем синк для ClickHouse
bin/pulsar-admin sinks create \
  --sink-type 'jdbc-clickhouse' \
  --name "clickhouse-events-sink" \
  --inputs "persistent://public/default/clickhouse-test" \
  --tenant "public" \
  --sink-config-file /configs/clickhouse-connector.yaml \
  --parallelism 1

bin/pulsar-admin sinks start \
  --name 'clickhouse-events-sink'
