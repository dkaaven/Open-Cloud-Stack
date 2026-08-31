#!/usr/bin/env bash
set -Eeuo pipefail

umask 022

readonly CONFIG_ROOT="${CLOUDSTACK_CONFIG_ROOT:-/etc/cloudstack}"

readonly MODULE_CONFIG_ROOT="${CLOUDSTACK_MODULE_CONFIG_ROOT:-${CONFIG_ROOT}/modules/workplace/nextcloud/config}"

readonly TRAEFIK_DYNAMIC_ROOT="${CLOUDSTACK_TRAEFIK_DYNAMIC_ROOT:-${CONFIG_ROOT}/modules/core/traefik/config/dynamic}"

load_config() {
    local file

    for file in \
        "${CONFIG_ROOT}/stack.env" \
        "${CONFIG_ROOT}/customer.env"
    do
        [[ -f "${file}" ]] || continue

        set -a
        # Deployment configuration is root-managed shell environment syntax.
        # shellcheck disable=SC1090
        . "${file}"
        set +a
    done
}

validate() {
    local host="$1"
    local protocol="$2"
    local admin_user="$3"

    [[ "${host}" =~ ^[A-Za-z0-9][A-Za-z0-9.-]*(:[0-9]{1,5})?$ ]] || {
        printf '[cloudstack] ERROR: Invalid Nextcloud host: %s\n' \
            "${host}" >&2
        return 1
    }

    case "${protocol}" in
        http|https)
            ;;
        *)
            printf '[cloudstack] ERROR: Nextcloud protocol must be http or https.\n' >&2
            return 1
            ;;
    esac

    [[ "${admin_user}" =~ ^[A-Za-z0-9_.@-]+$ ]] || {
        printf '[cloudstack] ERROR: Invalid Nextcloud admin user.\n' >&2
        return 1
    }
}

render_runtime_env() {
    local host="$1"
    local protocol="$2"
    local admin_user="$3"
    local tmp

    install -d -m 0755 "${MODULE_CONFIG_ROOT}"

    tmp="$(mktemp)"
    trap 'rm -f "${tmp:-}"' RETURN

    cat > "${tmp}" <<EOF
POSTGRES_HOST=cloudstack-data-postgres
POSTGRES_DB=nextcloud
POSTGRES_USER=nextcloud
POSTGRES_PASSWORD_FILE=/run/secrets/nextcloud-db-password
REDIS_HOST=cloudstack-data-valkey
REDIS_HOST_PORT=6379
REDIS_HOST_PASSWORD_FILE=/run/secrets/valkey-password
NEXTCLOUD_ADMIN_USER=${admin_user}
NEXTCLOUD_ADMIN_PASSWORD_FILE=/run/secrets/nextcloud-admin-password
NEXTCLOUD_TRUSTED_DOMAINS=${host}
TRUSTED_PROXIES=10.0.0.0/8
OVERWRITEHOST=${host}
OVERWRITEPROTOCOL=${protocol}
OVERWRITECLIURL=${protocol}://${host}
EOF

    install -m 0644 \
        "${tmp}" \
        "${MODULE_CONFIG_ROOT}/runtime.env"
}

render_traefik_route() {
    local host="$1"
    local tmp

    install -d -m 0755 "${TRAEFIK_DYNAMIC_ROOT}"

    tmp="$(mktemp)"
    trap 'rm -f "${tmp:-}"' RETURN

    cat > "${tmp}" <<EOF
http:
  routers:
    cloudstack-nextcloud:
      entryPoints:
        - web
      rule: "Host(\`${host}\`)"
      service: cloudstack-nextcloud

  services:
    cloudstack-nextcloud:
      loadBalancer:
        servers:
          - url: "http://cloudstack-workplace-nextcloud:80"
EOF

    install -m 0644 \
        "${tmp}" \
        "${TRAEFIK_DYNAMIC_ROOT}/nextcloud.yaml"
}

main() {
    local mode="${1:---apply}"

    load_config

    local host="${CLOUDSTACK_NEXTCLOUD_HOST:-nextcloud.localhost}"
    local protocol="${CLOUDSTACK_NEXTCLOUD_PROTOCOL:-http}"
    local admin_user="${CLOUDSTACK_NEXTCLOUD_ADMIN_USER:-cloudadmin}"

    validate "${host}" "${protocol}" "${admin_user}"

    case "${mode}" in
        --check)
            printf '[cloudstack] Nextcloud configuration: %s://%s\n' \
                "${protocol}" \
                "${host}"
            ;;
        --apply)
            render_runtime_env \
                "${host}" \
                "${protocol}" \
                "${admin_user}"

            render_traefik_route "${host}"

            printf '[cloudstack] Nextcloud route configured: %s://%s\n' \
                "${protocol}" \
                "${host}"
            ;;
        *)
            printf '[cloudstack] ERROR: Unknown mode: %s\n' "${mode}" >&2
            exit 1
            ;;
    esac
}

main "$@"
