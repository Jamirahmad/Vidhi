# Secrets Management

Vidhi uses **environment variables only** for secrets and sensitive runtime configuration.

## Rules

1. Do not hardcode API keys, tokens, passwords, or credentials in source code.
2. Use `.env` locally (never commit `.env` to git).
3. Use `.env.example` for placeholders/default documentation only.
4. Use CI/CD secret stores (GitHub Actions Secrets, cloud secret manager, vault) in deployed environments.

## Required secret variables

- `OPENROUTER_API_KEY`
- `SEARCHAPI_API_KEY` (if web search is enabled)

## Automated protection

- Secret scanning is available via:

```bash
npm run secrets:scan
```

- CI runs the same command during lint checks.

## Rotation guidance

- Rotate secrets immediately if exposed.
- Update deployment environment variables and restart services.
- Never post plaintext secrets in PR comments, issues, logs, or docs.
