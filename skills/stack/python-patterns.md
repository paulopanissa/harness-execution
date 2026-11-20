# Skill: python-patterns
Read only when in doubt. The repo's pattern beats this list.

## Basics
- Full type hints; `X | None`; `collections.abc` for collection types; `TypedDict`/`dataclass(frozen=True)`/Pydantic for structures.
- `pathlib.Path`, f-strings, `logging.getLogger(__name__)`.
- Specific exceptions + message with context; `raise ... from err`.
- Pure functions for rules; I/O at the edges.

## FastAPI
- Routers per domain; separate Pydantic schemas for input (`XCreate`) and output (`XRead`).
- `Depends` for DB session/auth/config. `HTTPException` with the right status.
- `async` route only with async I/O; blocking call → `def` (threadpool) or `run_in_threadpool`.
- Settings with `pydantic-settings`; validate at boot.

## Scripts/automation
- `main() -> int` + `sys.exit(main())`; `argparse`/`typer`.
- Idempotent when possible; `--dry-run` for destructive effects.
- Subprocess with an args list, `check=True`, never `shell=True` with input.

## AI/data pipelines
- Keys from env; client instantiated once.
- Timeout + exponential retry (tenacity if the repo uses it) + concurrency limit.
- Validate model output (Pydantic/JSON schema) before using it.
- Cache expensive embeddings/responses; batches instead of one-by-one.
- Pandas: vectorize; no `iterrows` at volume; explicit dtypes on load.

## Tests
- pytest: small fixtures, `tmp_path`, `monkeypatch`; `respx`/`httpx.MockTransport` for HTTP.
- `pytest.mark.parametrize` for edge cases.
