# Nextcloud

Nextcloud is the first end-user workload in Cloud Stack.

## Image

```text
docker.io/library/nextcloud@sha256:8e5f49801db0cf4659b3089ce1917728023bb8cba7f93731f2abbdfe3a18df0a
```

Human version:

```text
34.0.3-apache
```

The image is pinned by digest.

## Dependencies

Nextcloud requires:

```text
core/network
core/traefik
data/postgres
data/valkey
```

It uses:

- `cloudstack-edge` for HTTP traffic from Traefik;
- `cloudstack-data` for PostgreSQL and Valkey.

No Nextcloud port is published on the host.

## Database

Nextcloud declares:

```text
provision/postgres.yaml
```

Cloud Stack creates:

```text
database: nextcloud
role: nextcloud
```

The application does not use the PostgreSQL superuser.

## Secrets

Required deployment secrets:

```text
nextcloud-db-password
nextcloud-admin-password
```

The Valkey password is inherited through the `data/valkey` dependency.

## Deployment configuration

Defaults:

```text
CLOUDSTACK_NEXTCLOUD_HOST=nextcloud.localhost
CLOUDSTACK_NEXTCLOUD_PROTOCOL=http
CLOUDSTACK_NEXTCLOUD_ADMIN_USER=cloudadmin
```

Override deployment values in:

```text
/etc/cloudstack/customer.env
```

For an upstream TLS terminator such as NetBird, use:

```text
CLOUDSTACK_NEXTCLOUD_PROTOCOL=https
```

Traefik still receives HTTP on the Cloud Stack `web` entrypoint when TLS is
terminated upstream.

## Storage

Nextcloud persists `/var/www/html` in:

```text
cloudstack-workplace-nextcloud-data
```

This includes user files, local configuration, installed apps and instance
secrets.

The storage is backup-required.

## Cron

A separate non-root cron container mounts the same Nextcloud volume and runs
the image-provided cron service.

## Runtime privilege

The official Apache image starts as root because its entrypoint initializes and
updates the persistent application tree and Apache binds its internal port.

Apache/PHP request workers run as `www-data`.

This is currently an explicit application-runtime exception to the preferred
fully non-root container policy. The cron container runs as UID/GID 33 and
drops all capabilities.

## Health

```bash
modules/workplace/nextcloud/health/check.sh
```
