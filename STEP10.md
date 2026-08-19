# Step 10: Profile-driven installer

## Apply

```bash
rsync -av ~/Downloads/cloudstack-runtime-step10-profile-installer/ ./
uv run pytest
```

## Clean host

After pushing the changes to GitHub, the clean Debian 13 install path becomes:

```bash
apt-get update && apt-get install -y curl ca-certificates

curl -fsSL   https://raw.githubusercontent.com/dkaaven/Open-Cloud-Stack/main/runtime/bootstrap.sh   | bash
```

The bootstrap installs the default `core` profile.

To install a different profile from an existing checkout:

```bash
./runtime/install-stack.sh --profile workplace
```

Profiles that require secrets will fail until the required secret files exist under:

```text
/etc/cloudstack/secrets/
```
