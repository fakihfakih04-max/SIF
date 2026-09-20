# SIF Mobile & Computer — Cloudflare Online Migration

This folder is the safe migration layer for the SIF FastAPI application.

## Important
The existing Windows/local application remains unchanged. Do not deploy the current SQLAlchemy/SQLite backend directly as a Cloudflare Worker.

Cloudflare Workers supports FastAPI through its Python ASGI runtime, and D1 is the managed SQLite-compatible database. The online version must replace the file-based SQLite/SQLAlchemy persistence with D1 bindings before production deployment.

## Current contents
- `wrangler.jsonc` — Worker configuration template.
- `pyproject.toml` — Python Worker dependencies.
- `src/worker.py` — minimal Worker/FastAPI health/static shell used during migration.
- `migrations/0001_schema.sql` — D1 schema matching the current SIF database.
- `migrations/0002_seed_admin.sql` — initial admin seed.

## Deployment order
1. Create the D1 database in Cloudflare.
2. Put its database ID in `wrangler.jsonc`.
3. Apply `0001_schema.sql` and `0002_seed_admin.sql`.
4. Migrate the FastAPI routes from SQLAlchemy sessions to D1 binding calls.
5. Test every existing module before production deployment.

Do not point the production domain at this migration shell until the API migration is complete.
