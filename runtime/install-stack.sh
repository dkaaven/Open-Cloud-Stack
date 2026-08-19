#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

readonly SCRIPT_DIR
readonly REPO_ROOT
readonly RESOLVER="${SCRIPT_DIR}/lib/resolve.py"

readonly QUADLET_ROOT="/etc/containers/systemd/cloudstack"
readonly CONFIG_ROOT="/etc/cloudstack/modules"
readonly SECRETS_ROOT="/etc/cloudstack/secrets"
readonly RUNTIME_ROOT="/etc/cloudstack/runtime"

readonly TARGET_FILE="/etc/systemd/system/cloudstack.target"
readonly PROFILE_FILE="${RUNTIME_ROOT}/profile"
readonly MODULE_MANIFEST="${RUNTIME_ROOT}/modules"
readonly UNIT_MANIFEST="${RUNTIME_ROOT}/units"
readonly WORKLOAD_MANIFEST="${RUNTIME_ROOT}/workloads"

PROFILE="core"
START_STACK=true

log() {
    printf '[cloudstack] %s\n' "$*"
}

fail() {
    printf '[cloudstack] ERROR: %s\n' "$*" >&2
    exit 1
}

usage() {
    cat <<'EOF'
Usage: install-stack.sh [--profile <profile>] [--no-start]

Options:
  --profile <profile>  Profile to install. Default: core
  --no-start           Install and validate without enabling/starting the stack
EOF
}

require_root() {
    [[ "${EUID}" -eq 0 ]] || fail "Run this installer as root."
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --profile)
                [[ $# -ge 2 ]] || fail "--profile requires a value."
                PROFILE="$2"
                shift 2
                ;;
            --no-start)
                START_STACK=false
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

quadlet_to_unit() {
    local file
    file="$(basename "$1")"

    case "${file}" in
        *.container)
            printf '%s\n' "${file%.container}.service"
            ;;
        *.pod)
            printf '%s\n' "${file%.pod}-pod.service"
            ;;
        *.network)
            printf '%s\n' "${file%.network}-network.service"
            ;;
        *.volume)
            printf '%s\n' "${file%.volume}-volume.service"
            ;;
        *)
            return 1
            ;;
    esac
}

resolve_modules() {
    local output

    output="$(python3 "${RESOLVER}" \
        --repo "${REPO_ROOT}" \
        --profile "${PROFILE}")" || exit $?

    [[ -n "${output}" ]] || fail "Profile '${PROFILE}' resolves to no modules."

    printf '%s\n' "${output}"
}

resolve_secrets() {
    python3 "${RESOLVER}" \
        --repo "${REPO_ROOT}" \
        --profile "${PROFILE}" \
        --secrets
}

prepare_secrets() {
    local secret

    while IFS= read -r secret; do
        [[ -n "${secret}" ]] || continue

        local source="${SECRETS_ROOT}/${secret}"

        [[ -f "${source}" ]] || {
            fail "Required secret is missing: ${source}"
        }

        if podman secret inspect "${secret}" >/dev/null 2>&1; then
            log "Podman secret already exists: ${secret}"
        else
            log "Creating Podman secret: ${secret}"
            podman secret create "${secret}" "${source}" >/dev/null
        fi
    done < <(resolve_secrets)
}

remove_old_workload_dropins() {
    [[ -f "${WORKLOAD_MANIFEST}" ]] || return 0

    while IFS= read -r unit; do
        [[ -n "${unit}" ]] || continue

        rm -f "/etc/systemd/system/${unit}.d/10-cloudstack.conf"
        rmdir "/etc/systemd/system/${unit}.d" 2>/dev/null || true
    done < "${WORKLOAD_MANIFEST}"
}

install_module() {
    local module_id="$1"
    local module_dir="${REPO_ROOT}/modules/${module_id}"
    local module_config="${CONFIG_ROOT}/${module_id}"

    [[ -d "${module_dir}" ]] || fail "Module directory not found: ${module_id}"

    log "Installing module: ${module_id}"

    install -d -m 0755 "${module_config}"

    install -m 0644 \
        "${module_dir}/module.yaml" \
        "${module_config}/module.yaml"

    if [[ -d "${module_dir}/config" ]]; then
        rm -rf "${module_config}/config"
        install -d -m 0755 "${module_config}/config"
        cp -a "${module_dir}/config/." "${module_config}/config/"
        chown -R root:root "${module_config}/config"
    fi

    if [[ -d "${module_dir}/quadlet" ]]; then
        while IFS= read -r -d '' file; do
            local filename
            local destination
            local unit

            filename="$(basename "${file}")"
            destination="${QUADLET_ROOT}/${filename}"

            [[ ! -e "${destination}" ]] || \
                fail "Duplicate Quadlet filename: ${filename}"

            install -m 0644 "${file}" "${destination}"

            unit="$(quadlet_to_unit "${file}")" || continue
            printf '%s\n' "${unit}" >> "${TMP_UNITS}"

            case "${file}" in
                *.container|*.pod)
                    printf '%s\n' "${unit}" >> "${TMP_WORKLOADS}"
                    ;;
            esac
        done < <(
            find "${module_dir}/quadlet" \
                -maxdepth 1 \
                -type f \
                \( \
                    -name '*.container' -o \
                    -name '*.pod' -o \
                    -name '*.network' -o \
                    -name '*.volume' \
                \) \
                -print0
        )
    fi

    if [[ -d "${module_dir}/dropins" ]]; then
        cp -a "${module_dir}/dropins/." "${QUADLET_ROOT}/"
        chown -R root:root "${QUADLET_ROOT}"
    fi
}

generate_target() {
    {
        printf '[Unit]\n'
        printf 'Description=Open Cloud Stack\n'
        printf 'Documentation=https://github.com/dkaaven/Open-Cloud-Stack\n'
        printf 'Wants=network-online.target\n'
        printf 'After=network-online.target\n'

        while IFS= read -r unit; do
            [[ -n "${unit}" ]] && printf 'Wants=%s\n' "${unit}"
        done < "${UNIT_MANIFEST}"

        printf '\n[Install]\n'
        printf 'WantedBy=multi-user.target\n'
    } > "${TARGET_FILE}"
}

install_workload_dropins() {
    while IFS= read -r unit; do
        [[ -n "${unit}" ]] || continue

        install -d -m 0755 "/etc/systemd/system/${unit}.d"

        cat > "/etc/systemd/system/${unit}.d/10-cloudstack.conf" <<EOF
[Unit]
PartOf=cloudstack.target
EOF
    done < "${WORKLOAD_MANIFEST}"
}

validate_units() {
    local failed=0
    local unit

    log "Checking generated Quadlet units..."

    while IFS= read -r unit; do
        [[ -n "${unit}" ]] || continue

        if systemctl cat "${unit}" >/dev/null 2>&1; then
            printf '  ✓ %s\n' "${unit}"
        else
            printf '  ✗ %s\n' "${unit}"
            failed=1
        fi
    done < "${UNIT_MANIFEST}"

    (( failed == 0 )) || fail "One or more Quadlets failed to generate."
}

main() {
    parse_args "$@"
    require_root

    command -v podman >/dev/null || fail "Podman is not installed."
    command -v systemctl >/dev/null || fail "systemd is required."
    command -v python3 >/dev/null || fail "Python 3 is required."

    [[ -x "${RESOLVER}" ]] || fail "Resolver not found: ${RESOLVER}"

    local resolved
    resolved="$(resolve_modules)"

    mapfile -t modules <<< "${resolved}"

    log "Installing profile: ${PROFILE}"
    log "Repository: ${REPO_ROOT}"

    if systemctl cat cloudstack.target >/dev/null 2>&1; then
        log "Stopping existing Cloud Stack target..."
        systemctl disable --now cloudstack.target >/dev/null 2>&1 || true
    fi

    remove_old_workload_dropins

    rm -rf "${QUADLET_ROOT}"
    install -d -m 0755 \
        "${QUADLET_ROOT}" \
        "${CONFIG_ROOT}" \
        "${RUNTIME_ROOT}" \
        "${SECRETS_ROOT}"

    TMP_UNITS="$(mktemp)"
    TMP_WORKLOADS="$(mktemp)"
    readonly TMP_UNITS TMP_WORKLOADS
    trap 'rm -f "${TMP_UNITS:-}" "${TMP_WORKLOADS:-}"' EXIT

    : > "${MODULE_MANIFEST}"

    local module_id
    for module_id in "${modules[@]}"; do
        printf '%s\n' "${module_id}" >> "${MODULE_MANIFEST}"
        install_module "${module_id}"
    done

    prepare_secrets

    sort -u "${TMP_UNITS}" > "${UNIT_MANIFEST}"
    sort -u "${TMP_WORKLOADS}" > "${WORKLOAD_MANIFEST}"
    printf '%s\n' "${PROFILE}" > "${PROFILE_FILE}"

    generate_target
    install_workload_dropins

    log "Reloading systemd..."
    systemctl daemon-reload

    validate_units

    if ${START_STACK}; then
        log "Enabling and starting Cloud Stack..."
        systemctl enable --now cloudstack.target
    fi

    printf '\n'
    log "Cloud Stack installed."
    printf 'Profile: %s\n' "${PROFILE}"
    printf '\n'
    printf 'Status:\n'
    printf '  %s/status.sh\n' "${SCRIPT_DIR}"
}

main "$@"
