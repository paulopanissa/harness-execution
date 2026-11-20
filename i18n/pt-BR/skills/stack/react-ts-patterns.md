# Skill: react-ts-patterns
Ler só em dúvida. Padrão do repo vence esta lista.

## Componentes
- Função + props tipadas (`type Props = {...}`); sem `React.FC` se o repo não usa.
- Componente > ~150 linhas ou com 2+ responsabilidades → extrair subcomponente/hook.
- Composição (children/slots) antes de props booleanas em cascata.
- Keys estáveis (id), nunca índice em lista mutável.

## Hooks
- Estado derivado = calcular no render (ou `useMemo` se caro), não `useEffect` + `setState`.
- `useEffect` só para sincronizar com externo; deps completas; cleanup.
- Lógica reutilizável → hook `useXxx` com retorno tipado.
- `useCallback`/`useMemo` só com motivo (prop de memo, dep de effect, custo real).

## Dados
- Server state: React Query/SWR/Server Components conforme repo; não duplicar em store global.
- Next.js App Router: buscar no server component; client só para interação. Server Actions validam input (zod).
- Loading/erro/vazio sempre tratados.

## Estilo
- Tailwind: tokens do tema; `cn()`/`clsx` para condicionais; sem valor mágico arbitrário se existir token.
- Reusar design system (`components/ui`) antes de criar.

## Forms
- `react-hook-form` + `zod` se o repo usa; mensagens de erro acessíveis (`aria-describedby`).

## Segurança/A11y
- Sem `dangerouslySetInnerHTML` com dado externo; sem secret em `NEXT_PUBLIC_*`.
- Elementos semânticos, `label`, `alt`, foco visível, navegação por teclado.

## Testes
- Testing Library: `getByRole`/`findByText`, `userEvent`. MSW para HTTP se o repo usa.
