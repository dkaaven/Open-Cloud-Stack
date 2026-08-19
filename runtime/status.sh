#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

STACK_VERSION="unknown"
[[ -f "${ROOT}/VERSION" ]] && STACK_VERSION="$(cat "${ROOT}/VERSION")"

value_or_unknown() {
    local value="$1"
    [[ -n "${value}" ]] && printf '%s' "${value}" || printf 'unknown'
}

service_status() {
    local unit="$1"

    if ! systemctl cat "${unit}" >/dev/null 2>&1; then
        printf 'not installed'
        return
    fi

    systemctl is-active "${unit}" 2>/dev/null || true
}

network_status() {
    local network="$1"

    if podman network exists "${network}" 2>/dev/null; then
        printf 'present'
    else
        printf 'not installed'
    fi
}

printf 'Cloud Stack\n'
printf '===========\n\n'

printf 'Host\n'
printf '%s\n' '----'

if [[ -r /etc/os-release ]]; then
    # shellcheck disable=SC1091
    source /etc/os-release
    printf 'OS:               %s\n' "${PRETTY_NAME:-unknown}"
fi

printf 'Virtualization:   %s\n' \
    "$(systemd-detect-virt --container 2>/dev/null || printf 'none')"

if command -v podman >/dev/null 2>&1; then
    printf 'Podman:           %s\n' "$(podman --version)"
    printf 'Mode:             %s\n' \
        "$(podman info --format '{{if .Host.Security.Rootless}}rootless{{else}}rootful{{end}}')"
    printf 'Storage:          %s\n' \
        "$(podman info --format '{{.Store.GraphDriverName}}')"
    printf 'cgroup:           %s\n' \
        "$(podman info --format '{{.Host.CgroupsVersion}}')"
else
    printf 'Podman:           not installed\n'
fi

printf '\nStack\n'
printf '%s\n' '-----'
printf 'Version:          %s\n' "${STACK_VERSION}"
printf 'Repository:       %s\n' "${ROOT}"
printf 'Configuration:    /etc/cloudstack\n'
printf 'Quadlets:         /etc/containers/systemd\n'
printf 'State:            /var/lib/cloudstack\n'

printf '\nNetworks\n'
printf '%s\n' '--------'
printf '%-24s %s\n' 'cloudstack-edge' "$(network_status cloudstack-edge)"
printf '%-24s %s\n' 'cloudstack-data' "$(network_status cloudstack-data)"

printf '\nServices\n'
printf '%s\n' '--------'
printf '%-34s %s\n' \
    'Edge network' \
    "$(service_status cloudstack-edge-network.service)"

printf '%-34s %s\n' \
    'Data network' \
    "$(service_status cloudstack-data-network.service)"

printf '%-34s %s\n' \
    'Traefik' \
    "$(service_status cloudstack-core-traefik.service)"

printf '%-34s %s\n' \
    'PostgreSQL' \
    "$(service_status cloudstack-data-postgres.service)"

printf '\nContainers\n'
printf '%s\n' '----------'

containers="$(
    podman ps -a \
        --filter 'name=cloudstack-' \
        --format '{{.Names}}\t{{.Status}}' \
        2>/dev/null || true
)"

if [[ -n "${containers}" ]]; then
    printf '%-34s %s\n' 'NAME' 'STATUS'
    printf '%b\n' "${containers}"
else
    printf 'None\n'
fi

printf '\nVolumes\n'
printf '%s\n' '-------'

volumes="$(
    podman volume ls \
        --filter 'name=cloudstack-' \
        --format '{{.Name}}' \
        2>/dev/null || true
)"

if [[ -n "${volumes}" ]]; then
    printf '%s\n' "${volumes}"
else
    printf 'None\n'
fi
