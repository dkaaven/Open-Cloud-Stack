# Operations

Cloud Stack lifecycle is managed through the runtime tooling and systemd.

## Install

Bootstrap a clean Debian 13 host:

```bash
curl -fsSL https://raw.githubusercontent.com/dkaaven/Open-Cloud-Stack/main/runtime/bootstrap.sh | bash
```

The default profile is `core`.

Install another profile:

```bash
./runtime/install-stack.sh --profile workplace
```

## Status

```bash
./runtime/status.sh
```

## Uninstall

```bash
./runtime/uninstall-stack.sh
```

Persistent volumes, secrets and `/var/lib/cloudstack` are preserved.

## Rules

- Runtime operations require root.
- Profiles determine installed modules.
- Dependencies are resolved from `module.yaml`.
- Failed operations return a non-zero exit code.
