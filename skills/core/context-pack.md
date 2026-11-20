# Skill: context-pack
Protocolo de coleta de contexto mínimo. Saída ≤ 30 linhas.

## Ordem fixa
1. **Graphify**: consultar símbolo/arquivo/feature do pedido → nós relevantes, deps diretas (1 salto), chamadores. Parar quando achar o ponto de mudança.
2. **ai-memory**: 1–3 queries (módulo, feature, termo do erro). Extrair só gotchas/decisões aplicáveis. Nunca listar ou ler o vault inteiro do Obsidian.
3. **Leitura cirúrgica**: ranges exatos dos arquivos apontados. > 400 linhas → só range. Máx. ~8 arquivos.

## Fallback (Graphify ou ai-memory indisponível)
- Escopo: diretório do módulo alvo. `rg -n "<símbolo>" <dir-do-módulo>`; nunca o repo inteiro sem `-g`/dir.
- Chamadores: `rg -n "<símbolo>\(" <dir-pai> -g '!**/node_modules/**'`.
- Memória: `rg -i "<termo>" ~/.hx/fallback-memory.jsonl` (JSONL: `{"repo","area","fact","date"}`).

## Saída
```
STACK: ...
OBJETIVO: ...
ARQUIVOS:
- path:Lx-Ly — motivo
DEPS: ...
GOTCHAS: ...
TESTES: ...
ACEITE:
- ...
RISCO: ...
```
Proibido: colar código, criar `.md`, sugerir arquitetura nova.
