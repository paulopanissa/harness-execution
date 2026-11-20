## What

<!-- One or two sentences. Link the issue: Closes #123 -->

## Why

## Token impact

<!-- Output of `python3 ~/.hx/scripts/measure.py baseline` before/after, or "none" (scripts, tests, CI). -->

## Checklist

- [ ] `python3 -m unittest discover -s tests -t tests` passes
- [ ] Rule changes are made in English **and** in `i18n/pt-BR/` (or the PR says why not)
- [ ] Python stays stdlib-only; hooks stay plain bash
- [ ] Works with no per-project configuration
- [ ] No secrets, internal URLs, company names or personal paths
- [ ] `CHANGELOG.md` updated under `Unreleased` for user-facing changes
