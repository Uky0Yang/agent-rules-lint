# agent-rules-lint

Lint AI agent instruction files before they confuse your coding agent.

`agent-rules-lint` is a small, dependency-free Python CLI that scans files such as `AGENTS.md`, `CLAUDE.md`, Cursor rules, and GitHub Copilot instructions for common quality and safety problems.

## Why

Recent high-growth developer repos show a clear pattern: teams are adding more agent skills, rule files, memory files, and coding-agent playbooks. The missing piece is a quick quality gate for those instructions.

Bad agent instructions are expensive. They can be too long, vague, contradictory, unsafe, or accidentally include secrets. This tool gives you a fast local and CI check before those rules affect real work.

## What It Checks

- Common instruction files:
  - `AGENTS.md`
  - `CLAUDE.md`
  - `GEMINI.md`
  - `.cursorrules`
  - `.cursor/rules/*.md`
  - `.github/copilot-instructions.md`
  - `.github/instructions/*.md`
- Secret-like values
- Risky shell and Git commands
- Prompt-injection-like language
- Missing title
- Missing purpose, scope, command, or safety guidance
- Vague language
- Files that are too long for practical agent use
- A small set of obvious contradictory rules

## Install

From this repository:

```bash
python -m pip install -e .
```

Or run without installing:

```bash
python -m agent_rules_lint .
```

## Usage

Scan the current repository:

```bash
agent-rules-lint .
```

Return JSON for CI or custom reports:

```bash
agent-rules-lint . --format json
```

Fail CI on warnings:

```bash
agent-rules-lint . --warnings-as-errors
```

Change the long-file threshold:

```bash
agent-rules-lint . --max-chars 8000
```

## Example Output

```text
agent-rules-lint checked 1 file(s)
errors=0 warnings=1 info=2

Files:
  - AGENTS.md

Findings:
  [warning] AGENTS.md:42 risky-command: Risky command should include explicit safeguards or approval rules.
  [info] AGENTS.md missing-safety: Consider adding a clear safety section.
```

## CI

Add this to GitHub Actions:

```yaml
name: Lint agent rules

on:
  pull_request:
  push:
    branches:
      - main

jobs:
  lint-agent-rules:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install -e .
      - run: agent-rules-lint . --warnings-as-errors
```

## Design Principles

- No model calls
- No network calls
- No dependencies
- Safe to run in CI
- Findings should be specific enough to act on
- Warnings should improve instruction quality, not enforce one writing style

## Current Limitations

- Conflict detection is intentionally conservative and only catches obvious pairs.
- It does not estimate real tokenizer counts; it uses character length as a practical proxy.
- It does not validate whether an instruction is correct for a specific tool.

## Development

```bash
python -m pip install -e .
python -m unittest discover -s tests
python -m agent_rules_lint .
```

## Agent OSS Toolkit

This project is part of a small toolkit for building and launching agent-ready open-source repositories:

- [agent-repo-kit](https://github.com/Uky0Yang/agent-repo-kit): scaffold launch-ready, AI-agent-friendly repositories
- [oss-launch-check](https://github.com/Uky0Yang/oss-launch-check): audit whether a repository is ready to launch as open source
- [repo-context-card](https://github.com/Uky0Yang/repo-context-card): generate compact repository context cards for coding agents
- [agent-rules-lint](https://github.com/Uky0Yang/agent-rules-lint): lint AGENTS.md, CLAUDE.md, Cursor rules, and Copilot instructions
- [awesome-ai-agents-zh](https://github.com/Uky0Yang/awesome-ai-agents-zh): Chinese AI Agents / MCP / AI DevTools directory

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
