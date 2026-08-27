#!/usr/bin/env bash
set -Eeuo pipefail

umask 022

readonly NETBIRD_KEYRING="/usr/share/keyrings/netbird-archive-keyring.gpg"
readonly NETBIRD_REPO="/etc/apt/sources.list.d/netbird.list"
readonly NETBIRD_KEY_URL="https://pkgs.netbird.io/debian/public.key"

log() {
    printf '[cloudstack] %s\n' "$*"
}

fail() {
    printf '[cloudstack] ERROR: %s\n' "$*" >&2
    exit 1
}

require_root() {
    [[ "${EUID}" -eq 0 ]] || fail "Run this installer as root."
}

install_dependencies() {
    log "Installing NetBird package dependencies..."

    # Remove potentially broken repository state from an interrupted
    # or older installation before running apt update.
    rm -f "${NETBIRD_REPO}"
    rm -f "${NETBIRD_KEYRING}"

    apt-get update

    DEBIAN_FRONTEND=noninteractive \
        apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg
}

install_repository() {
    local tmp_keyring

    log "Installing NetBird APT repository..."

    tmp_keyring="$(mktemp)"
    trap 'rm -f "${tmp_keyring:-}"' EXIT

    curl -fsSL "${NETBIRD_KEY_URL}" \
        | gpg --batch --yes --dearmor \
        > "${tmp_keyring}"

    install -o root -g root -m 0644 \
        "${tmp_keyring}" \
        "${NETBIRD_KEYRING}"

    cat > "${NETBIRD_REPO}" <<EOF
deb [signed-by=${NETBIRD_KEYRING}] https://pkgs.netbird.io/debian stable main
EOF

    chmod 0644 "${NETBIRD_REPO}"

    apt-get update
}

install_netbird() {
    log "Installing NetBird..."

    DEBIAN_FRONTEND=noninteractive \
        apt-get install -y --no-install-recommends netbird
}

verify_installation() {
    command -v netbird >/dev/null || \
        fail "NetBird binary was not installed."

    log "NetBird installed: $(netbird version)"
}

main() {
    require_root
    install_dependencies
    install_repository
    install_netbird
    verify_installation

    log "NetBird installation complete."
}

main "$@"