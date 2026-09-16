# CI integration (v0.2.0)

Produce a report even when the quality gate fails:

```bash
agent-rules-lint . --format sarif --output reports/instructions.sarif --warnings-as-errors
```

Exit codes: 0 passes; 1 findings fail the configured gate; 2 invalid path or report I/O failure.
SARIF contains relative paths, rule IDs and line locations, not file contents.

```yaml
name: Agent instructions
on: [push, pull_request]
permissions:
  contents: read
jobs:
  lint:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    steps:
      - uses: actions/checkout@v7.0.1
      - uses: Uky0Yang/agent-rules-lint@v0.2.0
        with:
          warnings-as-errors: 'true'
      - uses: github/codeql-action/upload-sarif@v4.37.9
        if: always() && hashFiles('agent-rules-lint.sarif') != ''
        with:
          sarif_file: agent-rules-lint.sarif
```

For a pre-commit gate, add to .pre-commit-config.yaml:

```yaml
repos:
  - repo: https://github.com/Uky0Yang/agent-rules-lint
    rev: v0.2.0
    hooks:
      - id: agent-rules-lint
```

The hook checks the whole instruction set once, without receiving individual filenames.
Fork PRs may not have code-scanning upload permissions; the lint report still runs.
