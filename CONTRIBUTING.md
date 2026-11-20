# Contributing to HX

Thanks for taking the time. HX is maintained by one person, so this page sets clear expectations before you write code.

[Português](docs/CONTRIBUTING.pt-BR.md)

## How decisions are made

- Every pull request is reviewed and merged by the maintainer ([CODEOWNERS](.github/CODEOWNERS)). Nobody else can merge.
- A PR can be correct and still be declined if it does not fit the project's direction. You will get a reason.
- For anything bigger than a bug fix, **open an issue first** and wait for a go-ahead. It saves you work.

## What fits HX

HX exists to keep agent sessions cheap and predictable. A change fits when it:

1. **Does not grow the always-loaded context** without a strong reason. `AGENTS.md` plus agent and command descriptions are paid on every turn. Skills and command bodies load on demand, so prefer them.
2. **Needs no per-project configuration.** `/hx` must keep working in any repository through the global files only.
3. **Keeps the stack minimal:** Python stdlib only, plain bash hooks, no network calls at runtime besides `git`.
4. **Enforces rules in code when possible** (hooks, gate) instead of adding more prompt text.
5. **Stays company-neutral.** Corporate flows belong in a private org preset, never in this repository.

Probably declined: new always-on rules, heavy dependencies, telemetry, features tied to one company or one personal setup.

## Workflow

```bash
gh repo fork paulopanissa/harness-execution --clone
cd harness-execution
git switch -c fix/short-description
python3 -m unittest discover -s tests -t tests   # must pass
```

- Tests run in a sandbox (own `HX_HOME`, Claude and Codex homes). They never touch your real install.
- Rules live in English at the root and in Brazilian Portuguese under `i18n/pt-BR/`. Change both, or say in the PR why not. The test suite checks the two sets have the same files and frontmatter.
- Report token impact with `python3 scripts/measure.py baseline --lang all` (before/after) when you touch rules.
- Commits follow [Conventional Commits](https://www.conventionalcommits.org/): `feat|fix|refactor|chore|docs|test|perf|ci`.
- One topic per PR. Small PRs get reviewed first.
- CI (Ubuntu + Windows) must be green before review.

## Reporting bugs

Use the issue templates. Strip tokens, internal URLs, company names and personal paths from logs before posting.

## Security

Do not open public issues for vulnerabilities. See [SECURITY.md](SECURITY.md).

## License

By contributing you agree that your contribution is licensed under the [MIT License](LICENSE).
