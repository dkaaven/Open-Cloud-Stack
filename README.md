# Open Cloud Stack

Cloud Stack is a modular, reproducible, Podman-based application platform for small and medium businesses.

It provides an open-source alternative to common Microsoft 365 cloud capabilities, including collaboration, identity, endpoint management, security, mail, storage and office productivity.

## Architecture

Cloud Stack is built around:

- **Modules** — deployable capabilities
- **Profiles** — collections of modules
- **Podman** — container runtime
- **Quadlet** — container and resource definitions
- **systemd** — service lifecycle

Kubernetes is not required. Components should remain Kubernetes-portable where practical.

## Principles

- Modular
- Reproducible
- Secure by default
- Standards based
- Recoverable
- Open source where practical
- Simple to operate

## Installation

Cloud Stack currently targets **Debian 13 (Trixie)**.

Run as root:

```bash
apt-get update && apt-get install -y curl ca-certificates

curl -fsSL   https://raw.githubusercontent.com/dkaaven/Open-Cloud-Stack/main/runtime/bootstrap.sh   | bash
```

The bootstrap installs the Podman runtime, downloads Cloud Stack and installs the default `core` profile.

### Proxmox LXC

Recommended baseline:

```text
unprivileged=1
features=nesting=1,keyctl=1
```

## Compliance

The platform is designed to be auditable, recoverable and suitable for organisations working toward ISO 27001 and NIS2 requirements.

Cloud Stack itself is not a compliance certification. It provides technical controls, configuration and operational evidence that can support compliance.

## Documentation

Technical documentation is available in [`docs/`](docs/).

Architectural decisions are recorded in [`docs/adr/`](docs/adr/).

## Status

Cloud Stack is under active development.
