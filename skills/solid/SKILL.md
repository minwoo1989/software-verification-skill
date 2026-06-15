---
name: solid
description: Use when verifying SOLID principle compliance in an object-oriented codebase
---

# Verify SOLID

Detects SOLID principle violations. Runs for OOP languages (Python, Java, Kotlin, C#, TypeScript with classes).

**REQUIRED REFERENCE:** Read `svs:findings-schema` for output format. Read `svs:language-adapters` for AST tool.

## Rules

### SRP — Single Responsibility Principle
- **Heuristic:** Class with > 10 public methods
- **Semantic check:** After flagging by count, read method names and group by apparent responsibility. Report as `error` only if 2+ distinct responsibility clusters exist. Report as `warning` if count is 10-14 with a single coherent cluster.
- **violation_type:** `SOLID.SRP`

### OCP — Open/Closed Principle
- **Heuristic:** `if`/`elif` chain with > 5 branches that checks a type field, enum value, or string tag (e.g., `if action == "create": ... elif action == "update":`)
- **violation_type:** `SOLID.OCP`

### LSP — Liskov Substitution Principle
- **Heuristic:** Subclass method override that raises `NotImplementedError` or an exception class not declared in the parent method
- **violation_type:** `SOLID.LSP`

### ISP — Interface Segregation Principle
- **Heuristic:** Abstract class or Protocol with > 7 abstract methods
- **violation_type:** `SOLID.ISP`

### DIP — Dependency Inversion Principle
- **Source of truth:** `.verify-structure.yml` `architecture.layers` declares which layers are "infrastructure". Do NOT use hardcoded keywords.
- **Detection:** Files in a layer scan imports. If a module in a high-level layer (domain, application) directly imports from a path declared as an infrastructure layer's `source_paths`, flag as DIP violation.
- **Fallback if no `.verify-structure.yml`:** Skip DIP check and note it requires architecture config.
- **violation_type:** `SOLID.DIP`

## Python Detection Pattern for DIP

```python
import ast, yaml
from pathlib import Path

def _load_config():
    cfg_path = Path(".verify-structure.yml")
    if not cfg_path.exists():
        return None
    return yaml.safe_load(cfg_path.read_text())

def _layer_paths(config, layer_name):
    for layer in config["architecture"]["layers"]:
        if layer["name"] == layer_name:
            return layer.get("source_paths", [f"src/{layer_name}"])
    return []

def test_dip_domain_no_infrastructure_import():
    config = _load_config()
    if config is None:
        return  # skip — no config
    infra_paths = _layer_paths(config, "infrastructure")
    domain_paths = _layer_paths(config, "domain")
    violations = []
    for domain_src in domain_paths:
        for py_file in Path(domain_src).rglob("*.py"):
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if any(node.module.startswith(".".join(Path(p).parts[1:]))
                           for p in infra_paths):
                        violations.append(f"{py_file}:{node.lineno} → {node.module}")
    assert not violations, "DIP violations:\n" + "\n".join(violations)
```

## Findings Output Example

```json
[
  {
    "violation_type": "SOLID.DIP",
    "severity": "error",
    "file": "src/domain/user.py",
    "line": 3,
    "description": "Domain layer directly imports from infrastructure layer (infrastructure.db)",
    "suggested_fix": "Define UserRepository as an abstract interface in domain; inject it via constructor"
  }
]
```
