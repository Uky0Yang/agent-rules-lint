import json
import tempfile
import unittest
from pathlib import Path

from agent_rules_lint.cli import main


class SarifTests(unittest.TestCase):
    def test_report_file_preserves_failure_and_source_location(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'AGENTS.md').write_text('# Rules\nRun git reset --hard\n', encoding='utf-8')
            output = root / 'reports' / 'lint.sarif'
            code = main([str(root), '--format', 'sarif', '--output', str(output), '--warnings-as-errors'])
            report = json.loads(output.read_text(encoding='utf-8'))
            results = report['runs'][0]['results']
            self.assertEqual(code, 1)
            self.assertEqual(report['version'], '2.1.0')
            self.assertTrue(any(r['locations'][0]['physicalLocation']['region']['startLine'] == 2 for r in results if 'region' in r['locations'][0]['physicalLocation']))
