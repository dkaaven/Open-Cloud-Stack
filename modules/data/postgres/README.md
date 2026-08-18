# PostgreSQL

Shared PostgreSQL service for Cloud Stack applications.

## Network

PostgreSQL joins:

```text
cloudstack-data
```

No host port is published.

## Data

Persistent data is stored in:

```text
cloudstack-data-postgres-data
```

PostgreSQL 18 stores its versioned data directory below `/var/lib/postgresql`; the volume is mounted at that parent path.

## Secrets

Required:

```text
postgres-superuser-password
```

It is exposed to the container as:

```text
/run/secrets/postgres-superuser-password
```

## Applications

Applications should use separate databases and roles on the shared PostgreSQL cluster.

## Health

```bash
health/check.sh
```

## Backup

```bash
backup/backup.sh
```

Backups are logical cluster dumps created with `pg_dumpall`.

## Restore

Restore into an empty or replacement Cloud Stack PostgreSQL cluster:

```bash
backup/restore.sh <dump.sql>
```
