# Skill: verification-before-completion
Proibido declarar "pronto", "feito", "corrigido" ou "passa" sem evidência fresca.

## Regra
1. Rode `bash ~/.hx/scripts/gate.sh` APÓS a última edição desta rodada.
2. Só conta `exit 0` com saída `GATE: PASS` (ou `GATE: PASS (...)`).
3. Output de rodada anterior, de outro agente ou "deve passar" não conta.
4. `GATE: PASS (nenhum checker aplicável)` → diga explicitamente que não houve verificação automática e liste o teste manual feito.
5. Falhou → não declare pronto. Corrija (máx. 2) ou reporte o FAIL com as linhas do gate.

## Relato final
`GATE: PASS` + lista `arquivo:linha` alterados. Nada de "tudo funcionando" sem o gate.
