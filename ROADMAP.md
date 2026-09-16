# Roadmap

## Near Term

Shipped in v0.2.0: SARIF, a composite GitHub Action and a pre-commit hook.

- Add more real-world examples
- Add markdown output
- Add line excerpts in JSON output
- Support config in `pyproject.toml`
- Keep PyPI releases automated through Trusted Publishing

## Mid Term

- Add rule IDs with documentation pages
- Add optional token estimation adapters
- Add fixture corpus from public agent instruction files

## Long Term

- Build a benchmark of high-quality agent instruction files
- Add project-specific profiles for Codex, Claude Code, Cursor, Copilot, and Gemini CLI

## Non-Goals

- No model-based scoring by default
- No network calls by default
- No automatic rewriting of user instructions without explicit user action
