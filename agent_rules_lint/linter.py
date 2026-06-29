from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import fnmatch
import json
import re
from typing import Iterable


DEFAULT_PATTERNS = (
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".cursorrules",
    ".cursor/rules/*.md",
    ".github/copilot-instructions.md",
    ".github/instructions/*.md",
)

DEFAULT_IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
}

SECRET_PATTERNS = (
    re.compile(r"\bghp_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgho_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
)

RISKY_COMMAND_PATTERNS = (
    re.compile(r"\brm\s+-rf\s+[/~$*]", re.IGNORECASE),
    re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE),
    re.compile(r"\bgit\s+clean\s+-fdx\b", re.IGNORECASE),
    re.compile(r"\bRemove-Item\b.+\b-Recurse\b.+\b-Force\b", re.IGNORECASE),
    re.compile(r"\bcurl\b.+\|\s*(bash|sh)\b", re.IGNORECASE),
    re.compile(r"\bwget\b.+\|\s*(bash|sh)\b", re.IGNORECASE),
)

PROMPT_INJECTION_PATTERNS = (
    re.compile(r"ignore (all )?(previous|prior|above) instructions", re.IGNORECASE),
    re.compile(r"reveal (the )?(system|developer) (prompt|message)", re.IGNORECASE),
    re.compile(r"bypass (safety|policy|guardrails)", re.IGNORECASE),
)

SECTION_HINTS = {
    "purpose": ("purpose", "goal", "objective", "what this does", "overview", "目标", "目的"),
    "scope": ("scope", "when to use", "applies to", "boundaries", "范围", "适用"),
    "commands": ("commands", "scripts", "verification", "tests", "test", "build", "命令", "验证", "测试"),
    "safety": ("safety", "security", "secrets", "do not", "never", "安全", "密钥", "不要"),
    "style": ("style", "formatting", "conventions", "tone", "风格", "格式", "约定"),
}


@dataclass(frozen=True)
class Finding:
    file: str
    severity: str
    rule: str
    message: str
    line: int | None = None

    def to_dict(self) -> dict:
        data = {
            "file": self.file,
            "severity": self.severity,
            "rule": self.rule,
            "message": self.message,
        }
        if self.line is not None:
            data["line"] = self.line
        return data


@dataclass
class LintResult:
    root: str
    files_checked: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")

    @property
    def info_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "info")

    def to_dict(self) -> dict:
        return {
            "root": self.root,
            "files_checked": self.files_checked,
            "summary": {
                "errors": self.error_count,
                "warnings": self.warning_count,
                "info": self.info_count,
            },
            "findings": [finding.to_dict() for finding in self.findings],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


def discover_instruction_files(root: Path, patterns: Iterable[str] = DEFAULT_PATTERNS) -> list[Path]:
    root = root.resolve()
    matches: list[Path] = []
    normalized_patterns = tuple(pattern.replace("\\", "/") for pattern in patterns)

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in DEFAULT_IGNORE_DIRS for part in path.relative_to(root).parts):
            continue
        relative = path.relative_to(root).as_posix()
        if any(fnmatch.fnmatch(relative, pattern) for pattern in normalized_patterns):
            matches.append(path)

    return sorted(matches, key=lambda item: item.relative_to(root).as_posix())


def lint_path(root: Path, max_chars: int = 12000) -> LintResult:
    root = root.resolve()
    result = LintResult(root=str(root))
    files = discover_instruction_files(root)

    if not files:
        result.findings.append(
            Finding(
                file=".",
                severity="warning",
                rule="no-instruction-files",
                message="No known agent instruction files found.",
            )
        )
        return result

    for path in files:
        relative = path.relative_to(root).as_posix()
        result.files_checked.append(relative)
        result.findings.extend(lint_file(path, root, max_chars=max_chars))

    return result


def lint_file(path: Path, root: Path, max_chars: int = 12000) -> list[Finding]:
    relative = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    findings: list[Finding] = []

    if not text.strip():
        findings.append(Finding(relative, "error", "empty-file", "Instruction file is empty."))
        return findings

    if len(text) > max_chars:
        findings.append(
            Finding(
                relative,
                "warning",
                "too-long",
                f"Instruction file is {len(text)} characters; consider splitting or tightening it.",
            )
        )

    if not re.search(r"^#\s+\S+", text, flags=re.MULTILINE):
        findings.append(Finding(relative, "warning", "missing-title", "Add a top-level heading."))

    present_sections = detect_sections(text)
    for section in ("purpose", "scope", "commands", "safety"):
        if section not in present_sections:
            findings.append(
                Finding(
                    relative,
                    "info",
                    f"missing-{section}",
                    f"Consider adding a clear {section} section.",
                )
            )

    findings.extend(scan_patterns(relative, lines, SECRET_PATTERNS, "error", "secret-like-value", "Looks like a secret or private key."))
    findings.extend(scan_patterns(relative, lines, RISKY_COMMAND_PATTERNS, "warning", "risky-command", "Risky command should include explicit safeguards or approval rules."))
    findings.extend(scan_patterns(relative, lines, PROMPT_INJECTION_PATTERNS, "warning", "prompt-injection", "Instruction resembles prompt-injection language."))
    findings.extend(scan_weak_language(relative, lines))
    findings.extend(scan_absolute_claims(relative, lines))
    findings.extend(scan_conflicts(relative, lines))

    return findings


def detect_sections(text: str) -> set[str]:
    lowered = text.lower()
    present: set[str] = set()
    for section, hints in SECTION_HINTS.items():
        if any(hint in lowered for hint in hints):
            present.add(section)
    return present


def scan_patterns(
    relative: str,
    lines: list[str],
    patterns: Iterable[re.Pattern[str]],
    severity: str,
    rule: str,
    message: str,
) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, line in enumerate(lines, start=1):
        if any(pattern.search(line) for pattern in patterns):
            findings.append(Finding(relative, severity, rule, message, line_number))
    return findings


def scan_weak_language(relative: str, lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    pattern = re.compile(r"\b(try to|maybe|if possible|do your best|尽量|可能的话)\b", re.IGNORECASE)
    for line_number, line in enumerate(lines, start=1):
        if pattern.search(line):
            findings.append(
                Finding(
                    relative,
                    "info",
                    "weak-language",
                    "Vague language can make agent behavior inconsistent.",
                    line_number,
                )
            )
    return findings


def scan_absolute_claims(relative: str, lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    pattern = re.compile(r"\b(always|never|must|禁止|必须|永远|绝不)\b", re.IGNORECASE)
    for line_number, line in enumerate(lines, start=1):
        if pattern.search(line) and len(line) > 180:
            findings.append(
                Finding(
                    relative,
                    "info",
                    "long-absolute-rule",
                    "Long absolute rules are hard to follow; split into short, testable bullets.",
                    line_number,
                )
            )
    return findings


def scan_conflicts(relative: str, lines: list[str]) -> list[Finding]:
    text = "\n".join(lines).lower()
    findings: list[Finding] = []
    conflict_pairs = (
        ("always ask", "never ask"),
        ("always commit", "never commit"),
        ("always browse", "never browse"),
        ("must use python", "never use python"),
        ("必须询问", "不要询问"),
    )
    for left, right in conflict_pairs:
        if left in text and right in text:
            findings.append(
                Finding(
                    relative,
                    "warning",
                    "possible-conflict",
                    f"Possible conflicting instructions: '{left}' and '{right}'.",
                )
            )
    return findings
