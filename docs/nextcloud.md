# Nextcloud

Nextcloud is deployed by the `workplace` profile.

## Deployment configuration

Customer-specific values belong in:

```text
/etc/cloudstack/customer.env
```

Example for local HTTP testing:

```text
CLOUDSTACK_NEXTCLOUD_HOST=nextcloud.localhost
CLOUDSTACK_NEXTCLOUD_PROTOCOL=http
CLOUDSTACK_NEXTCLOUD_ADMIN_USER=cloudadmin
```

Example when TLS is terminated before Traefik:

```text
CLOUDSTACK_NEXTCLOUD_HOST=cloud.example.com
CLOUDSTACK_NEXTCLOUD_PROTOCOL=https
CLOUDSTACK_NEXTCLOUD_ADMIN_USER=cloudadmin
```

The module configuration hook generates:

```text
/etc/cloudstack/modules/workplace/nextcloud/config/runtime.env
/etc/cloudstack/modules/core/traefik/config/dynamic/nextcloud.yaml
```

These generated files are deployment state and are not committed.

## Secrets

Create:

```text
/etc/cloudstack/secrets/nextcloud-db-password
/etc/cloudstack/secrets/nextcloud-admin-password
```

Use long random values.

The admin password is used to create the initial local `cloudadmin` account.
Changing the deployment secret later does not currently rotate the password of
an existing Nextcloud account. Secret rotation will be handled separately.

## Database

The module database contract creates a dedicated:

```text
database: nextcloud
role: nextcloud
```

The role password comes from `nextcloud-db-password`.

## Valkey

Nextcloud uses the shared Valkey service for distributed caching and file
locking.

## Ingress

Nextcloud has no host-published port.

Traefik routes the configured hostname over the `cloudstack-edge` network to:

```text
http://cloudstack-workplace-nextcloud:80
```

## Background jobs

The Nextcloud background-job mode is set to `cron`.

A separate `cloudstack-workplace-nextcloud-cron` container runs the cron
service as UID/GID 33.

## Backup

The Nextcloud volume is marked `backup: true`.

Backup and restore implementation and live recovery validation are handled in
Step 13.2.
