# Skill: security-check
Checagem focada SÓ nas linhas do diff. Saída no formato do `reviewer`.

## 1. Secrets vazados
`git diff HEAD -U0 | rg -n '^\+' | rg -i '(api[_-]?key|secret|token|passw|private[_-]?key|BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|xox[bpa]-|sk-[A-Za-z0-9_-]{20,}|mongodb(\+srv)?://[^ ]*:[^ ]*@|postgres(ql)?://[^ ]*:[^ ]*@)'`
Também: `.env`, `*.pem`, `*.key`, `credentials*.json` adicionados ao git.

## 2. Injection
- SQL: concatenação/template string em query (`` `SELECT ... ${x}` ``, f-string, `$queryRawUnsafe`, `.raw(` com input).
- NoSQL: objeto de request direto em filtro Mongo (`find(req.body)`, `$where`, operadores `$` vindos do usuário).
- Shell: `exec`/`spawn` com `shell: true`, `os.system`, `subprocess(..., shell=True)` com input.
- Path traversal: input do usuário em caminho de arquivo sem normalizar/validar.

## 3. XSS
`dangerouslySetInnerHTML`, `innerHTML`, `v-html`, `| safe`, `Markup(` com dado externo; URL `javascript:` em `href`.

## 4. Validação de input
Rota/handler/consumer novo sem schema (DTO, zod, Pydantic). Tipos/limites (tamanho, enum, range) ausentes.

## 5. Permissões
Endpoint novo sem guard/auth/middleware; checagem de ownership (IDOR) ausente; role hardcoded; CORS `*` com credenciais.

## 6. Diversos
Erro devolvendo stack/SQL ao cliente; log com PII/token; `verify=False`/`rejectUnauthorized: false`; crypto fraca (md5/sha1 para senha).

## Saída
`arquivo:linha — <categoria>: <problema> → <correção curta>` ou nada (sem achados).
