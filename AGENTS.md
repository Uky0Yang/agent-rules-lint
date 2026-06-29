# Agent Instructions

## Purpose

Maintain `agent-rules-lint`, a dependency-free Python CLI for linting AI agent instruction files.

## Scope

These instructions apply to code, tests, documentation, and GitHub workflow files in this repository.

## Commands

Run the standard checks before publishing:

```bash
python -m unittest discover -s tests
python -m agent_rules_lint .
```

## Safety

- Do not add network calls to the default lint path.
- Do not add model calls to the default lint path.
- Do not commit API keys, access tokens, cookies, private credentials, or generated build output.
- Keep checks deterministic so they are safe for CI.

## Style

- Prefer standard-library Python.
- Keep rule messages short and actionable.
- Add tests when changing lint behavior.
