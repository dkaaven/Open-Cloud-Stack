# Step 5 apply note

Copy this package over the repository.

Rename the existing Nextcloud Quadlet placeholders:

```bash
mv modules/workplace/nextcloud/quadlet/nextcloud.container \
   modules/workplace/nextcloud/quadlet/cloudstack-workplace-nextcloud.container

mv modules/workplace/nextcloud/quadlet/nextcloud-cron.container \
   modules/workplace/nextcloud/quadlet/cloudstack-workplace-nextcloud-cron.container

mv modules/workplace/nextcloud/quadlet/nextcloud-data.volume \
   modules/workplace/nextcloud/quadlet/cloudstack-workplace-nextcloud-data.volume
```

The shared network Quadlets keep their existing names:

```text
cloudstack-edge.network
cloudstack-data.network
```

Current service Quadlets are placeholders, so module `images` remain empty until implementation begins.

Run:

```bash
uv run pytest
```
