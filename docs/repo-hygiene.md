# Repository Hygiene

To share source snapshots safely, export a **clean archive** that excludes `.git` metadata.

## Why

- Prevent leaking commit history/metadata when sharing ZIP bundles.
- Avoid unnecessarily large archives with local caches and VCS internals.

## How

Use the helper script:

```bash
bash scripts/export-clean-repo.sh
```

Optional custom output path:

```bash
bash scripts/export-clean-repo.sh /tmp/vidhi-clean.zip
```

This script uses `git archive`, which automatically excludes `.git` internals.
