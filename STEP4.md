# Step 4 apply note

Copy this package over the repository.

The following existing directories satisfy the recovery contract:

```text
modules/data/postgres/backup/
modules/workplace/nextcloud/backup/
```

Valkey and Traefik declare persistent but disposable state, so no backup requirement is added.

Run:

```bash
uv run pytest
```
