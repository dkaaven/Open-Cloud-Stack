# Step 12: Valkey

Step 12 adds Valkey to the `platform` profile as the shared cache and
distributed-locking service.

## Apply

```bash
rsync -av ~/Downloads/cloudstack-runtime-step12-valkey/ ./
uv run pytest
```

Then:

```bash
git add .
git commit -m "feat: add valkey data service"
git push
```

## Demo host: kernel prerequisite

```bash
cd /opt/open-cloud-stack
git pull

modules/data/valkey/health/check-host.sh
```

Valkey recommends `vm.overcommit_memory=1`.

If this fails inside an unprivileged Proxmox LXC, do not force the sysctl from
the guest; configure it at the appropriate host level.

## Create the deployment secret

```bash
install -d -m 0700 /etc/cloudstack/secrets
umask 077
openssl rand -hex 32 > /etc/cloudstack/secrets/valkey-password
chmod 0600 /etc/cloudstack/secrets/valkey-password
```

Do not print the secret.

## Install

```bash
./runtime/install-stack.sh --profile platform
./runtime/status.sh
```

## Health and security

```bash
podman inspect   --format '{{.State.Health.Status}}'   cloudstack-data-valkey

podman exec cloudstack-data-valkey id

podman inspect   --format 'configured-user={{.Config.User}}'   cloudstack-data-valkey

podman port cloudstack-data-valkey
```

Expected:

```text
healthy
uid=999(valkey) gid=1000(valkey)
configured-user=999:1000
```

`podman port` should print nothing.

Unauthenticated access:

```bash
podman exec cloudstack-data-valkey valkey-cli ping
```

Expected:

```text
NOAUTH Authentication required.
```

Authenticated access:

```bash
podman exec cloudstack-data-valkey   sh -c 'valkey-cli --no-auth-warning -a "$(cat /run/secrets/valkey-password)" ping'
```

Expected:

```text
PONG
```

## Persistence test

```bash
podman exec cloudstack-data-valkey   sh -c 'valkey-cli --no-auth-warning -a "$(cat /run/secrets/valkey-password)" SET cloudstack:step12 survived'

sleep 2

./runtime/install-stack.sh --profile platform
```

Wait until Valkey is healthy again, then:

```bash
podman exec cloudstack-data-valkey   sh -c 'valkey-cli --no-auth-warning -a "$(cat /run/secrets/valkey-password)" GET cloudstack:step12'
```

Expected:

```text
survived
```

Valkey persistence is intentionally `backup: false`; this proves continuity
across reconciliation, not that Valkey is a backup source.
