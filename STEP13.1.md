# Step 13.1: Nextcloud runtime

Step 13.1 deploys the first end-user Cloud Stack workload.

## Apply

From the repository root:

```bash
rsync -av   ~/Downloads/cloudstack-runtime-step13-1-nextcloud/   ./

./apply-step13-1.py
rm apply-step13-1.py

uv run pytest
```

Then:

```bash
git add .
git commit -m "feat: deploy nextcloud workplace service"
git push
```

## Demo deployment configuration

For the first local test, the defaults work:

```text
CLOUDSTACK_NEXTCLOUD_HOST=nextcloud.localhost
CLOUDSTACK_NEXTCLOUD_PROTOCOL=http
CLOUDSTACK_NEXTCLOUD_ADMIN_USER=cloudadmin
```

To use a real hostname, create or update:

```text
/etc/cloudstack/customer.env
```

For example:

```bash
cat > /etc/cloudstack/customer.env <<'EOF'
CLOUDSTACK_NEXTCLOUD_HOST=nextcloud.example.com
CLOUDSTACK_NEXTCLOUD_PROTOCOL=https
CLOUDSTACK_NEXTCLOUD_ADMIN_USER=cloudadmin
EOF

chmod 0644 /etc/cloudstack/customer.env
```

Use `https` when TLS is terminated upstream, such as by a NetBird reverse
proxy.

## Create Nextcloud secrets

```bash
install -d -m 0700 /etc/cloudstack/secrets

(
    umask 077

    openssl rand -hex 32       > /etc/cloudstack/secrets/nextcloud-db-password

    openssl rand -base64 36       > /etc/cloudstack/secrets/nextcloud-admin-password
)

chmod 0600   /etc/cloudstack/secrets/nextcloud-db-password   /etc/cloudstack/secrets/nextcloud-admin-password
```

Do not print the secrets.

## Install workplace profile

```bash
cd /opt/open-cloud-stack

git fetch origin
git reset --hard origin/main

./runtime/install-stack.sh --profile workplace
./runtime/status.sh
```

Expected modules:

```text
core/network
core/traefik
data/postgres
data/valkey
workplace/nextcloud
```

Expected new resource:

```text
cloudstack-workplace-nextcloud-data-volume.service
```

Expected new workloads:

```text
cloudstack-workplace-nextcloud.service
cloudstack-workplace-nextcloud-cron.service
```

The Nextcloud image is large and the first initialization creates the
application tree and database schema. Health can therefore remain `starting`
for a while.

## Health

```bash
podman inspect   --format '{{.State.Health.Status}}'   cloudstack-workplace-nextcloud
```

Wait for:

```text
healthy
```

Then:

```bash
modules/workplace/nextcloud/health/check.sh
```

## Database isolation

Verify the database and owner:

```bash
podman exec   --user postgres   cloudstack-data-postgres   psql -U postgres -d postgres   -c "\l+ nextcloud"

podman exec   --user postgres   cloudstack-data-postgres   psql -U postgres -d postgres   -c "\du nextcloud"
```

Nextcloud must use the dedicated `nextcloud` role, not `postgres`.

## No host port

```bash
podman port cloudstack-workplace-nextcloud
```

Expected: no output.

Traefik is the ingress path.

## Local routing test

If using the default configuration:

```bash
curl -sS   -H 'Host: nextcloud.localhost'   http://127.0.0.1/status.php
```

The response should be Nextcloud status JSON with `installed` set to `true`.

## Valkey

Check the effective Nextcloud configuration without exposing private values:

```bash
podman exec   --user 33   cloudstack-workplace-nextcloud   php /var/www/html/occ config:list system
```

The configuration should show Redis/Valkey caching and locking enabled.

## Persistence regression

Create a marker file through the Nextcloud volume:

```bash
podman exec   cloudstack-workplace-nextcloud   sh -c 'printf "step13.1\n" > /var/www/html/data/.cloudstack-step13-1'
```

Reconcile:

```bash
./runtime/install-stack.sh --profile workplace
```

Then:

```bash
podman exec   cloudstack-workplace-nextcloud   cat /var/www/html/data/.cloudstack-step13-1
```

Expected:

```text
step13.1
```

Step 13.2 will implement and live-test backup/restore and additional
Nextcloud-specific hardening.
