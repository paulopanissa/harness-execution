# Contribuindo com o HX

Valeu pelo interesse. O HX é mantido por uma pessoa só, então esta página deixa as expectativas claras antes de você escrever código.

[English](../CONTRIBUTING.md)

## Como as decisões são tomadas

- Todo pull request é revisado e mergeado pelo mantenedor ([CODEOWNERS](../.github/CODEOWNERS)). Ninguém mais faz merge.
- Um PR pode estar correto e mesmo assim ser recusado se não combinar com a direção do projeto. Você recebe o motivo.
- Para qualquer coisa maior que correção de bug, **abra uma issue antes** e espere o ok. Economiza seu trabalho.

## O que combina com o HX

O HX existe para manter as sessões de agente baratas e previsíveis. Uma mudança combina quando:

1. **Não aumenta o contexto sempre carregado** sem um motivo forte. `AGENTS.md` e as descrições de agentes e comandos são pagos em todo turno. Skills e corpos de comando carregam sob demanda; prefira eles.
2. **Não exige configuração por projeto.** O `/hx` tem que continuar funcionando em qualquer repositório só com os arquivos globais.
3. **Mantém a stack mínima:** Python só com stdlib, hooks em bash puro, nenhuma chamada de rede em runtime além do `git`.
4. **Garante regras por código quando possível** (hooks, gate) em vez de mais texto no prompt.
5. **Fica neutra em relação a empresas.** Fluxo corporativo vai num preset org privado, nunca neste repositório.

Provavelmente recusado: novas regras sempre ativas, dependências pesadas, telemetria, recursos amarrados a uma empresa ou a um setup pessoal.

## Fluxo

```bash
gh repo fork paulopanissa/harness-execution --clone
cd harness-execution
git switch -c fix/descricao-curta
python3 -m unittest discover -s tests -t tests   # tem que passar
```

- Os testes rodam num sandbox (`HX_HOME`, Claude e Codex próprios). Nunca tocam na sua instalação real.
- As regras ficam em inglês na raiz e em português em `i18n/pt-BR/`. Altere os dois, ou diga no PR por que não. A suíte confere se os dois conjuntos têm os mesmos arquivos e frontmatter.
- Ao mexer em regras, mostre o impacto em tokens com `python3 scripts/measure.py baseline --lang all` (antes/depois).
- Commits seguem [Conventional Commits](https://www.conventionalcommits.org/): `feat|fix|refactor|chore|docs|test|perf|ci`.
- Um assunto por PR. PR pequeno é revisado primeiro.
- O CI (Ubuntu + Windows) precisa estar verde antes da revisão.

## Reportando bugs

Use os templates de issue. Tire tokens, URLs internas, nomes de empresa e caminhos pessoais dos logs antes de postar.

## Segurança

Não abra issue pública para vulnerabilidade. Veja o [SECURITY.md](../SECURITY.md).

## Licença

Ao contribuir, você concorda que sua contribuição fica sob a [Licença MIT](../LICENSE).
