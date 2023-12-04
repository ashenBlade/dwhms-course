#!/usr/bin/env sh

# Создаем топики для работы
for topic in page-visit searching filtering cart-add cart-delete ordering \
      order-cancel review-review review-creating registering logging-in \
      profile-edit mailing-subscription support-contact recommendation-view \
      sale-participation item-comparison order-history-viewing item-return \
      promo-usage category-view
do
  echo "Создаю топик $topic"
  /pulsar/bin/pulsar-admin topics create "public/default/$topic"
done

echo "Топики созданы"

# Создаем коннекторы для каждого топика
for topic in page-visit filtering cart-add cart-delete ordering \
      order-cancel review-review review-creating registering logging-in \
      profile-edit mailing-subscription support-contact recommendation-view \
      sale-participation item-comparison order-history-viewing item-return \
      promo-usage category-view
do
  TABLE_NAME="$(echo $topic | tr - _)s"
  TOPIC=$topic
  echo "tenant: 'public'
namespace: 'default'
name: 'clickhouse-$TOPIC'
inputs: [ 'persistent://public/default/$TOPIC' ]
sinkType: 'jdbc-clickhouse'
configs:
    jdbcUrl: 'jdbc:clickhouse://clickhouse:8123/default'
    tableName: '$TABLE_NAME'
    useTransactions: 'false'" > /tmp/connector.yaml

  echo "Создаю коннектор для $TOPIC"
  /pulsar/bin/pulsar-admin sinks create \
      --sink-config-file "/tmp/connector.yaml" \
      --parallelism 1
done

# Удаляем созданный конфиг файл
rm /tmp/connector.yaml