---
name: language-adapters
description: Use when implementing a verify-* skill and you need to know which AST tool, test framework, or default file location to use for a given programming language
---

# Language Adapters

Reference for language-specific tooling. All verify-* sub-skills read from here — never hardcode language logic inside a sub-skill.

## Detection Order (per project)

1. **Parse project config** for actual test settings:
   - Python: `pytest.ini` or `[tool.pytest.ini_options]` in `pyproject.toml` → `testpaths`
   - JS/TS: `jest.config.js` or `vitest.config.ts` / `vitest.config.js` → `testMatch` / `include`
   - Java: `pom.xml` → `<testSourceDirectory>` or `build.gradle` → `test.sourceSet`
2. **Fall back** to language convention if not found (see table below)
3. **Ask user** if ambiguous: "Where should I generate architecture tests? (default: `tests/architecture/`)"

## Language Table

| Language | AST / Analysis Tool | Test Framework | Default Test Location | Extra Dep Needed? |
|---|---|---|---|---|
| Python | `ast` (stdlib) | `pytest` | `tests/architecture/` | No |
| TypeScript / JS | `ts-morph` | `jest` or `vitest` | `src/__tests__/architecture/` | `npm i -D ts-morph` |
| Java | `ArchUnit` (bytecode) | `JUnit5` | `src/test/java/architecture/` | Add to `pom.xml` / `build.gradle` |
| Kotlin | `ArchUnit` + `Kotest` | `Kotest` | `src/test/kotlin/architecture/` | Add ArchUnit to build |
| C# | `Roslyn` (Microsoft.CodeAnalysis) | `xUnit` | `tests/Architecture/` | NuGet: `Microsoft.CodeAnalysis.CSharp` |
| Go | `go/ast` (stdlib) | `testing` | `*_arch_test.go` alongside source | No |
| PHP | `nikic/PHP-Parser` | `PHPUnit` | `tests/Architecture/` | `composer require nikic/php-parser` |
| Rust | `syn` crate | `#[cfg(test)]` | inline `mod tests` in `src/lib.rs` | Add `syn` to `dev-dependencies` |

## ArchUnit Dependency Snippet (Java / Maven)

```xml
<dependency>
  <groupId>com.tngtech.archunit</groupId>
  <artifactId>archunit-junit5</artifactId>
  <version>1.3.0</version>
  <scope>test</scope>
</dependency>
```

## ts-morph Import Graph Example

```typescript
import { Project } from "ts-morph";
const project = new Project({ tsConfigFilePath: "tsconfig.json" });
const sourceFiles = project.getSourceFiles();
// sourceFiles[i].getImportDeclarations() → build import graph
```

## Go ast Example

```go
import (
    "go/ast"
    "go/parser"
    "go/token"
)
fset := token.NewFileSet()
node, _ := parser.ParseFile(fset, "file.go", nil, 0)
ast.Inspect(node, func(n ast.Node) bool {
    if imp, ok := n.(*ast.ImportSpec); ok {
        // imp.Path.Value is the imported package path
    }
    return true
})
```
