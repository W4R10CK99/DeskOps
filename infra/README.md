# Local infrastructure

`compose.yaml` runs PostgreSQL for development with a named volume, configurable credentials/port, and a `pg_isready` health check. Configuration values are placeholders in the repository-root `.env.example`; copy it to ignored `.env` before starting Compose.

From the repository root:

```powershell
Copy-Item .env.example .env
docker compose --env-file .env -f infra/compose.yaml up -d
docker compose --env-file .env -f infra/compose.yaml ps
docker compose --env-file .env -f infra/compose.yaml logs postgres
docker compose --env-file .env -f infra/compose.yaml down
```

`down` preserves the named database volume. `down -v` permanently removes local database data. The API and PostgreSQL remain separate processes; Alembic owns schema creation and upgrades.
