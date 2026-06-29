from __future__ import annotations

import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from agent_rules_lint.cli import main


class CliTests(unittest.TestCase):
    def test_clean_file_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text(
                "# Rules\n\n"
                "## Purpose\n\nHelp agents.\n\n"
                "## Scope\n\nThis repo.\n\n"
                "## Commands\n\nRun tests.\n\n"
                "## Safety\n\nDo not commit secrets.\n",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                self.assertEqual(main([str(root)]), 0)

    def test_warnings_as_errors_exits_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n\nRun `git reset --hard`.", encoding="utf-8")

            with redirect_stdout(StringIO()):
                self.assertEqual(main([str(root), "--warnings-as-errors"]), 1)


if __name__ == "__main__":
    unittest.main()
