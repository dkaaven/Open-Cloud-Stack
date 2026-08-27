#!/usr/bin/env bash
set -Eeuo pipefail

readonly CONTAINER="cloudstack-data-valkey"

podman container exists "${CONTAINER}" || {
    printf '[cloudstack] ERROR: Valkey container not found.\n' >&2
    exit 1
}

podman exec "${CONTAINER}" /etc/valkey/healthcheck.sh
printf '[cloudstack] Valkey: healthy\n'
