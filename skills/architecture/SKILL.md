---
name: architecture
description: Use when verifying layer boundary compliance, dependency direction, circular dependencies, and Fat Controller violations in a layered or clean architecture codebase
---

# Verify Architecture

Detects architectural structural violations. Requires `.verify-structure.yml` for layer boundary checks. Circular dependency and Fat Controller checks run without config.

**REQUIRED REFERENCE:** Read `svs:findings-schema` and `svs:language-adapters`.

## Checks

### 1. Layer Boundary Violations (requires `.verify-structure.yml`)

For each layer, read its `source_paths` and `allowed_imports` from config. Walk all source files in that layer. Any import from a layer NOT in `allowed_imports` is a violation.

**violation_type:** `ARCH.LAYER_BOUNDARY`
**severity:** `error`

```python
# tests/architecture/test_layer_boundaries.py
import ast, yaml
from pathlib import Path

def _config():
    cfg = Path(".verify-structure.yml")
    if not cfg.exists():
        return None
    return yaml.safe_load(cfg.read_text())

def test_layer_boundaries():
    config = _config()
    if config is None:
        return  # skip — no .verify-structure.yml
    layers = {l["name"]: l for l in config["architecture"]["layers"]}
    violations = []
    for layer_name, layer in layers.items():
        allowed = layer.get("allowed_imports", [])
        forbidden_prefixes = [
            ".".join(Path(p).parts[1:])
            for name, l in layers.items()
            if name not in allowed and name != layer_name
            for p in l.get("source_paths", [f"src/{name}"])
        ]
        for src_dir in layer.get("source_paths", [f"src/{layer_name}"]):
            for py_file in Path(src_dir).rglob("*.py"):
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        if any(node.module.startswith(p) for p in forbidden_prefixes):
                            violations.append(
                                f"[{layer_name}] {py_file}:{node.lineno} "
                                f"imports forbidden module {node.module}"
                            )
    assert not violations, "Layer boundary violations:\n" + "\n".join(violations)
```

### 2. Circular Dependencies

Build a module import graph via AST. Run DFS cycle detection. Report each cycle as one finding.

**violation_type:** `ARCH.CIRCULAR_DEP`
**severity:** `error`

```python
# tests/architecture/test_circular_deps.py
import ast
from pathlib import Path
from collections import defaultdict

def _build_graph(src_root="src"):
    graph = defaultdict(set)
    root = Path(src_root)
    for py_file in root.rglob("*.py"):
        module = ".".join(py_file.with_suffix("").relative_to(root.parent).parts)
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                graph[module].add(node.module)
    return graph

def _find_cycles(graph):
    visited, rec_stack, cycles = set(), set(), []
    def dfs(node, path):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, path + [neighbor])
            elif neighbor in rec_stack:
                cycle_start = path.index(neighbor) if neighbor in path else 0
                cycles.append(" → ".join(path[cycle_start:] + [neighbor]))
        rec_stack.discard(node)
    for node in list(graph):
        if node not in visited:
            dfs(node, [node])
    return cycles

def test_no_circular_dependencies():
    cycles = _find_cycles(_build_graph())
    assert not cycles, "Circular dependencies:\n" + "\n".join(cycles)
```

### 3. Fat Controller

For each file in the `presentation` layer (from config, or files matching `*controller*`, `*router*`, `*view*`):
Count public methods/route handlers. If > 7, flag.

**violation_type:** `ARCH.FAT_CONTROLLER`
**severity:** `warning`

```python
def test_no_fat_controllers():
    MAX_HANDLERS = 7
    HTTP_METHODS = ("get", "post", "put", "patch", "delete")
    violations = []
    controller_dirs = ["src/api", "src/controllers", "src/views"]
    for ctrl_dir in controller_dirs:
        if not Path(ctrl_dir).exists():
            continue
        for py_file in Path(ctrl_dir).rglob("*.py"):
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            route_count = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for dec in node.decorator_list:
                        attr = None
                        if isinstance(dec, ast.Attribute):
                            attr = dec
                        elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                            attr = dec.func
                        if attr and attr.attr in HTTP_METHODS:
                            route_count += 1
                # Also count class-based controller methods
                if isinstance(node, ast.ClassDef):
                    methods = [n for n in node.body
                               if isinstance(n, ast.FunctionDef)
                               and not n.name.startswith("_")]
                    if len(methods) > MAX_HANDLERS:
                        violations.append(f"{py_file}: class {node.name} has {len(methods)} methods")
            if route_count > MAX_HANDLERS:
                violations.append(f"{py_file}: {route_count} route handlers (threshold: {MAX_HANDLERS})")
    if violations:
        print("Fat controllers (warning):\n" + "\n".join(violations))
```

## Java Layer Check (ArchUnit)

```java
@AnalyzeClasses(packages = "com.example")
class LayerTest {
    @ArchTest
    static final ArchRule layers = layeredArchitecture()
        .consideringAllDependencies()
        .layer("Domain").definedBy("..domain..")
        .layer("Application").definedBy("..application..")
        .layer("Infrastructure").definedBy("..infrastructure..")
        .layer("Presentation").definedBy("..presentation..")
        .whereLayer("Domain").mayNotAccessAnyLayer()
        .whereLayer("Application").mayOnlyAccessLayers("Domain")
        .whereLayer("Infrastructure").mayOnlyAccessLayers("Domain", "Application")
        .whereLayer("Presentation").mayOnlyAccessLayers("Application");

    @ArchTest
    static final ArchRule noCycles = slices()
        .matching("com.example.(*)..")
        .should().beFreeOfCycles();
}
```

## Findings Output Example

```json
[
  {
    "violation_type": "ARCH.LAYER_BOUNDARY",
    "severity": "error",
    "file": "src/domain/user.py",
    "line": 3,
    "description": "Domain layer imports from Infrastructure layer (infrastructure.db)",
    "suggested_fix": "Define UserRepository abstract interface in domain; implement it in infrastructure"
  },
  {
    "violation_type": "ARCH.CIRCULAR_DEP",
    "severity": "error",
    "file": "src/application/user_service.py",
    "line": 1,
    "description": "Circular dependency: application.user_service → domain.user → application.user_service",
    "suggested_fix": "Extract the shared dependency into a separate module with no back-references"
  }
]
```
