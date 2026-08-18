# ADR-0010: Runtime resource naming

Status: Accepted

## Decision

Module-owned runtime resources use:

```text
cloudstack-<category>-<module>[-<role>]
```

Examples:

```text
cloudstack-workplace-nextcloud
cloudstack-workplace-nextcloud-cron
cloudstack-workplace-nextcloud-data
cloudstack-data-postgres
```

Shared platform networks use their established role names:

```text
cloudstack-edge
cloudstack-data
```

Quadlet filenames use the same resource name.

## Consequences

- Runtime resources map predictably to module IDs.
- Naming collisions between categories are avoided.
- Cloud Stack resources are easy to identify.
