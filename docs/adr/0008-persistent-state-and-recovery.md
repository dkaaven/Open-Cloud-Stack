# ADR-0008: Persistent state and recovery

Status: Accepted

## Decision

Modules declare persistent storage in `module.yaml`.

Each storage entry declares whether it must be included in backup and restore operations.

Storage implementation is not defined by this contract.

## Consequences

- Stateful modules must declare at least one storage entry.
- Stateless modules must not declare persistent storage.
- Storage marked for backup requires module backup and restore support.
- Recoverable and disposable state are explicitly distinguished.
