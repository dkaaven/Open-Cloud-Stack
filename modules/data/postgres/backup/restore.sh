#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <postgres-dump.sql>" >&2
    exit 2
fi

BACKUP="$1"

[[ -f "${BACKUP}" ]] || {
    echo "Backup not found: ${BACKUP}" >&2
    exit 1
}

if [[ -f "${BACKUP}.sha256" ]]; then
    (
        cd "$(dirname "${BACKUP}")"
        sha256sum --check "$(basename "${BACKUP}").sha256"
    )
fi

cat "${BACKUP}" | podman exec -i cloudstack-data-postgres     psql -X -U postgres -d postgres

podman exec cloudstack-data-postgres     vacuumdb -U postgres --all --analyze
