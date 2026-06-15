---
name: metrics
description: Use when checking a codebase for cyclomatic complexity, file size, and God Object violations as part of structural verification
---

# Verify Metrics

Detects code quality metric violations. Always runs regardless of architecture type — language detection alone is sufficient.

**REQUIRED REFERENCE:** Read `svs:findings-schema` for output format. Read `svs:language-adapters` for AST tool per language.

## Thresholds

| Metric | Warning | Error | How to Count |
|---|---|---|---|
| Cyclomatic complexity per function | — | > 10 | 1 + number of: `if`, `elif`, `for`, `while`, `except`, `with`, `assert`, comprehension conditions |
| File line count | > 300 | > 500 | Raw line count including blanks and comments |
| Class method count | — | > 20 | Public methods only (exclude `_private`) |
| Function line count | — | > 50 | Lines from `def` to last line of body |

## Process

1. Read `svs:language-adapters` for the AST tool to use.
2. For Python: use `ast.parse()` to walk all `.py` files under declared source root.
3. For each function/method: count branch nodes for complexity. Count lines for length.
4. For each class: count public methods. If > 20, emit `METRICS.GOD_OBJECT` finding.
5. For each file: count lines.
6. Emit findings following `svs:findings-schema`.

## Python Implementation (generated test pattern)

```python
# tests/architecture/test_metrics.py
import ast
from pathlib import Path

BRANCH_NODES = (ast.If, ast.For, ast.While, ast.ExceptHandler,
                ast.With, ast.Assert, ast.comprehension)

def _src_files():
    return list(Path("src").rglob("*.py"))

def test_function_complexity():
    violations = []
    for py_file in _src_files():
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = 1 + sum(
                    1 for n in ast.walk(node) if isinstance(n, BRANCH_NODES)
                )
                if complexity > 10:
                    violations.append(
                        f"{py_file}:{node.lineno} {node.name}() complexity={complexity}"
                    )
    assert not violations, "Cyclomatic complexity violations:\n" + "\n".join(violations)

def test_file_size():
    errors, warnings = [], []
    for py_file in _src_files():
        lines = len(py_file.read_text(encoding="utf-8").splitlines())
        if lines > 500:
            errors.append(f"[error]   {py_file}: {lines} lines")
        elif lines > 300:
            warnings.append(f"[warning] {py_file}: {lines} lines")
    if warnings:
        print("\n".join(warnings))
    assert not errors, "Files exceed 500-line limit:\n" + "\n".join(errors)

def test_no_god_classes():
    violations = []
    for py_file in _src_files():
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                public = [
                    n for n in node.body
                    if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")
                ]
                if len(public) > 20:
                    violations.append(f"{py_file}: {node.name} ({len(public)} public methods)")
    assert not violations, "God classes detected:\n" + "\n".join(violations)

def test_large_functions():
    violations = []
    for py_file in _src_files():
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                length = node.end_lineno - node.lineno + 1
                if length > 50:
                    violations.append(
                        f"{py_file}:{node.lineno} {node.name}() is {length} lines"
                    )
    assert not violations, "Large functions (>50 lines):\n" + "\n".join(violations)
```

## Findings Output Example

```json
[
  {
    "violation_type": "METRICS.COMPLEXITY",
    "severity": "error",
    "file": "src/application/user_service.py",
    "line": 4,
    "description": "Function process() has cyclomatic complexity 11 (threshold: 10)",
    "suggested_fix": "Extract nested conditions into guard clauses or separate functions"
  }
]
```
