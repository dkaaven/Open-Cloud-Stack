#!/usr/bin/env bash
set -Eeuo pipefail

readonly CLOUDSTACK_ETC="/etc/cloudstack"
readonly CLOUDSTACK_SECRETS="${CLOUDSTACK_ETC}/secrets"
readonly CLOUDSTACK_STATE="/var/lib/cloudstack"
readonly CLOUDSTACK_BACKUPS="${CLOUDSTACK_STATE}/backups"
readonly QUADLET_DIR="/etc/containers/systemd"

log() {
    printf '[cloudstack] %s\n' "$*"
}

warn() {
    printf '[cloudstack] WARNING: %s\n' "$*" >&2
}

die() {
    printf '[cloudstack] ERROR: %s\n' "$*" >&2
    exit 1
}

require_root() {
    [[ "${EUID}" -eq 0 ]] || die "Run this installer as root."
}

load_os_release() {
    [[ -r /etc/os-release ]] || die "/etc/os-release not found."

    # shellcheck disable=SC1091
    source /etc/os-release

    [[ "${ID:-}" == "debian" ]] || \
        die "Unsupported OS: ${ID:-unknown}. Debian 13 is currently required."

    [[ "${VERSION_ID:-}" == "13" ]] || \
        die "Unsupported Debian version: ${VERSION_ID:-unknown}. Debian 13 is currently required."
}

detect_virtualization() {
    VIRT="$(systemd-detect-virt --container 2>/dev/null || true)"

    if [[ "${VIRT}" == "lxc" ]]; then
        log "Detected LXC container."

        if [[ -r /proc/1/uid_map ]]; then
            local host_uid
            host_uid="$(awk 'NR == 1 { print $2 }' /proc/1/uid_map)"

            if [[ "${host_uid}" != "0" ]]; then
                log "Detected unprivileged/user-namespaced LXC."
            else
                warn "LXC appears privileged. Unprivileged LXC is recommended."
            fi
        fi

        log "Proxmox baseline: unprivileged=1, features=nesting=1,keyctl=1"
    elif [[ -n "${VIRT}" && "${VIRT}" != "none" ]]; then
        log "Detected container virtualization: ${VIRT}"
    else
        log "No container virtualization detected."
    fi
}

install_packages() {
    log "Updating APT metadata..."
    export DEBIAN_FRONTEND=noninteractive
    apt-get update

    log "Installing runtime packages..."
    apt-get install -y --no-install-recommends \
        podman \
        crun \
        ca-certificates \
        curl \
        git \
        jq \
        keyutils \
        openssl \
        python3 \
        python3-yaml \
        rsync \
        fuse-overlayfs

    apt-get clean
}

create_layout() {
    log "Creating Cloud Stack filesystem layout..."

    install -d -m 0755 "${CLOUDSTACK_ETC}"
    install -d -m 0700 "${CLOUDSTACK_SECRETS}"

    install -d -m 0755 "${CLOUDSTACK_STATE}"
    install -d -m 0700 "${CLOUDSTACK_BACKUPS}"

    install -d -m 0755 "${QUADLET_DIR}"
}

check_cgroup_v2() {
    local version
    version="$(podman info --format '{{.Host.CgroupsVersion}}' 2>/dev/null || true)"

    [[ "${version}" == "v2" ]] || \
        die "Podman reports cgroup ${version:-unknown}; Quadlet requires cgroup v2."

    log "cgroup v2: OK"
}

check_storage() {
    local driver
    driver="$(podman info --format '{{.Store.GraphDriverName}}' 2>/dev/null || true)"

    [[ -n "${driver}" ]] || die "Unable to determine Podman storage driver."

    log "Podman storage driver: ${driver}"

    if [[ "${driver}" == "vfs" ]]; then
        warn "Podman is using the vfs storage driver. This works but is not recommended for Cloud Stack."
    fi
}

check_quadlet() {
    local generator="/usr/lib/systemd/system-generators/podman-system-generator"

    [[ -x "${generator}" ]] || \
        die "Podman Quadlet generator not found at ${generator}."

    local tmp
    tmp="$(mktemp -d)"
    trap 'rm -rf "${tmp:-}"' RETURN

    cat > "${tmp}/cloudstack-install-test.network" <<'EOF'
[Network]
NetworkName=cloudstack-install-test
Driver=bridge
EOF

    local output
    output="$(
        QUADLET_UNIT_DIRS="${tmp}" \
        "${generator}" --dryrun 2>&1
    )" || {
        printf '%s\n' "${output}" >&2
        die "Quadlet generator validation failed."
    }

    grep -q 'cloudstack-install-test-network.service' <<< "${output}" || \
        die "Quadlet generator did not produce the expected test unit."

    rm -rf "${tmp}"
    trap - RETURN

    log "Quadlet generator: OK"
}

check_podman_resources() {
    log "Testing Podman network creation..."

    podman network rm -f cloudstack-install-test >/dev/null 2>&1 || true
    podman network create cloudstack-install-test >/dev/null || \
        die "Podman could not create a network."

    podman network rm cloudstack-install-test >/dev/null || \
        die "Podman could not remove the test network."

    log "Testing Podman volume creation..."

    podman volume rm -f cloudstack-install-test >/dev/null 2>&1 || true
    podman volume create cloudstack-install-test >/dev/null || \
        die "Podman could not create a volume."

    podman volume rm cloudstack-install-test >/dev/null || \
        die "Podman could not remove the test volume."

    log "Podman network and volume operations: OK"
}

check_keyctl() {
    if keyctl show >/dev/null 2>&1; then
        log "keyctl: OK"
    else
        warn "keyctl is unavailable inside this container."
        warn "For Proxmox unprivileged LXC, enable features=nesting=1,keyctl=1 on the Proxmox host."
    fi
}

show_summary() {
    printf '\n'
    log "Host bootstrap complete."
    printf '\n'
    printf 'OS:                 %s\n' "${PRETTY_NAME}"
    printf 'Virtualization:     %s\n' "${VIRT:-none}"
    printf 'Podman:             %s\n' "$(podman --version)"
    printf 'Podman mode:        %s\n' \
        "$(podman info --format '{{if .Host.Security.Rootless}}rootless{{else}}rootful{{end}}')"
    printf 'Storage driver:     %s\n' "$(podman info --format '{{.Store.GraphDriverName}}')"
    printf 'cgroup:             %s\n' "$(podman info --format '{{.Host.CgroupsVersion}}')"
    printf 'Quadlets:           %s\n' "${QUADLET_DIR}"
    printf 'Configuration:      %s\n' "${CLOUDSTACK_ETC}"
    printf 'Secrets:            %s\n' "${CLOUDSTACK_SECRETS}"
    printf 'Cloud Stack state:  %s\n' "${CLOUDSTACK_STATE}"
    printf 'Backups:            %s\n' "${CLOUDSTACK_BACKUPS}"
    printf '\n'
    log "Ready for Cloud Stack installation."
}

main() {
    require_root
    load_os_release
    detect_virtualization
    install_packages
    create_layout

    log "Validating Podman runtime..."
    podman info >/dev/null

    check_cgroup_v2
    check_storage
    check_quadlet
    check_podman_resources
    check_keyctl

    show_summary
}

main "$@"
