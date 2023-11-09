#!/usr/bin/env bash

# Выставляем совместимость вперед - FORWARD_TRANSITIVE
# Именно его, так как я буду добавлять новое поле
/pulsar/bin/pulsar-admin namespaces set-schema-compatibility-strategy --compatibility FORWARD_TRANSITIVE public/default

