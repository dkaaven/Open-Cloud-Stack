# Step 3 apply note

Copy this package over the repository, then remove the obsolete private Nextcloud network:

```bash
rm -f modules/workplace/nextcloud/quadlet/nextcloud.network
```

If `nextcloud.container` references `nextcloud.network`, replace that membership with:

```ini
Network=cloudstack-edge.network
Network=cloudstack-data.network
```

Do not change other container settings.

Run:

```bash
uv run pytest
```
