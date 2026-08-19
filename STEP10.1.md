# Step 10.1: Runtime resource reconciliation

This step fixes a live-tested lifecycle issue where a Quadlet network service
could remain `active` while the underlying Podman network no longer existed.

## Apply

```bash
rsync -av ~/Downloads/cloudstack-runtime-step10-1-resource-reconciliation/ ./
uv run pytest
```

Then commit and push:

```bash
git add .
git commit -m "fix: reconcile quadlet resources before workloads"
git push
```

## Demo host

```bash
cd /opt/open-cloud-stack
git pull

./runtime/install-stack.sh --profile core
./runtime/status.sh
```

Expected runtime state:

```text
Resources
---------
cloudstack-data-network.service              active
cloudstack-edge-network.service              active

Workloads
---------
cloudstack-core-traefik.service              active
```

The actual Podman networks should also be present:

```bash
podman network ls
```

No manual `systemctl restart` of the network units should be necessary.

## Regression test

Stop the workload target first so Traefik releases the edge network:

```bash
systemctl stop cloudstack.target
podman network rm cloudstack-edge cloudstack-data
./runtime/status.sh
```

This reproduces the previously observed mismatch: the resource services can
still report `active` while the Podman networks are absent.

Re-running:

```bash
./runtime/install-stack.sh --profile core
```

must recreate the resources automatically and start the workload again.
