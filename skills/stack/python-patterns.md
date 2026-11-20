# Skill: python-patterns
Ler só em dúvida. Padrão do repo vence esta lista.

## Base
- Type hints completos; `X | None`; `collections.abc` para tipos de coleção; `TypedDict`/`dataclass(frozen=True)`/Pydantic para estruturas.
- `pathlib.Path`, f-strings, `logging.getLogger(__name__)`.
- Exceções específicas + mensagem com contexto; `raise ... from err`.
- Funções puras para regra; I/O nas bordas.

## FastAPI
- Routers por domínio; schemas Pydantic separados de entrada (`XCreate`) e saída (`XRead`).
- `Depends` para DB session/auth/config. `HTTPException` com status correto.
- Rota `async` só com I/O async; chamada bloqueante → `def` (threadpool) ou `run_in_threadpool`.
- Settings com `pydantic-settings`; validar no boot.

## Scripts/automação
- `main() -> int` + `sys.exit(main())`; `argparse`/`typer`.
- Idempotente quando possível; `--dry-run` para efeito destrutivo.
- Subprocess com lista de args, `check=True`, nunca `shell=True` com input.

## Pipelines de IA/dados
- Chaves por env; cliente instanciado uma vez.
- Timeout + retry exponencial (tenacity se o repo usa) + limite de concorrência.
- Validar saída do modelo (Pydantic/JSON schema) antes de usar.
- Cache de embeddings/respostas caras; lotes em vez de 1-a-1.
- Pandas: vetorizar; nada de `iterrows` em volume; dtypes explícitos no load.

## Testes
- pytest: fixtures pequenas, `tmp_path`, `monkeypatch`; `respx`/`httpx.MockTransport` para HTTP.
- `pytest.mark.parametrize` para edge cases.
