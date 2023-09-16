#!/usr/bin/env bash

# Запускаем конфиг
echo "Запуск сервисов"
kubectl apply -f hadoop.config.yaml -f hadoop.namenode.yaml -f hadoop.datanode.yaml

echo "Начинаю проброс портов"

kubectl port-forward hadoop-namenode-0 3000:9870 >/dev/null &
kubectl port-forward hadoop-datanode-0 3001:9864 >/dev/null &
kubectl port-forward hadoop-datanode-1 3002:9864 >/dev/null &
kubectl port-forward hadoop-datanode-2 3003:9864 >/dev/null &

echo "Открыты HTTP порты:
NAMENODE:
  - localhost:3000
DATANODE:
  - localhost:3001
  - localhost:3002
  - localhost:3003

Для завершения работы нажми Ctrl+C
"

(trap exit SIGINT; read -r -d '' _ </dev/tty) # Ждем завершения работы

echo "Получил SIGINT - закрываю порты"
jobs -p | xargs kill -9
