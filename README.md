# software-verification-skill

[한국어](README.ko.md)

A Claude Code plugin that verifies software structural integrity and generates permanent CI-enforcing architecture tests.

Detects SOLID violations, layer boundary breaches, circular dependencies, cyclomatic complexity, and REST API anti-patterns — then writes test files that fail the build when structure regresses.

---

## Installation

**Step 1 — Add the marketplace**

```
/plugin marketplace add https://github.com/minwoo1989/software-verification-skill
```

**Step 2 — Install the plugin**

```
/plugin install software-verification-skill
```

---

## Skills

| Skill | Invocation | Description |
|---|---|---|
| `verify-structure` | `/verify:verify-structure` | Entry point — detects, confirms, dispatches, reports, generates |
| `solid` | `/verify:solid` | SOLID principle violations (SRP, OCP, LSP, ISP, DIP) |
| `architecture` | `/verify:architecture` | Layer boundaries, circular deps, Fat Controller |
| `metrics` | `/verify:metrics` | Cyclomatic complexity, file size, God Object |
| `api-design` | `/verify:api-design` | REST anti-patterns (pagination, versioning, status codes, etc.) |

---

## Usage

### Quick start

Run the entry point skill from your project root:

```
/verify:verify-structure
```

**First run — Claude will:**
1. Detect language and framework by parsing manifest files
2. Propose an architecture layer structure (e.g., Clean Architecture, MVC)
3. Ask for your confirmation before applying any rules
4. Write `.verify-structure.yml` with the confirmed rules
5. Run all relevant sub-skills and report findings
6. Offer to generate permanent architecture test files

**Re-runs — Claude will:**
- Read `.verify-structure.yml` directly and skip detection
- Run analysis and report new/existing violations

### Example output

```
── Structural Issues Found ───────────────────────────────
[error]   src/domain/user.py:3
          ARCH.LAYER_BOUNDARY — domain imports infrastructure.db
          Fix: Define UserRepository interface in domain; inject via constructor

[warning] src/application/user_service.py:4
          METRICS.COMPLEXITY — process() complexity=11 (threshold: 10)
          Fix: Extract nested conditions into guard clauses
──────────────────────────────────────────────────────────
1 error, 1 warning

Generate architecture tests to enforce these rules in CI? [Y/n]
```

### Generated test files

After confirmation, test files are written to your project (e.g., `tests/architecture/`):

```
tests/architecture/test_layer_boundaries.py  ← ARCH violations
tests/architecture/test_solid.py             ← SOLID violations
tests/architecture/test_metrics.py           ← Metrics violations
tests/architecture/test_api_design.py        ← API design violations
```

These tests run on every CI build and fail if a violation is introduced.

### Run sub-skills individually

```
/verify:metrics        — Complexity, file size, God Object
/verify:solid          — SOLID principle violations
/verify:architecture   — Layer boundaries, circular deps, Fat Controller
/verify:api-design     — REST anti-patterns
```

---

## Configuration

`.verify-structure.yml` is created on first run and committed to your repo:

```yaml
language: python
framework: fastapi
architecture:
  type: layered
  layers:
    - name: domain
      source_paths: [src/domain]
      allowed_imports: []
    - name: application
      source_paths: [src/application]
      allowed_imports: [domain]
    - name: infrastructure
      source_paths: [src/infrastructure]
      allowed_imports: [domain, application]
    - name: presentation
      source_paths: [src/api]
      allowed_imports: [application]
```

Edit this file to adjust layer rules. All sub-skills read from it automatically.

---

## Supported Languages

| Language | AST Tool | Test Framework |
|---|---|---|
| Python | `ast` (stdlib) | pytest |
| TypeScript / JS | `ts-morph` | jest / vitest |
| Java | ArchUnit | JUnit5 |
| Kotlin | ArchUnit + Kotest | Kotest |
| C# | Roslyn | xUnit |
| Go | `go/ast` (stdlib) | testing |
| PHP | nikic/PHP-Parser | PHPUnit |
| Rust | `syn` crate | `#[cfg(test)]` |

---

## Violation Types

| Prefix | Types | Severity |
|---|---|---|
| `ARCH` | `LAYER_BOUNDARY`, `CIRCULAR_DEP`, `FAT_CONTROLLER` | error |
| `SOLID` | `SRP`, `OCP`, `LSP`, `ISP`, `DIP` | error / warning |
| `METRICS` | `COMPLEXITY`, `FILE_SIZE_ERROR`, `FILE_SIZE_WARNING`, `GOD_OBJECT`, `LARGE_FUNCTION` | error / warning |
| `API` | `NO_PAGINATION`, `NO_VERSIONING`, `WRONG_STATUS_CODE`, `NO_ENTITY_LINKING`, `NO_TIMEOUT`, `NO_CONTENT_NEGOTIATION` | warning |

---

## License

MIT
