# Step 10.2: Aardvark DNS runtime dependency

Live testing showed that Podman networking worked without `aardvark-dns`,
but container shutdown could fail during Netavark cleanup.

Cloud Stack therefore installs `aardvark-dns` explicitly instead of relying
on Debian package recommendations.

## Apply

From the repository root:

```bash
rsync -av ~/Downloads/cloudstack-runtime-step10-2-aardvark/ ./
./apply-step10-2.sh
rm apply-step10-2.sh

uv run pytest
```

Then commit:

```bash
git add .
git commit -m "fix: install aardvark dns runtime dependency"
git push
```

## Demo host

After pushing:

```bash
cd /opt/open-cloud-stack
git pull

./runtime/install-podman.sh
```

Verify:

```bash
dpkg -l aardvark-dns
```

Existing Cloud Stack workloads do not need to be reinstalled just for this
package change.
