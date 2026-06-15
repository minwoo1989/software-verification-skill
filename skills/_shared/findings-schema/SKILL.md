---
name: findings-schema
description: Use when building or extending a verify-* skill and you need the shared findings JSON format for inter-skill communication
---

# Findings Schema

Reference for the structured findings format shared across all verify-* skills.

## Schema

Each finding is a JSON object:

```json
{
  "violation_type": "ARCH.LAYER_BOUNDARY",
  "severity": "error",
  "file": "src/domain/user.py",
  "line": 3,
  "description": "Domain layer imports from Infrastructure layer (infrastructure.db)",
  "suggested_fix": "Define a UserRepository abstract interface in domain; implement it in infrastructure"
}
```

## violation_type Values

`violation_type` format: `<Prefix>.<Value>` (e.g. `ARCH.LAYER_BOUNDARY`, `SOLID.SRP`, `METRICS.COMPLEXITY`)

| Prefix | Values | Severity |
|---|---|---|
| `ARCH` | `LAYER_BOUNDARY`, `CIRCULAR_DEP`, `FAT_CONTROLLER` | error |
| `SOLID` | `SRP`, `OCP`, `LSP`, `ISP`, `DIP` | error or warning (thresholds defined in verify-solid SKILL.md) |
| `METRICS` | `COMPLEXITY`, `FILE_SIZE_ERROR`, `FILE_SIZE_WARNING`, `GOD_OBJECT`, `LARGE_FUNCTION` | warning or error (thresholds defined in verify-metrics SKILL.md) |
| `API` | `NO_PAGINATION`, `NO_VERSIONING`, `WRONG_STATUS_CODE`, `NO_ENTITY_LINKING`, `NO_TIMEOUT`, `NO_CONTENT_NEGOTIATION` | warning |

## Severity Rules

- `error` → fails CI, blocks PR merge
- `warning` → printed to console, does not fail test

## Output

Sub-skills return findings as a JSON array. The entry skill (`verify-structure`) collects all arrays, deduplicates by `(file, line, violation_type)`, and displays a grouped report.
