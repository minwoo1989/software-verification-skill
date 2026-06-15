# software-verification-skill

[English](README.md)

소프트웨어 구조적 무결성을 검증하고 CI에서 영구적으로 강제되는 아키텍처 테스트를 생성하는 Claude Code 플러그인입니다.

SOLID 원칙 위반, 레이어 경계 침범, 순환 의존성, 순환 복잡도, REST API 안티패턴을 탐지하고 — 구조 회귀 시 빌드를 실패시키는 테스트 파일을 직접 작성합니다.

---

## 설치

**1단계 — 마켓플레이스 추가**

```
/plugin marketplace add https://github.com/minwoo1989/software-verification-skill
```

**2단계 — 플러그인 설치**

```
/plugin install software-verification-skill
```

---

## 스킬 목록

| 스킬 | 호출 방법 | 설명 |
|---|---|---|
| `verify-structure` | `/svs:verify-structure` | 진입점 — 감지·확인·조율·리포트·테스트 생성 |
| `solid` | `/svs:solid` | SOLID 원칙 위반 (SRP, OCP, LSP, ISP, DIP) |
| `architecture` | `/svs:architecture` | 레이어 경계·순환 의존성·Fat Controller |
| `metrics` | `/svs:metrics` | 순환 복잡도·파일 크기·God Object |
| `api-design` | `/svs:api-design` | REST 안티패턴 6종 |

---

## 사용법

### 빠른 시작

프로젝트 루트에서 진입점 스킬을 실행합니다:

```
/svs:verify-structure
```

**첫 실행 시 Claude가 수행하는 작업:**
1. 매니페스트 파일을 파싱해 언어·프레임워크 감지
2. 아키텍처 레이어 구조 제안 (예: 클린 아키텍처, MVC)
3. 규칙 적용 전 사용자 확인
4. `.verify-structure.yml` 생성 (팀 공유용 — git 커밋 권장)
5. 관련 서브스킬 실행 후 위반 사항 리포트
6. CI 강제 테스트 파일 생성 제안

**재실행 시:** `.verify-structure.yml`을 읽고 감지 단계 건너뜀 → 바로 분석 시작

### 출력 예시

```
── Structural Issues Found ───────────────────────────────
[error]   src/domain/user.py:3
          ARCH.LAYER_BOUNDARY — domain이 infrastructure.db를 import
          Fix: domain에 UserRepository 인터페이스 정의 후 생성자 주입

[warning] src/application/user_service.py:4
          METRICS.COMPLEXITY — process() 복잡도=11 (임계값: 10)
          Fix: 중첩 조건을 가드 절로 분리
──────────────────────────────────────────────────────────
1 error, 1 warning

Generate architecture tests to enforce these rules in CI? [Y/n]
```

### 생성되는 테스트 파일

승인 후 테스트 파일이 프로젝트에 영구 저장됩니다:

```
tests/architecture/test_layer_boundaries.py  ← ARCH 위반
tests/architecture/test_solid.py             ← SOLID 위반
tests/architecture/test_metrics.py           ← 메트릭 위반
tests/architecture/test_api_design.py        ← API 설계 위반
```

이후 모든 CI 빌드에서 위반 시 빌드가 실패합니다.

### 서브스킬 단독 실행

```
/svs:metrics        ← 복잡도·파일 크기·God Object
/svs:solid          ← SOLID 원칙 위반
/svs:architecture   ← 레이어 경계·순환 의존성·Fat Controller
/svs:api-design     ← REST 안티패턴 6종
```

---

## 설정

첫 실행 시 `.verify-structure.yml`이 프로젝트 루트에 생성됩니다:

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

레이어 규칙은 이 파일을 직접 수정해 조정합니다. 모든 서브스킬이 자동으로 읽습니다.

---

## 플러그인 구조

```
skills/
  verify-structure/    → /svs:verify-structure  (진입점)
  solid/               → /svs:solid
  metrics/             → /svs:metrics
  architecture/        → /svs:architecture
  api-design/          → /svs:api-design
  findings-schema/     → /svs:findings-schema
  language-adapters/   → /svs:language-adapters
  test-generator/      → /svs:test-generator
```

---

## 지원 언어

| 언어 | AST 도구 | 테스트 프레임워크 |
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

## 위반 타입

| 접두사 | 타입 | 심각도 |
|---|---|---|
| `ARCH` | `LAYER_BOUNDARY`, `CIRCULAR_DEP`, `FAT_CONTROLLER` | error |
| `SOLID` | `SRP`, `OCP`, `LSP`, `ISP`, `DIP` | error / warning |
| `METRICS` | `COMPLEXITY`, `FILE_SIZE_ERROR`, `FILE_SIZE_WARNING`, `GOD_OBJECT`, `LARGE_FUNCTION` | error / warning |
| `API` | `NO_PAGINATION`, `NO_VERSIONING`, `WRONG_STATUS_CODE`, `NO_ENTITY_LINKING`, `NO_TIMEOUT`, `NO_CONTENT_NEGOTIATION` | warning |

---

## 라이선스

MIT
