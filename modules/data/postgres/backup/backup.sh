#!/usr/bin/env bash
set -Eeuo pipefail

BACKUP_ROOT="${1:-/var/lib/cloudstack/backups/postgres}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="${BACKUP_ROOT}/postgres-${TIMESTAMP}.sql"
PARTIAL="${BACKUP}.partial"

mkdir -p "${BACKUP_ROOT}"
chmod 0700 "${BACKUP_ROOT}"

cleanup() {
    rm -f "${PARTIAL}"
}
trap cleanup EXIT

podman exec cloudstack-data-postgres     pg_dumpall --clean --if-exists -U postgres > "${PARTIAL}"

chmod 0600 "${PARTIAL}"
mv "${PARTIAL}" "${BACKUP}"
sha256sum "${BACKUP}" > "${BACKUP}.sha256"
chmod 0600 "${BACKUP}.sha256"

trap - EXIT
printf '%s\n' "${BACKUP}"
