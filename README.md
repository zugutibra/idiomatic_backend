# Idiomatic API

FastAPI backend for the Idiomatic IELTS speaking-idioms app: auth, idiom browsing, Leitner-box spaced-repetition review, quiz mode, and progress stats.

## Local development

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

alembic upgrade head
python -m scripts.seed_idioms

uvicorn app.main:app --reload
```

Defaults to a local SQLite file (`idiomatic.db`) — no external database needed for local dev. Copy `.env.example` to `.env` to override `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`.

Interactive docs: http://localhost:8000/docs

## Tests

```sh
pytest
```

## Deploying to Neon + Render

1. Create a Neon project, copy the **pooled** connection string (Render's free tier can spin up multiple workers, so use the pooled URL, not the direct one).
2. On Render, create a Web Service from this repo:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Env vars: `DATABASE_URL` (Neon pooled URL, with `postgresql://` scheme), `SECRET_KEY` (random secret)
3. Run the migration once against Neon before or right after first deploy:
   ```sh
   DATABASE_URL=<neon-pooled-url> alembic upgrade head
   DATABASE_URL=<neon-pooled-url> python -m scripts.seed_idioms
   ```
4. First request after idle may take ~30-60s (Render free tier cold start) — this is expected, not a bug.
