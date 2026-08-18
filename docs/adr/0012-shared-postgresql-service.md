# ADR-0012: Shared PostgreSQL service

Status: Accepted

## Decision

Cloud Stack uses one shared PostgreSQL service by default.

Applications use separate databases and roles on the shared PostgreSQL cluster.

PostgreSQL is reachable only through `cloudstack-data` and does not publish a host port.

## Consequences

- Backup, recovery and monitoring are centralized.
- Application data remains separated by database roles and permissions.
- PostgreSQL maintenance affects all applications using the shared service.
