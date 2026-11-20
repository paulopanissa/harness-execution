# Security policy

## Supported versions

Only the latest release on `main` gets fixes. Update with `python3 ~/.hx/scripts/update.py`.

## Reporting a vulnerability

**Do not open a public issue.** Report privately through GitHub:
[Security → Report a vulnerability](https://github.com/paulopanissa/harness-execution/security/advisories/new).

Include what you found, how to reproduce it, and the impact. You should get a first answer within 7 days. Please keep the details private until a fix is released.

## Scope

HX runs on your machine with your permissions. It writes to `~/.hx`, `~/.claude` and `~/.codex`, and registers hooks that Claude Code runs before tool calls. Relevant reports include:

- a hook or script that can be made to run unintended commands, write outside those folders, or leak file contents;
- `install.py`, `update.py` or `sync.py` overwriting user files without the backup they promise;
- secrets or personal data ending up in generated files, logs or the repository.

Third-party mods in `mods/catalog.json` are independent projects; report their issues to their own repositories.
