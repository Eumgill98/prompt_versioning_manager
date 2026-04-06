# PVM MCP Server Implementation Status

이 문서는 `DESIGN_MCP.md` 기준 MCP 서버 구현 결과를 현재 코드 상태로 요약한 것이다.

## 현재 상태

- MCP 서버 구현 완료
- 패키지 레이아웃은 `pvm/mcp/`
- FastMCP 기반 stdio 서버
- 기존 `PVMProject` 퍼사드 직접 호출

## 구현 완료 범위

### 1. 사전 준비

완료:

- [x] `fastmcp>=3.2.0` 의존성 확인 (core dependency로 이미 포함)
- [x] `pyproject.toml`에 `pvm-mcp` entry point 추가

결과:

```toml
[project.scripts]
pvm        = "pvm.cli:main"
pvm-server = "server.main:main"
pvm-mcp    = "pvm.mcp.server:main"
```

`[tool.setuptools.packages.find]`의 `pvm*` 패턴에 `pvm/mcp/`가 자동 포함되므로 별도 변경 불필요.

### 2. 패키지 골격

완료:

- [x] `pvm/mcp/__init__.py`
- [x] `pvm/mcp/server.py`
- [x] `pvm/mcp/tools/__init__.py`
- [x] `pvm/mcp/tools/project.py`
- [x] `pvm/mcp/tools/prompts.py`
- [x] `pvm/mcp/tools/snapshots.py`

결과:

- `pvm-mcp` CLI 명령 사용 가능
- `pvm-mcp --root /path/to/project` 경로 지정 가능

### 3. 서버 진입점 (`server.py`)

완료:

- [x] `FastMCP("pvm-mcp")` 인스턴스 생성
- [x] `--root` argparse 처리 (`os.chdir()` 방식)
- [x] tool 모듈 side-effect import
- [x] `mcp.run(transport="stdio")` 기동

### 4. 프로젝트 관리 tools (`project.py`)

완료:

- [x] `check_integrity` — `.pvm/` 구조 검사
- [x] `init` — 프로젝트 초기화 (이미 존재하면 `ToolError`)
- [x] `load_config` — `.pvm/config.yaml` 로드
- [x] `load_template` — 기본 템플릿 구조 조회
- [x] `guide_destroy` — `pvm destroy` CLI 명령 안내 문자열 반환
- [x] `guide_reset` — `pvm reset` CLI 명령 안내 문자열 반환

에러 처리:

- `PVMError` 계열 → `ToolError`
- `guide_*`: 실행 없이 CLI 안내 문자열만 반환

### 5. 프롬프트 관리 tools (`prompts.py`)

완료:

- [x] `list_prompts` — 전체 prompt ID 목록
- [x] `list_prompt_versions` — 특정 prompt의 버전 목록
- [x] `get_prompt` — 프롬프트 조회 (production → latest fallback)
- [x] `get_prompt_info` — 프롬프트 메타 정보 및 버전 요약
- [x] `add_prompt` — YAML 템플릿으로 새 버전 생성 (사전 검증 포함)
- [x] `deploy_prompt` — production 승격 (version 생략 시 latest)
- [x] `rollback_prompt` — 이전 production으로 롤백
- [x] `diff_prompt` — 두 버전 간 diff
- [x] `guide_delete_prompt` — `pvm delete <id>` CLI 명령 안내 문자열 반환

`add_prompt` 사전 검증:

- `load_yaml`로 파일 읽기 실패 → `ValueError`
- `id`, `llm`, `prompt` 필수 필드 누락 → `ValueError`
- `llm`이 비어있지 않은 dict가 아닐 경우 → `ValueError`
- `bump_level`은 `Literal["patch", "minor", "major"]` 타입으로 처리 (별도 검증 불필요)

확인된 사항:

- `load_yaml` 위치: `pvm/storage/yaml_io.py`
- `PVMProject.get_prompt()` fallback 동작: `pvm/prompts/get.py`에 production → latest 구현 확인. tool 내 추가 처리 불필요
- `PVMProject.deploy` / `PVMProject.rollback` 메서드명: facade는 suffix 없음. MCP tool명은 `deploy_prompt`, `rollback_prompt`

### 6. 스냅샷 관리 tools (`snapshots.py`)

완료:

- [x] `list_snapshots` — 스냅샷 버전 목록
- [x] `get_snapshot` — 스냅샷 메타 정보 조회 (프롬프트 내용 미포함)
- [x] `read_snapshot` — 스냅샷 전체 내용 조회 (프롬프트 내용 포함)
- [x] `create_snapshot` — 현재 production 프롬프트로 스냅샷 생성
- [x] `export_snapshot` — ZIP 내보내기 (`export_snapshots/snapshot-{version}.zip` 자동 저장)
- [x] `diff_snapshots` — 두 스냅샷 비교

`export_snapshot` 처리:

- `output_path` 미지정 시: `project_root/export_snapshots/snapshot-{version}.zip`
- `output_path` 지정 시: cwd 기준 resolve
- 저장 전 `resolved.parent.mkdir(parents=True, exist_ok=True)` 자동 호출

확인된 사항:

- `PVMProject.diff_snapshot` (단수): facade 메서드명. MCP tool명은 `diff_snapshots` (복수)로 유지하고 내부에서 `diff_snapshot` 호출

### 7. `.mcp.json` 연동

완료:

- [x] WSL 환경 `.mcp.json` 등록 (`run_pvm_mcp.sh` 경유)
- [x] `run_pvm_mcp.sh` 작성 (`uv` 탐색 → `pvm-mcp` 폴백)

현재 동작:

```json
{
  "mcpServers": {
    "pvm": {
      "type": "stdio",
      "command": "wsl",
      "args": ["bash", "-lc", "./run_pvm_mcp.sh"]
    }
  }
}
```

## 현재 문서 기준 참고

- 설계: `DESIGN_MCP.md`
- 사용자 개요 (한국어): `README_MCP_KO.md`
- 사용자 개요 (영어): `README_MCP_EN.md`
