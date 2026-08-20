# PostgreSQL

Cloud Stack provides one shared PostgreSQL cluster through:

```text
data/postgres
```

Applications should use separate PostgreSQL databases and roles rather than
deploying one PostgreSQL server per application.

## Profile

The `platform` profile currently installs:

```text
core/network
core/traefik
data/postgres
```

`core/network` is resolved automatically as a dependency.

## Secret

PostgreSQL requires:

```text
postgres-superuser-password
```

The deployment value is stored outside the repository:

```text
/etc/cloudstack/secrets/postgres-superuser-password
```

Create it before installing the `platform` profile:

```bash
install -d -m 0700 /etc/cloudstack/secrets
umask 077
openssl rand -hex 32 > /etc/cloudstack/secrets/postgres-superuser-password
chmod 0600 /etc/cloudstack/secrets/postgres-superuser-password
```

Cloud Stack checks required secret files before stopping the currently running
stack.

During installation the deployment secret file is synchronized to the Podman
secret store.

## Storage

PostgreSQL uses the named volume:

```text
cloudstack-data-postgres-data
```

The volume is declared as backup-required persistent state in `module.yaml`.

The PostgreSQL 18 container mounts it at:

```text
/var/lib/postgresql
```

## Network

PostgreSQL joins only:

```text
cloudstack-data
```

No PostgreSQL port is published on the host.

## Health

```bash
podman inspect   --format '{{.State.Health.Status}}'   cloudstack-data-postgres
```

Expected:

```text
healthy
```

## Backup

From the repository checkout:

```bash
modules/data/postgres/backup/backup.sh
```

Backups are stored below:

```text
/var/lib/cloudstack/backups/postgres
```

unless the backup script is configured otherwise.

## Restore

Restore is intended for an empty or replacement PostgreSQL cluster.

Do not test restore destructively against a working production database.
