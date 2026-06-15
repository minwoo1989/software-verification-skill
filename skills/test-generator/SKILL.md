---
name: test-generator
description: Use when converting structural violation findings into permanent architecture test files for CI enforcement
---

# Test Generator

Converts findings from verify-* sub-skills into actual test files written to the project.

**REQUIRED REFERENCE:** Read `svs:language-adapters` to determine test framework and file location.

## Process

1. **Determine test location:**
   - Run language-adapters detection order (parse project config → convention → ask user)
   - Present the resolved path: "Architecture tests will be written to `tests/architecture/`. Correct?"

2. **Group findings by `violation_type` prefix:**
   - `ARCH.*` → `test_layer_boundaries.py`
   - `SOLID.*` → `test_solid.py`
   - `METRICS.*` → `test_metrics.py`
   - `API.*` → `test_api_design.py`

3. **Generate one test function per unique `violation_type`** (not per finding instance):
   - The generated test catches the class of violation, not just the specific instance
   - Use the pattern from the relevant verify-* skill
   - Parameterize with values from `.verify-structure.yml` (layer paths, thresholds)

4. **Handle existing files:**
   - If a test file already exists, append new test functions only
   - If a function name collision exists (same `test_` name), ask: "Skip, rename as `test_X_v2`, or replace?"

5. **Show preview before writing:**
   ```
   Files to generate:
     tests/architecture/test_layer_boundaries.py  ← ARCH.LAYER_BOUNDARY, ARCH.FAT_CONTROLLER
     tests/architecture/test_solid.py             ← SOLID.DIP, SOLID.SRP
     tests/architecture/test_metrics.py           ← METRICS.COMPLEXITY, METRICS.FILE_SIZE_ERROR
   
   Additional dependencies needed: none (Python ast is stdlib)
   
   Proceed?
   ```

6. **After writing:** Print the exact command to run immediately:
   ```
   pytest tests/architecture/ -v
   ```
   And confirm: "From the next PR, these rules will fail CI if violated."

## What Not to Do

- Do NOT write tests that hard-code specific file names or line numbers found in the current scan. Tests must catch the violation CLASS, not the specific instance.
- Do NOT generate test code with `# TODO` or placeholder comments.
- Do NOT overwrite existing test functions silently.
- Do NOT add dependencies that are not in the language adapter table without asking.

## Output Confirmation

After writing files, report:
```
Generated:
  tests/architecture/test_layer_boundaries.py  (2 test functions)
  tests/architecture/test_solid.py             (2 test functions)
  tests/architecture/test_metrics.py           (3 test functions)

Run: pytest tests/architecture/ -v
```
