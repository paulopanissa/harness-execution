---
description: Debug sistemático — causa raiz, fix mínimo, gate
argument-hint: <erro | stack trace | comportamento>
---
Erro: $ARGUMENTS

1. Ler `~/.hx/skills/core/systematic-debugging.md` e seguir.
2. `explorer` com o erro → Context Pack focado no ponto de falha (stack trace, arquivos, gotchas do ai-memory).
3. Reprodução mínima (comando/teste que falha). Sem repro → coletar sinal, não editar.
4. Hipóteses (3–5 → 2) com evidência; provar uma.
5. Fix mínimo na causa + teste de regressão (`~/.hx/skills/quality/lean-test.md`), via agente da stack do pack.
6. `bash ~/.hx/scripts/gate.sh` → exit 0 obrigatório.
7. 3 strikes → PARAR e reportar.

Saída (≤ 15 linhas): `CAUSA` · `REPRO` · `FIX (arquivo:linha)` · `TESTE` · `GATE`.
