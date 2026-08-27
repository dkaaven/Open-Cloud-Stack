# Host requirements

Some Cloud Stack modules require host settings that cannot be provided by
container configuration alone.

A module may provide an executable prerequisite check at:

```text
modules/<category>/<module>/health/check-host.sh
```

`install-stack.sh` runs these checks for every module resolved by the selected
profile before modifying the currently installed stack.

If a check fails, installation stops before:

- workloads are stopped;
- configuration is replaced;
- Quadlets are replaced;
- secrets are refreshed.

## Current requirements

| Module | Requirement |
| --- | --- |
| `data/valkey` | `vm.overcommit_memory=1` |

Platform-specific setup belongs under:

```text
docs/platforms/
```
