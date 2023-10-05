#!/usr/bin/env bash

kubectl cp mapper.py hadoop-resourcemanager-0:/
kubectl cp reducer.py hadoop-resourcemanager-0:/

# Это чтобы обновить контейнер

sed -i -e 's/deb.debian.org/archive.debian.org/g' \
           -e 's|security.debian.org|archive.debian.org/|g' \
           -e '/stretch-updates/d' /etc/apt/sources.list

apt update -y  && apt install python3
ln -s /usr/bin/python3 /usr/bin/python

# Отсортировать результаты

awk '{print $NF,$1}' part-00000 | sort -nr -t' ' -k1 | awk -F' ' '{print $NS}'
