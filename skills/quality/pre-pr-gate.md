# Skill: pre-pr-gate
Gate barato primeiro; IA só se o bash passar.

## Passos
1. `bash ~/.hx/scripts/gate.sh [--base origin/<branch-alvo>]`.
   - `GATE: FAIL` → pare. Mostre as linhas, corrija (máx. 2) ou devolva ao agente da stack. Não chame o `reviewer`.
2. `GATE: PASS` → chamar `reviewer` com: output do gate + critérios de aceite. Ele lê o diff.
   - Lista de erros → corrigir → voltar ao passo 1 (máx. 2 ciclos; depois reportar).
3. `PASS` do reviewer → gerar descrição de PR em exatamente 5 bullets:
```
- **O quê:** <mudança>
- **Por quê:** <motivação/WI>
- **Como:** <abordagem, arquivos-chave>
- **Testes:** <gate PASS + testes adicionados>
- **Risco:** <baixo|médio|alto> — <rollback/impacto>
```
4. Título: conventional commit (`feat(escopo): ...`). Sem menção a IA/Claude/Codex.
5. Não fazer push/abrir PR sem confirmação do usuário.
