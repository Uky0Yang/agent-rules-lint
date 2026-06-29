from __future__ import annotations

import argparse
from pathlib import Path
import sys

from . import __version__
from .linter import LintResult, lint_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-rules-lint",
        description="Lint AI agent instruction files such as AGENTS.md, CLAUDE.md, Cursor rules, and Copilot instructions.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Repository or directory to scan.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    parser.add_argument("--max-chars", type=int, default=12000, help="Warn when a file exceeds this many characters.")
    parser.add_argument("--warnings-as-errors", action="store_true", help="Exit non-zero when warnings are found.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def render_text(result: LintResult) -> str:
    lines = [
        f"agent-rules-lint checked {len(result.files_checked)} file(s)",
        f"errors={result.error_count} warnings={result.warning_count} info={result.info_count}",
    ]
    if result.files_checked:
        lines.append("")
        lines.append("Files:")
        for file in result.files_checked:
            lines.append(f"  - {file}")

    if result.findings:
        lines.append("")
        lines.append("Findings:")
        for finding in result.findings:
            location = finding.file
            if finding.line is not None:
                location = f"{location}:{finding.line}"
            lines.append(f"  [{finding.severity}] {location} {finding.rule}: {finding.message}")
    else:
        lines.append("")
        lines.append("No findings.")

    return "\n".join(lines)


def exit_code(result: LintResult, warnings_as_errors: bool) -> int:
    if result.error_count:
        return 1
    if warnings_as_errors and result.warning_count:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = lint_path(Path(args.path), max_chars=args.max_chars)

    if args.format == "json":
        print(result.to_json())
    else:
        print(render_text(result))

    return exit_code(result, warnings_as_errors=args.warnings_as_errors)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
