# Skill: lean-test
Testes cirúrgicos só para caminhos novos/alterados do diff. Sem `test-planner`, sem plano de testes em arquivo.

## Escopo
1. `git diff --name-only HEAD` + `git ls-files --others --exclude-standard` → arquivos de código alterados.
2. Para cada função/branch nova ou alterada: 1 happy path + 1–2 edge cases críticos (null/vazio, limite, erro esperado, permissão negada).
3. Código não tocado → não testar. Refactor puro com teste existente passando → não adicionar teste.

## Regras
- Colocar teste junto do padrão do repo (`*.spec.ts`, `*.test.tsx`, `tests/test_*.py`).
- Reusar fixtures/factories existentes. Fixture nova ≤ 15 linhas.
- Mock só na fronteira (HTTP, DB, fila, relógio, FS). Nunca mockar a unidade testada.
- Asserções de comportamento observável; sem snapshot de árvore inteira.
- Nome do teste = comportamento: `retorna 404 quando pedido não existe`.
- Teste determinístico: sem sleep, sem rede real, seed fixa.

## Fim
`bash ~/.hx/scripts/gate.sh` (roda só testes relacionados ao diff).
