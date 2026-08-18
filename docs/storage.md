# Storage and recovery

Persistent state is declared in `module.yaml`.

Example:

```yaml
storage:
  - id: data
    backup: true
```

## Rules

- `stateful: true` requires persistent storage.
- `stateful: false` requires `storage: []`.
- `backup: true` means the storage must be included in backup and restore operations.
- `backup: false` means the storage may be recreated or discarded.
- Storage implementation is defined separately.
