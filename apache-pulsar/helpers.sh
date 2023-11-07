#!/usr/bin/env bash

# Выставляем автообновление схемы для всего неймспейса
/pulsar/bin/pulsar-admin namespaces set-is-allow-auto-update-schema --enable public/default
/pulsar/bin/pulsar-admin namespaces set-schema-autoupdate-strategy  --compatibility Full public/default
/pulsar/bin/pulsar-admin namespaces set-schema-validation-enforce --disable public/default
