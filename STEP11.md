# Step 11: PostgreSQL deployment

Step 11 live-tests the existing `data/postgres` module as the first persistent,
secret-backed Cloud Stack workload.

It adds the `platform` profile:

```text
core/network
core/traefik
data/postgres
```

It also strengthens the installer so required secrets are checked before the
currently running stack is stopped.

## Apply

From the repository root:

```bash
rsync -av ~/Downloads/cloudstack-runtime-step11-postgres/ ./
uv run pytest
```

Then:

```bash
git add .
git commit -m "feat: deploy postgres through platform profile"
git push
```

## Demo host: create PostgreSQL secret

```bash
install -d -m 0700 /etc/cloudstack/secrets
umask 077

openssl rand -hex 32   > /etc/cloudstack/secrets/postgres-superuser-password

chmod 0600 /etc/cloudstack/secrets/postgres-superuser-password
```

Do not print the secret.

## Install platform

```bash
cd /opt/open-cloud-stack
git pull

./runtime/install-stack.sh --profile platform
./runtime/status.sh
```

The first image pull and PostgreSQL initialization can take a little time.

Check health:

```bash
podman inspect   --format '{{.State.Health.Status}}'   cloudstack-data-postgres
```

Expected:

```text
healthy
```

Check process identity:

```bash
podman exec cloudstack-data-postgres id

podman inspect   --format 'configured-user={{.Config.User}}'   cloudstack-data-postgres
```

Do not force a `User=` override yet. The official PostgreSQL image performs
initialization before dropping privileges.

## Verify network exposure

```bash
podman port cloudstack-data-postgres
```

Expected: no published host ports.

Verify network membership:

```bash
podman inspect   --format '{{json .NetworkSettings.Networks}}'   cloudstack-data-postgres
```

PostgreSQL should only use `cloudstack-data`.

## Persistence test

Create a test database and row:

```bash
podman exec cloudstack-data-postgres   psql -U postgres -d postgres   -c 'CREATE DATABASE cloudstack_step11;'

podman exec cloudstack-data-postgres   psql -U postgres -d cloudstack_step11   -c 'CREATE TABLE persistence_test (value text NOT NULL);'

podman exec cloudstack-data-postgres   psql -U postgres -d cloudstack_step11   -c "INSERT INTO persistence_test VALUES ('survived');"
```

Reinstall the same desired state:

```bash
./runtime/install-stack.sh --profile platform
```

Wait for PostgreSQL to become healthy, then query:

```bash
podman exec cloudstack-data-postgres   psql -U postgres -d cloudstack_step11   -c 'TABLE persistence_test;'
```

Expected:

```text
 survived
```

## Backup test

Run:

```bash
modules/data/postgres/backup/backup.sh
```

Then:

```bash
ls -lh /var/lib/cloudstack/backups/postgres/
```

Do not perform a destructive restore test against this working database.
