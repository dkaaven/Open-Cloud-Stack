# Runtime resources

## Images

Modules declare deployable images in `module.yaml`.

```yaml
images:
  - id: app
    version: "1.2.3"
    reference: registry.example/app@sha256:<digest>
```

Rules:

- Image references must be immutable digests.
- `latest` is not allowed.
- Image updates are explicit repository changes.

## Naming

Module-owned resources use:

```text
cloudstack-<category>-<module>[-<role>]
```

Quadlet filenames use the same name.

Shared platform networks remain:

```text
cloudstack-edge
cloudstack-data
```
