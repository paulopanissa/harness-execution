# Skill: node-ts-patterns
Ler só em dúvida. Padrão do repo vence esta lista.

## Estrutura (NestJS)
- Módulo por domínio: `controller` (HTTP fino) → `service` (regra) → `repository`/Prisma (dados).
- DTO de entrada com `class-validator` + `ValidationPipe({ whitelist: true, forbidNonWhitelisted: true })`.
- Guards para auth/roles; interceptors para logging/serialização; filtros de exceção globais.
- Config via `ConfigService` + schema validado no boot.

## TypeScript
- `strict: true`. Sem `any` novo → `unknown` + narrowing.
- Retorno explícito em exportadas. `readonly` em props de DTO/entidade.
- Erros de domínio tipados (`class NotFoundError extends DomainError`), mapeados para HTTP no filtro.
- Imutabilidade: spread/`map`, não mutar argumentos.

## Prisma
- `select`/`include` explícitos; nunca devolver entidade crua com campos sensíveis.
- Múltiplas escritas → `prisma.$transaction`. Paginação com `take`/`cursor`.
- N+1: buscar em lote (`where: { id: { in } }`). Raw só `$queryRaw` tagged (nunca `Unsafe` com input).
- Migration nova → revisar `DROP`/`NOT NULL` sem default.

## APIs
- Status: 201 create, 204 sem corpo, 400 validação, 401/403 auth, 404, 409 conflito.
- Idempotency-Key em POST de pagamento/efeito externo.
- Timeouts + retry com backoff em HTTP externo; circuit breaker se o repo tiver.

## Filas (BullMQ/SQS/Rabbit/Kafka)
- Handler idempotente (chave de dedupe). Ack só após sucesso.
- Retry exponencial + DLQ. Payload versionado e validado.
- Sem trabalho pesado no request HTTP → enfileirar.

## Testes
- Jest/Vitest: `Test.createTestingModule` com providers reais da unidade e mocks só de I/O.
- e2e só se o repo já tem `test/*.e2e-spec.ts`.
