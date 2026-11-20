# Skill: systematic-debugging
Causa raiz antes de editar. Zero `.md`.

## Passos
1. **Sintoma exato**: mensagem de erro, stack, input, ambiente. Sem paráfrase.
2. **Reprodução mínima**: comando/teste único que falha de forma determinística. Sem repro → coletar mais sinal (log temporário), não editar.
3. **Hipóteses**: listar 3–5 causas possíveis; reduzir às 2 mais prováveis com evidência (Context Pack, git log -L, blame do trecho).
4. **Provar**: log/assert temporário ou teste que confirme UMA hipótese. Só então editar.
5. **Fix mínimo** na causa, não no sintoma. Teste de regressão que falhava antes e passa depois.
6. Remover logs temporários. `bash ~/.hx/scripts/gate.sh`.

## Regra dos 3 strikes
3 tentativas de fix sem sucesso → PARE. Reporte (≤ 10 linhas): sintoma, hipóteses descartadas + evidência, próxima suspeita, o que falta saber.

## Proibido
- Editar "pra ver se resolve" sem hipótese.
- Silenciar erro (`try/catch` vazio, `skip` de teste, `any`, `# type: ignore`) como fix.
- Criar arquivo de análise/plano.
