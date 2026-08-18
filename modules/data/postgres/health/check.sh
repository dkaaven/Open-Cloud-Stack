#!/usr/bin/env bash
set -Eeuo pipefail

podman exec cloudstack-data-postgres     pg_isready -U postgres -d postgres
