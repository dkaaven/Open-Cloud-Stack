# Step 7: Traefik runtime

Traefik v3.7.10 is pinned to the multi-platform image digest:

```text
docker.io/library/traefik@sha256:9c3b91d5fb7770853ca5c1124a23c34bf2d9b47ffaebeab2614cbaf410dcb2ac
```

## Apply

```bash
rsync -av ~/Downloads/cloudstack-runtime-step7-traefik/ ./
uv run pytest
```

## Validate Quadlet generation

```bash
tmp="$(mktemp -d)"

cp modules/core/network/quadlet/cloudstack-edge.network "$tmp/"
cp modules/core/traefik/quadlet/cloudstack-core-traefik.container "$tmp/"

QUADLET_UNIT_DIRS="$tmp" /usr/lib/systemd/system-generators/podman-system-generator --dryrun

rm -rf "$tmp"
```

## Install on the demo host

Prepare configuration:

```bash
sudo install -d -m 0755 /etc/cloudstack/traefik/dynamic
sudo install -m 0644   modules/core/traefik/config/traefik.yaml   /etc/cloudstack/traefik/traefik.yaml
```

Install Quadlets:

```bash
sudo install -m 0644   modules/core/network/quadlet/cloudstack-edge.network   /etc/containers/systemd/cloudstack-edge.network

sudo install -m 0644   modules/core/traefik/quadlet/cloudstack-core-traefik.container   /etc/containers/systemd/cloudstack-core-traefik.container
```

Reload and start:

```bash
sudo systemctl daemon-reload
sudo systemctl start cloudstack-core-traefik.service
```

Check:

```bash
sudo systemctl status cloudstack-core-traefik.service
sudo podman ps
sudo podman inspect   --format '{{.State.Health.Status}}'   cloudstack-core-traefik
curl -I http://127.0.0.1/
```

A `404` from the HTTP request is expected until a dynamic route is installed.

NetBird may point a domain/tunnel to host port 80. No HTTP-to-HTTPS redirect is enabled by default, so upstream TLS termination is supported.
