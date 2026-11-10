"""Small, deterministic checks. Submitted Python code is parsed, never run."""

import ast
import re

from app.schemas.audits import CodeAuditCreate, DesignAuditCreate
from app.schemas.findings import Severity

Issue = tuple[str, str, str, Severity]


def analyze_code(data: CodeAuditCreate) -> list[Issue]:
    issues: list[Issue] = []
    try:
        tree = ast.parse(data.source)
    except SyntaxError as exc:
        return [("syntax_error", f"Syntax error on line {exc.lineno}",
                 "Correct the Python syntax and run the audit again.", "critical")]

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in {"eval", "exec"}:
                issues.append(("unsafe_call", f"{node.func.id}() on line {node.lineno}",
                               "Avoid executing dynamic code.", "high"))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if (node.end_lineno or node.lineno) - node.lineno + 1 > 30:
                issues.append(("long_function", f"Function {node.name} exceeds 30 lines",
                               "Split the function into smaller parts.", "low"))

    for line_number, line in enumerate(data.source.splitlines(), start=1):
        if re.search(r"(?i)\b(password|api_key|secret)\s*=\s*['\"][^'\"]+['\"]", line):
            issues.append(("hardcoded_secret", f"Possible hardcoded secret on line {line_number}",
                           "Move secrets to environment variables.", "high"))
    return issues


def _luminance(color: str) -> float:
    channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
              for value in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def analyze_design(data: DesignAuditCreate) -> list[Issue]:
    issues: list[Issue] = []
    for index, element in enumerate(data.elements, start=1):
        if element.kind in {"button", "input", "link"} and not (element.label or "").strip():
            issues.append(("missing_label", f"Element {index} has no label",
                           "Add visible text or an accessible name.", "high"))
        light = max(_luminance(element.text_color), _luminance(element.background_color))
        dark = min(_luminance(element.text_color), _luminance(element.background_color))
        if (light + 0.05) / (dark + 0.05) < 4.5:
            issues.append(("low_contrast", f"Element {index} has low text contrast",
                           "Use colors with a contrast ratio of at least 4.5:1.", "medium"))
        if element.font_size < 14:
            issues.append(("small_text", f"Element {index} uses small text",
                           "Use a font size of at least 14 px.", "low"))
        if element.kind in {"button", "input", "link"} and (
            element.width is not None and element.width < 44
            or element.height is not None and element.height < 44
        ):
            issues.append(("small_target", f"Element {index} has a small interactive area",
                           "Use an interactive area of at least 44 by 44 px.", "medium"))
    return issues
