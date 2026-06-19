## Database migration

This project uses Alembic for database schema migrations.

Create the initial tables:

```bash
uv run alembic upgrade head
```

Alembic stores the applied revision in the `alembic_version` table, so running
the same command again does not recreate or overwrite existing tables.

After changing SQLModel table definitions, create a new migration:

```bash
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head
```
