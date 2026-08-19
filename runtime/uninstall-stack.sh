#!/usr/bin/env bash
set -Eeuo pipefail

readonly QUADLET_ROOT="/etc/containers/systemd/cloudstack"
readonly CONFIG_ROOT="/etc/cloudstack/modules"
readonly RUNTIME_ROOT="/etc/cloudstack/runtime"
readonly TARGET_FILE="/etc/systemd/system/cloudstack.target"
readonly WORKLOAD_MANIFEST="${RUNTIME_ROOT}/workloads"

PURGE_CONFIG=false

log() {
    printf '[cloudstack] %s\n' "$*"
}

fail() {
    printf '[cloudstack] ERROR: %s\n' "$*" >&2
    exit 1
}

usage() {
    cat <<'EOF'
Usage: uninstall-stack.sh [--purge-config]

Persistent Podman volumes, secrets and /var/lib/cloudstack are preserved.
EOF
}

require_root() {
    [[ "${EUID}" -eq 0 ]] || fail "Run this uninstaller as root."
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --purge-config)
                PURGE_CONFIG=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                fail "Unknown argument: $1"
                ;;
        esac
    done
}

main() {
    parse_args "$@"
    require_root

    log "Stopping Cloud Stack..."
    systemctl disable --now cloudstack.target >/dev/null 2>&1 || true

    if [[ -f "${WORKLOAD_MANIFEST}" ]]; then
        while IFS= read -r unit; do
            [[ -n "${unit}" ]] || continue

            rm -f "/etc/systemd/system/${unit}.d/10-cloudstack.conf"
            rmdir "/etc/systemd/system/${unit}.d" 2>/dev/null || true
        done < "${WORKLOAD_MANIFEST}"
    fi

    log "Removing installed Quadlet definitions..."
    rm -rf "${QUADLET_ROOT}"
    rm -f "${TARGET_FILE}"
    rm -rf "${RUNTIME_ROOT}"

    if ${PURGE_CONFIG}; then
        log "Removing installed module configuration..."
        rm -rf "${CONFIG_ROOT}"
    else
        log "Configuration preserved: ${CONFIG_ROOT}"
    fi

    systemctl daemon-reload
    systemctl reset-failed >/dev/null 2>&1 || true

    podman network rm cloudstack-edge >/dev/null 2>&1 || true
    podman network rm cloudstack-data >/dev/null 2>&1 || true

    printf '\n'
    log "Cloud Stack uninstalled."
    printf 'Persistent Podman volumes, secrets and /var/lib/cloudstack were NOT deleted.\n'
}

main "$@"
