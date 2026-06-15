---
name: verify-api-design
description: Use when verifying REST API design quality in a web backend codebase — detects missing pagination, versioning, incorrect status codes, and other anti-patterns
---

# Verify API Design

Detects REST API anti-patterns based on the 6 patterns validated by the PTIDEJ group (ICSOC 2021). Runs when the framework is a web server (Django, FastAPI, Spring, Express, NestJS, etc.).

**REQUIRED REFERENCE:** Read `verify:findings-schema` and `verify:language-adapters`.

## The 6 Anti-patterns

### 1. Missing List Pagination (`API.NO_PAGINATION`)
**Rule:** Any route handler for a collection endpoint (GET on a plural resource path, or path ending in `/`) must accept at least one of: `limit`, `offset`, `page`, `page_size`, `per_page`, `cursor`.
**Detection:** Parse route handler signatures (function parameters / query param declarations).
**Severity:** warning

### 2. Missing API Versioning (`API.NO_VERSIONING`)
**Rule:** All route paths must include a version prefix matching `/v{digit}/` or `/api/v{digit}/`.
**Detection:** Scan route path strings in route registration code.
**Severity:** warning

### 3. Incorrect POST/PUT/PATCH Return (`API.WRONG_STATUS_CODE`)
**Rule:** POST handlers should return 201. PUT and PATCH handlers should return 200 or 204.
**Detection:** Check explicit status code in response objects or route decorators.
**Severity:** warning
**Note:** Only flag if status code is explicitly set to a wrong value — do not flag if implicit (framework default).

### 4. Missing Entity Linking (`API.NO_ENTITY_LINKING`)
**Rule:** Response objects for individual resources should include a `url`, `href`, `_links`, or `self` field pointing to the resource's canonical URL.
**Detection:** Check response dict/schema definitions for link fields.
**Severity:** warning
**Note:** Only flag when response is a plain dict with an `id` field and no link field — do not flag implicit framework serialization.

### 5. Missing Server Timeout (`API.NO_TIMEOUT`)
**Rule:** HTTP client calls within the codebase should have an explicit timeout parameter.
**Detection:** Scan for `requests.get/post/put/delete/patch()`, `httpx.get()`, `aiohttp` calls — flag if no `timeout=` argument present.
**Severity:** warning

### 6. Missing Content Negotiation (`API.NO_CONTENT_NEGOTIATION`)
**Rule:** Routes that return data should declare supported content types.
**Detection:** Check for `Accept` header handling or `response_model` / `produces` annotations.
**Severity:** warning
**Note:** Frameworks like FastAPI implicitly handle JSON. Flag only when multiple content types are expected but no negotiation exists.

## Python (FastAPI) Route Scan Pattern

```python
import ast
from pathlib import Path

def _route_handlers(src_root="src"):
    handlers = []
    for py_file in Path(src_root).rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Attribute):
                        method = decorator.attr  # get, post, put, patch, delete
                        if method in ("get", "post", "put", "patch", "delete"):
                            handlers.append((py_file, node, method))
    return handlers

def test_list_endpoints_have_pagination():
    violations = []
    PAGINATION_PARAMS = {"limit", "offset", "page", "page_size", "per_page", "cursor"}
    for py_file, func, method in _route_handlers():
        if method != "get":
            continue
        arg_names = {a.arg for a in func.args.args}
        is_list = func.name.startswith("list_") or func.name.startswith("get_all")
        if is_list and not arg_names & PAGINATION_PARAMS:
            violations.append(f"{py_file}:{func.lineno} {func.name}() — no pagination param")
    assert not violations, "Missing pagination:\n" + "\n".join(violations)

def test_routes_have_version_prefix():
    violations = []
    import re
    for py_file in Path("src").rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "APIRouter":
                    for kw in node.keywords:
                        if kw.arg == "prefix" and isinstance(kw.value, ast.Constant):
                            prefix = kw.value.value
                            if not re.search(r"/v\d+", prefix):
                                violations.append(
                                    f"{py_file}: APIRouter prefix '{prefix}' has no version"
                                )
    assert not violations, "Missing API versioning:\n" + "\n".join(violations)
```
