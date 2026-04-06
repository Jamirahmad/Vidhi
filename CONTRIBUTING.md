# Contributing to Vidhi

Thanks for contributing to Vidhi.

## Development workflow

1. Create a feature branch from `main`.
2. Make focused, small commits.
3. Run local quality checks before opening a PR.
4. Open a PR with clear summary, motivation, and test evidence.

## Local setup

```bash
cp .env.example .env
npm install
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

## Required checks

Run these before every PR:

```bash
npm run lint:py
python -m pytest -q
npm run version:check
npm run secrets:scan
```

If working on frontend/contracts, also run:

```bash
npm run lint
npm --prefix frontend run test
npm --prefix packages/contracts run test
```

## Pull request guidelines

- Keep PRs scoped to one item or capability.
- Include test output and any known limitations.
- Update documentation for behavior/config/API changes.
- Do not commit secrets or credentials.

## Coding standards

- Python: Ruff + Black conventions (see `pyproject.toml`).
- TypeScript: strict Zod schema contracts for API/shared types.
- Prefer explicit validation over permissive parsing.

## Security and safety

- Follow `docs/secrets-management.md` for secret handling.
- Follow `docs/prompt-strategy.md` for prompt safety and output guardrails.
