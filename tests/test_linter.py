from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_rules_lint.linter import discover_instruction_files, lint_path


class LinterTests(unittest.TestCase):
    def test_discovers_common_instruction_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Agent\n\nPurpose section.", encoding="utf-8")
            (root / ".cursor" / "rules").mkdir(parents=True)
            (root / ".cursor" / "rules" / "ui.md").write_text("# UI\n\nScope section.", encoding="utf-8")
            (root / "README.md").write_text("# Ignore", encoding="utf-8")

            discovered = [path.relative_to(root).as_posix() for path in discover_instruction_files(root)]

            self.assertEqual(discovered, [".cursor/rules/ui.md", "AGENTS.md"])

    def test_flags_secret_like_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "CLAUDE.md").write_text("# Rules\n\nUse token sk-abcdefghijklmnopqrstuvwxyz123456.", encoding="utf-8")

            result = lint_path(root)

            self.assertEqual(result.error_count, 1)
            self.assertTrue(any(finding.rule == "secret-like-value" for finding in result.findings))

    def test_flags_risky_commands_without_failing_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n\nRun `git reset --hard` when stuck.", encoding="utf-8")

            result = lint_path(root)

            self.assertEqual(result.error_count, 0)
            self.assertTrue(any(finding.rule == "risky-command" for finding in result.findings))

    def test_warns_when_no_instruction_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = lint_path(Path(directory))

            self.assertEqual(result.warning_count, 1)
            self.assertEqual(result.findings[0].rule, "no-instruction-files")


if __name__ == "__main__":
    unittest.main()
