# Contributing

Thanks for helping improve `agent-rules-lint`.

## Good Contributions

- New checks for common agent instruction mistakes
- Better false-positive handling
- Tests for real-world `AGENTS.md`, `CLAUDE.md`, Cursor, or Copilot instruction patterns
- Documentation examples
- CI integration examples

## Before Opening a PR

Run:

```bash
python -m pytest
python -m agent_rules_lint .
```

If your change adds or changes a lint rule, include tests.

## Rule Design

Rules should be:

- Easy to explain
- Low noise
- Useful without sending data to a model
- Safe for public and private repositories

Avoid checks that require personal taste or project-specific assumptions.
