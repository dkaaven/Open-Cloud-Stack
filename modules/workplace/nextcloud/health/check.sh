#!/usr/bin/env bash
set -Eeuo pipefail

readonly CONTAINER="cloudstack-workplace-nextcloud"

podman container exists "${CONTAINER}" || {
    printf '[cloudstack] ERROR: Nextcloud container not found.\n' >&2
    exit 1
}

health="$(
    podman inspect \
        --format '{{.State.Health.Status}}' \
        "${CONTAINER}"
)"

[[ "${health}" == "healthy" ]] || {
    printf '[cloudstack] ERROR: Nextcloud health: %s\n' \
        "${health:-unknown}" >&2
    exit 1
}

podman exec \
    --user 33 \
    "${CONTAINER}" \
    php /var/www/html/occ status

printf '[cloudstack] Nextcloud: healthy\n'
