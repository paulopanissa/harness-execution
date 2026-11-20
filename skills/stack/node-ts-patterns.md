# Skill: node-ts-patterns
Read only when in doubt. The repo's pattern beats this list.

## Structure (NestJS)
- One module per domain: `controller` (thin HTTP) → `service` (rules) → `repository`/Prisma (data).
- Input DTO with `class-validator` + `ValidationPipe({ whitelist: true, forbidNonWhitelisted: true })`.
- Guards for auth/roles; interceptors for logging/serialization; global exception filters.
- Config via `ConfigService` + schema validated at boot.

## TypeScript
- `strict: true`. No new `any` → `unknown` + narrowing.
- Explicit return types on exports. `readonly` on DTO/entity props.
- Typed domain errors (`class NotFoundError extends DomainError`), mapped to HTTP in the filter.
- Immutability: spread/`map`, never mutate arguments.

## Prisma
- Explicit `select`/`include`; never return a raw entity with sensitive fields.
- Multiple writes → `prisma.$transaction`. Paginate with `take`/`cursor`.
- N+1: fetch in batch (`where: { id: { in } }`). Raw only via tagged `$queryRaw` (never `Unsafe` with input).
- New migration → review `DROP`/`NOT NULL` without default.

## APIs
- Status: 201 create, 204 no body, 400 validation, 401/403 auth, 404, 409 conflict.
- Idempotency-Key on POSTs for payments/external side effects.
- Timeouts + retry with backoff on external HTTP; circuit breaker if the repo has one.

## Queues (BullMQ/SQS/Rabbit/Kafka)
- Idempotent handler (dedupe key). Ack only after success.
- Exponential retry + DLQ. Versioned, validated payload.
- No heavy work inside the HTTP request → enqueue.

## Tests
- Jest/Vitest: `Test.createTestingModule` with the unit's real providers and mocks only for I/O.
- e2e only if the repo already has `test/*.e2e-spec.ts`.
