# Traefik

Provides HTTP and HTTPS ingress for Cloud Stack.

## Network

Traefik joins:

```text
cloudstack-edge
```

Host ports:

```text
80
443
```

HTTP is not redirected to HTTPS by default.

TLS may terminate at Traefik or at an upstream edge such as NetBird.

## Configuration

Installed configuration:

```text
/etc/cloudstack/modules/core/traefik/config/
```

Traefik uses the file provider. The Podman socket is not mounted.

## Health

Health is checked with Traefik's built-in `healthcheck` command.
