# Skill: react-ts-patterns
Read only when in doubt. The repo's pattern beats this list.

## Components
- Function + typed props (`type Props = {...}`); no `React.FC` if the repo does not use it.
- Component > ~150 lines or with 2+ responsibilities → extract a subcomponent/hook.
- Composition (children/slots) before cascades of boolean props.
- Stable keys (id), never the index in a mutable list.

## Hooks
- Derived state = compute during render (or `useMemo` if expensive), not `useEffect` + `setState`.
- `useEffect` only to sync with something external; complete deps; cleanup.
- Reusable logic → `useXxx` hook with a typed return.
- `useCallback`/`useMemo` only with a reason (memo prop, effect dep, real cost).

## Data
- Server state: React Query/SWR/Server Components per the repo; do not duplicate it in a global store.
- Next.js App Router: fetch in server components; client only for interaction. Server Actions validate input (zod).
- Always handle loading/error/empty.

## Style
- Tailwind: theme tokens; `cn()`/`clsx` for conditionals; no arbitrary magic value when a token exists.
- Reuse the design system (`components/ui`) before creating.

## Forms
- `react-hook-form` + `zod` if the repo uses them; accessible error messages (`aria-describedby`).

## Security/A11y
- No `dangerouslySetInnerHTML` with external data; no secrets in `NEXT_PUBLIC_*`.
- Semantic elements, `label`, `alt`, visible focus, keyboard navigation.

## Tests
- Testing Library: `getByRole`/`findByText`, `userEvent`. MSW for HTTP if the repo uses it.
