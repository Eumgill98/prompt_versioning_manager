# PVM MCP Server 설계

## 목적

기존 `pvm` CLI(`PVMProject` 퍼사드)를 재사용해 **FastMCP** 기반 MCP 서버를 제공한다.
Claude Code 등 MCP 클라이언트에서 pvm의 프롬프트 버전 관리 기능을 도구(tool)로 직접 호출할 수 있다.

구현 레이어:

```
CLI        → PVMProject → 내부 모듈
MCP server →     ↑ 동일한 경로
```

CLI 호출(subprocess)을 거치지 않는 이유:

- subprocess + stdout JSON 파싱 필요
- 에러가 exit code + stderr 텍스트로 전달되어 처리 복잡
- interactive confirm prompt(`destroy`, `reset`, `delete`)를 subprocess에서 처리 불가

---

## 핵심 설계 원칙

### 1. 프로젝트 루트 바인딩

서버 기동 시 `--root` 옵션으로 특정 경로를 지정할 수 있다. 미지정 시 cwd를 사용한다.

```
project_root = --root 지정값 | cwd (미지정 시)
```

- 지정 경로에 `.pvm/` 프로젝트가 있으면 자동 연결
- 없으면 `init` tool로 생성 필요 (`init` 외 모든 tool은 `NotValidProjectError` 반환)
- clone 후 별도 설정 없이 바로 사용 가능 (기본값 cwd)

`--root` 지정 시 `os.chdir()`로 프로세스 cwd를 변경한다. 이후 모든 tool은 `PVMProject.cwd()`를 그대로 사용한다.

> **주의:** `os.chdir()` 방식은 프로세스 전체 cwd를 변경하므로, 향후 다중 프로젝트를 하나의 서버에서 지원하려면 방식 변경이 필요하다. 현재는 단일 프로젝트만 지원하므로 문제 없다.

### 2. 위험 연산 처리 방침

되돌릴 수 없는 삭제/초기화 연산은 MCP tool로 직접 실행하지 않는다. 대신 터미널에서 실행할 CLI 명령어를 안내하는 guide tool을 제공한다.

| 분류 | 연산 | 방식 |
|------|------|------|
| 직접 실행 | 삭제 제외 모든 연산 | tool로 직접 실행 |
| CLI 안내 | `destroy`, `reset`, `delete_prompt` | 실행 대신 CLI 명령어 안내 |

### 3. `PVMProject` 인스턴스 생성

매 tool 호출마다 `PVMProject.cwd()`를 생성한다. `__init__`이 Path 설정만 하는 가벼운 연산이므로 오버헤드가 없다.

```python
@mcp.tool()
def list_prompts() -> list[str]:
    return PVMProject.cwd().list_prompt_ids()
```

### 4. `add_prompt` 경로 처리

`template_path`는 별도 처리 없이 그대로 전달한다.
MCP 서버의 cwd = project_root이므로, `add.py`의 `template_path.resolve()`가 project_root 기준으로 자동 처리된다.

```python
# 사용 예시 (cwd = project_root)
project.add_prompt("template.yaml")      # project_root/template.yaml
project.add_prompt("prompts/foo.yaml")   # project_root/prompts/foo.yaml
project.add_prompt("/abs/path/foo.yaml") # 절대 경로도 동작
```

### 5. `add_prompt` 템플릿 무결성 검증

`add_prompt` tool은 퍼사드 호출 전, 입력 YAML 파일에 필수 필드가 있는지 사전 검증한다.

| 필드 | 조건 |
|------|------|
| `id` | 비어있지 않은 문자열, 공백·`/` 불가 |
| `llm` | 비어있지 않은 dict (`provider`, `model` 등 포함) |
| `prompt` | 비어있지 않은 문자열 |

선택 필드: `description`, `author`, `input_variables`

검증 실패 시 `ValueError`를 반환한다.

### 6. `export_snapshot` 저장 경로

라이브러리 기본값을 MCP 서버 레이어에서 덮어쓴다.

| 상황 | 저장 경로 |
|------|-----------|
| `output_path` 미지정 | `project_root/export_snapshots/snapshot-{version}.zip` |
| `output_path` 지정 | cwd 기준 resolve (cwd = project_root이므로 동일) |

`export_snapshots/` 폴더가 없을 수 있으므로 zip 저장 전 자동 생성한다.

---

## 에러 처리

| 예외 타입 | 대상 | 예시 |
|-----------|------|------|
| `ToolError` | `PVMError` 계열 — 예상 가능한 도메인 에러 | `PromptNotFoundError`, `VersionNotFoundError`, `AlreadyInitializedError` |
| `ValueError` | 잘못된 입력 파라미터 | 유효하지 않은 `bump_level`, 필수 필드 누락 |

```python
from fastmcp.exceptions import ToolError
from pvm.core.errors import PVMError

@mcp.tool()
def get_prompt(prompt_id: str, version: str | None = None) -> dict:
    try:
        return PVMProject.cwd().get_prompt(prompt_id, version=version)
    except PVMError as e:
        raise ToolError(str(e))
```

---

## Tool 목록

### 프로젝트 관리

```python
check_integrity() -> dict
# .pvm/ 디렉토리 구조 검사

init(name: str = "my-project") -> dict
# 프로젝트 초기화 — 이미 존재하면 AlreadyInitializedError(ToolError)

load_config() -> dict
# .pvm/config.yaml 로드 (name, project_id 등)

load_template() -> dict
# 기본 템플릿 구조 조회 — 유저가 파일명만 주면 Claude가 이 구조에 맞춰 yaml 파일 구성

guide_destroy() -> str
# 프로젝트 영구 삭제 CLI 명령어 안내

guide_reset() -> str
# 프로젝트 초기화 CLI 명령어 안내
```

### 프롬프트 관리

```python
list_prompts() -> list[str]
# 전체 prompt ID 목록

list_prompt_versions(prompt_id: str) -> list[str]
# 특정 prompt_id의 버전 목록

get_prompt(prompt_id: str, version: str | None = None) -> dict
# version 지정 → 해당 버전
# version 미지정 → production 버전 → (없으면) 최신 버전 순으로 fallback
# 반환: {id, version, llm, prompt,
#         metadata: {id, version, description, author,
#                    created_at, source_file,
#                    prompt_checksum, model_config_checksum, template_checksum}}

get_prompt_info(prompt_id: str) -> dict
# 반환: {id,
#         info: {id, description, author, created_at},
#         versions: [...], latest_version,
#         production: {id, version, previous_versions: [...], updated_at} | None}

add_prompt(template_path: str, bump_level: str = "patch") -> dict
# bump_level: "patch"(기본, 0.1.0→0.1.1) | "minor"(0.1.1→0.2.0) | "major"(0.2.0→1.0.0)
# id 없음 → 신규 생성, 초기 버전 0.1.0
# id 있음 → SHA-256 체크섬 비교
#   동일 → no-op {"changed": False, "reason": "no_changes"}
#   다름 → 버전 증가 {"changed": True, "version": "..."}

deploy_prompt(prompt_id: str, version: str | None = None) -> dict
# version 미지정 → 최신 버전 자동 배포
# 이미 배포된 버전 → no-op {"changed": False, "reason": "already_deployed"}
# 반환: {id, version, changed, from_version}  # 최초 배포 시 from_version = None

rollback_prompt(prompt_id: str) -> dict
# 이전 production 없음 → {"changed": False, "reason": "no_rollback_target"}
# 반환: {id, changed, from_version, to_version}

diff_prompt(prompt_id: str, from_version: str, to_version: str) -> dict
# 반환: {id, from_version, to_version, changed,
#         prompt_length_delta, lines_added, lines_removed,
#         model_config_changed, checksum_from, checksum_to,
#         unified_diff}  # 변경 없으면 unified_diff = "(no changes)"

guide_delete_prompt(prompt_id: str) -> str
# 프롬프트 삭제 CLI 명령어 안내
```

### 스냅샷 관리

```python
list_snapshots() -> list[str]
# 스냅샷 버전 목록

get_snapshot(version: str) -> dict
# 메타 정보만 조회 (프롬프트 내용 미포함)
# 반환: {version, created_at, snapshot_checksum, prompt_count,
#         prompts: {id: {version, prompt_checksum, model_config_checksum}, ...}}

read_snapshot(version: str) -> dict
# 전체 내용 조회 (프롬프트 내용 포함)
# 반환: {version, created_at, snapshot_checksum, prompt_count,
#         prompts: {id: {version, llm, prompt, metadata: {...}}, ...}}

create_snapshot(bump_level: str = "patch") -> dict
# 현재 production 프롬프트를 묶어 스냅샷으로 버저닝
# bump_level: "patch"(기본) | "minor" | "major"
# 반환: {version, created_at, snapshot_checksum, prompt_count,
#         prompts: {id: {version, prompt_checksum, model_config_checksum}, ...}}

export_snapshot(version: str, output_path: str | None = None) -> dict
# 기본 저장 경로: project_root/export_snapshots/snapshot-{version}.zip
# output_path 지정 시: cwd 기준 resolve
# 반환: {version, output_path}
# zip 내부 구조:
#   manifest.json
#   prompts/
#     {id}/
#       prompt.md
#       model_config.json
#       metadata.json

diff_snapshots(from_version: str, to_version: str) -> dict
# 반환: {from_version, to_version,
#         added_ids: [...], removed_ids: [...],
#         changed_ids: [{id, from_version, to_version}, ...]}
```

---

## 파일 구조

```text
pvm/
  mcp/
    __init__.py
    server.py        # FastMCP 인스턴스, main() 진입점
    tools/
      __init__.py
      project.py     # check_integrity, init, load_config, load_template,
                     # guide_destroy, guide_reset
      prompts.py     # list_prompts, list_prompt_versions, get_prompt,
                     # get_prompt_info, add_prompt, deploy_prompt,
                     # rollback_prompt, diff_prompt, guide_delete_prompt
      snapshots.py   # list_snapshots, get_snapshot, read_snapshot,
                     # create_snapshot, export_snapshot, diff_snapshots
```

---

## 진입점 (`server.py`)

```python
import argparse
import os
from fastmcp import FastMCP

mcp = FastMCP("pvm-mcp")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=None, help="pvm 프로젝트 경로 (기본값: cwd)")
    args = parser.parse_args()

    if args.root:
        os.chdir(args.root)

    import pvm.mcp.tools.project   # noqa: F401
    import pvm.mcp.tools.prompts   # noqa: F401
    import pvm.mcp.tools.snapshots # noqa: F401

    mcp.run(transport="stdio")
```

tool 모듈은 `main()` 내부에서 import해 `@mcp.tool()` 데코레이터가 `mcp` 인스턴스에 등록되도록 한다.

---

## FastMCP tool 등록 방식

각 모듈에서 `mcp` 인스턴스를 import해 `@mcp.tool()` 데코레이터를 직접 사용한다.

```python
# pvm/mcp/tools/prompts.py
from pvm.mcp.server import mcp

@mcp.tool()
def list_prompts() -> list[str]:
    ...
```

---

## `pyproject.toml` 등록

```toml
[project.scripts]
pvm-mcp = "pvm.mcp.server:main"
```
