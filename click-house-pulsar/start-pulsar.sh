#!/usr/bin/env sh

bin/apply-config-from-env.py conf/broker.conf

exec bin/pulsar standalone