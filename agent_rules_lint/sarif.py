"""SARIF 2.1.0 output without source contents or absolute local paths."""
import json
from urllib.parse import quote

from . import __version__
from .linter import LintResult


def render_sarif(result: LintResult) -> str:
    rules = sorted({item.rule for item in result.findings})
    results = []
    for item in result.findings:
        location = {'artifactLocation': {'uri': quote(item.file.replace('\\', '/'), safe='/')}}
        if item.line is not None:
            location['region'] = {'startLine': max(1, item.line)}
        results.append({
            'ruleId': item.rule,
            'ruleIndex': rules.index(item.rule),
            'level': {'error': 'error', 'warning': 'warning', 'info': 'note'}[item.severity],
            'message': {'text': item.message},
            'locations': [{'physicalLocation': location}],
        })
    return json.dumps({
        '$schema': 'https://json.schemastore.org/sarif-2.1.0.json',
        'version': '2.1.0',
        'runs': [{'tool': {'driver': {
            'name': 'agent-rules-lint', 'version': __version__,
            'informationUri': 'https://github.com/Uky0Yang/agent-rules-lint',
            'rules': [{'id': rule} for rule in rules],
        }}, 'results': results}],
    }, ensure_ascii=False, indent=2)
