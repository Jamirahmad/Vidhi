# Versioning Strategy

This repository uses **Semantic Versioning 2.0.0** with release tags in the format `vMAJOR.MINOR.PATCH`.

## Source of truth

- Root `VERSION` file is the canonical release version.
- Root `package.json` `version` must match `VERSION`.
- Backend API exposes this version via:
  - OpenAPI app version (`FastAPI(..., version=...)`)
  - `GET /api/v1/health` as `appVersion`

## SemVer policy

- **MAJOR** (`X.0.0`): breaking API/contract changes.
- **MINOR** (`0.X.0`): backward-compatible features.
- **PATCH** (`0.0.X`): backward-compatible fixes and internal hardening.

Pre-release and build metadata are allowed (`1.2.0-rc.1`, `1.2.0+build.4`).

## Required checks

Validate versioning consistency locally and in CI:

```bash
npm run version:check
```

This validates:
- `VERSION` exists,
- `VERSION` follows SemVer,
- `package.json` version matches `VERSION`.

## Release workflow

1. Update `VERSION` and changelog/release notes.
2. Run quality gates (`lint`, `test`, `version:check`).
3. Create annotated tag from current commit:

```bash
npm run release:tag
```

4. Push commit and tag:

```bash
git push origin <branch>
git push origin v<version>
```
