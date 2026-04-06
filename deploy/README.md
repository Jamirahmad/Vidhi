# Deployment Scripts

This folder contains baseline deployment helpers for local/containerized environments.

## Scripts

- `deploy.sh` — build and start services using `docker compose up -d --build`
- `teardown.sh` — stop services and remove compose resources
- `healthcheck.sh` — probe backend health endpoint (`/api/v1/health`)

## Usage

```bash
bash deploy/deploy.sh
bash deploy/healthcheck.sh
bash deploy/teardown.sh
```

Optional:

```bash
BACKEND_URL=http://localhost:8000/api/v1/health bash deploy/healthcheck.sh
```
