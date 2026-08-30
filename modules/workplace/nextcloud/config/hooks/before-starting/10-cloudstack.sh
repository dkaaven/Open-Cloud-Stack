#!/bin/sh
set -eu

occ() {
    php /var/www/html/occ "$@"
}

if [ -n "${NEXTCLOUD_TRUSTED_DOMAINS:-}" ]; then
    occ config:system:set \
        trusted_domains 1 \
        --value="${NEXTCLOUD_TRUSTED_DOMAINS}"
fi

if [ -n "${TRUSTED_PROXIES:-}" ]; then
    occ config:system:set \
        trusted_proxies 0 \
        --value="${TRUSTED_PROXIES}"
fi

if [ -n "${OVERWRITEHOST:-}" ]; then
    occ config:system:set \
        overwritehost \
        --value="${OVERWRITEHOST}"
fi

if [ -n "${OVERWRITEPROTOCOL:-}" ]; then
    occ config:system:set \
        overwriteprotocol \
        --value="${OVERWRITEPROTOCOL}"
fi

if [ -n "${OVERWRITECLIURL:-}" ]; then
    occ config:system:set \
        overwrite.cli.url \
        --value="${OVERWRITECLIURL}"
fi

occ background:cron
