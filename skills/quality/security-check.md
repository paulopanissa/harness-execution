# Skill: security-check
Check ONLY the diff lines. Output in the `reviewer` format.

## 1. Leaked secrets
`git diff HEAD -U0 | rg -n '^\+' | rg -i '(api[_-]?key|secret|token|passw|private[_-]?key|BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|xox[bpa]-|sk-[A-Za-z0-9_-]{20,}|mongodb(\+srv)?://[^ ]*:[^ ]*@|postgres(ql)?://[^ ]*:[^ ]*@)'`
Also: `.env`, `*.pem`, `*.key`, `credentials*.json` added to git.

## 2. Injection
- SQL: concatenation/template strings in queries (`` `SELECT ... ${x}` ``, f-strings, `$queryRawUnsafe`, `.raw(` with input).
- NoSQL: request object straight into a Mongo filter (`find(req.body)`, `$where`, `$` operators coming from the user).
- Shell: `exec`/`spawn` with `shell: true`, `os.system`, `subprocess(..., shell=True)` with input.
- Path traversal: user input in a file path without normalizing/validating.

## 3. XSS
`dangerouslySetInnerHTML`, `innerHTML`, `v-html`, `| safe`, `Markup(` with external data; `javascript:` URLs in `href`.

## 4. Input validation
New route/handler/consumer without a schema (DTO, zod, Pydantic). Missing types/limits (size, enum, range).

## 5. Permissions
New endpoint without guard/auth/middleware; missing ownership check (IDOR); hardcoded role; CORS `*` with credentials.

## 6. Misc
Errors returning stack/SQL to the client; logs with PII/tokens; `verify=False`/`rejectUnauthorized: false`; weak crypto (md5/sha1 for passwords).

## Output
`file:line — <category>: <problem> → <short fix>` or nothing (no findings).
