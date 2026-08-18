# ADR-0001: Podman, Quadlet and systemd runtime

Status: Accepted

## Decision

Cloud Stack uses Podman as its container runtime.

Containers, networks, volumes and related resources are defined using Quadlet and managed by systemd.

Kubernetes is not required. Components should remain Kubernetes-portable where practical.

## Consequences

- systemd is the service manager and lifecycle authority.
- Quadlet is the native deployment format.
- Docker Compose and Kubernetes manifests are not primary deployment formats.