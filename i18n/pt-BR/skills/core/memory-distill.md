# Skill: memory-distill
Ao fechar a task: extrair 3–5 linhas PERMANENTES. Nada de diário.

## Critério (só entra se TODOS)
- Não é derivável do código/git (`git log`, leitura do arquivo).
- Vale para tasks futuras (gotcha, decisão, restrição, comando não óbvio).
- Cabe em 1 linha (≤ 160 chars), com área/módulo.

## Formato
`[<repo>/<área>] <fato>. Motivo: <por quê>.`
Ex.: `[api/billing] Webhook Stripe exige raw body; não usar json middleware na rota. Motivo: assinatura falha.`

## Destino
1. **ai-memory** (salvar cada linha como memória com tags repo/área).
2. Indisponível → append em `~/.hx/fallback-memory.jsonl`:
   `{"repo":"<repo>","area":"<área>","fact":"<fato>","date":"<YYYY-MM-DD>"}`
3. Obsidian: só via ai-memory; nunca abrir/escrever no vault diretamente.

Nada novo → não salve nada e diga `MEMÓRIA: nada novo`.
