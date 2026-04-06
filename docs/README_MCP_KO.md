# pvm MCP Server

`pvm-mcp`는 pvm의 프롬프트 버전 관리 기능을 MCP(Model Context Protocol) 도구로 노출하는 서버입니다.

제공 기능:

- 프로젝트 초기화 및 설정 도구
- 프롬프트 추가 / 조회 / 배포 / 롤백 / 비교 도구
- 스냅샷 생성 / 조회 / 내보내기 / 비교 도구
- FastMCP 기반 `stdio` 전송

## 셋업 순서

처음 사용하는 경우 아래 방법 중 하나를 따릅니다.

### uv (권장)

```bash
# 1. 저장소 클론
git clone https://github.com/Eumgill98/prompt_versioning_manager.git
cd REPO

# 2. uv 설치 (이미 설치되어 있으면 생략)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. 서버 실행 확인
uv run pvm-mcp --help
```

### pipx

```bash
# 1. 저장소 클론
git clone https://github.com/Eumgill98/prompt_versioning_manager.git
cd REPO

# 2. pipx 설치 (이미 설치되어 있으면 생략)
pip install pipx
pipx ensurepath

# 3. pvm-mcp 설치
pipx install ".[server]"

# 4. 서버 실행 확인
pvm-mcp --help
```

### Poetry (로컬 개발)

```bash
# 1. 저장소 클론
git clone https://github.com/Eumgill98/prompt_versioning_manager.git
cd REPO

# 2. 의존성 설치
poetry install -E server

# 3. 서버 실행 확인
poetry run pvm-mcp --help
```

Claude Code에서 사용하려면 프로젝트 루트의 `.mcp.json`을 등록합니다. 자세한 내용은 아래 [Claude Code 연동](#claude-code-연동) 섹션을 참고하세요.

---

## 설치

### 권장: `uv`

별도 설치 없이 프로젝트 루트에서 바로 실행합니다.

```bash
uv run pvm-mcp
```

### `pipx`

`server` extra를 포함해 설치합니다.

```bash
pipx install ".[server]"
pvm-mcp
```

### Poetry (로컬 개발)

```bash
poetry install -E server
poetry run pvm-mcp
```

## Claude Code 연동

프로젝트 루트에 `.mcp.json` 파일을 생성합니다. OS와 Python 환경에 따라 설정이 다릅니다.

> **`/path/to/repo`** 는 실제 저장소 절대 경로로 대체하세요.
> Windows 예시: `C:/Users/yourname/repos/prompt_versioning_manager`
> Linux/Mac 예시: `/home/yourname/repos/prompt_versioning_manager`

---

### Windows (네이티브, WSL 미사용)

Claude Code가 Windows 네이티브 환경에서 실행될 때의 설정입니다.

#### 일반 환경 (venv / 전역 pip)

```json
{
  "mcpServers": {
    "pvm": {
      "type": "stdio",
      "command": "C:/path/to/venv/Scripts/python.exe",
      "args": ["-m", "pvm.mcp.server"],
      "cwd": "C:/path/to/repo"
    }
  }
}
```

> 전역 pip로 설치한 경우 `command`를 `python`으로, 가상환경을 사용한다면 해당 venv의 `python.exe` 절대 경로로 지정합니다.

#### pipx

```json
{
  "mcpServers": {
    "pvm": {
      "type": "stdio",
      "command": "pvm-mcp",
      "cwd": "C:/path/to/repo"
    }
  }
}
```

> `pipx install ".[server]"` 후 `pvm-mcp`가 전역 명령으로 등록됩니다.

#### uv

```json
{
  "mcpServers": {
    "pvm": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "pvm-mcp"],
      "cwd": "C:/path/to/repo"
    }
  }
}
```

#### poetry

```json
{
  "mcpServers": {
    "pvm": {
      "type": "stdio",
      "command": "poetry",
      "args": ["run", "pvm-mcp"],
      "cwd": "C:/path/to/repo"
    }
  }
}
```

---

### Windows + WSL

Claude Code가 Windows에서 실행되지만 WSL 내부의 Python 환경을 사용할 때의 설정입니다.
`command`는 항상 `wsl`이고, 실제 실행 방식은 `args`에서 결정됩니다.

> WSL 경로 예시: `/home/yourname/repos/prompt_versioning_manager`

#### 일반 환경 (venv / 전역 pip)

```json
{
  "mcpServers": {
    "pvm": {
      "type": "stdio",
      "command": "wsl",
      "args": ["bash", "-lc", "cd /path/to/repo && .venv/bin/python -m pvm.mcp.server"]
    }
  }
}
```

> 전역 pip로 설치한 경우 `.venv/bin/python` 대신 `python3`을 사용합니다.

#### pipx

```json
{
  "mcpServers": {
    "pvm": {
      "type": "stdio",
      "command": "wsl",
      "args": ["bash", "-lc", "pvm-mcp"]
    }
  }
}
```

#### uv

```json
{
  "mcpServers": {
    "pvm": {
      "type": "stdio",
      "command": "wsl",
      "args": ["bash", "-lc", "cd /path/to/repo && uv run pvm-mcp"]
    }
  }
}
```

`run_pvm_mcp.sh` 헬퍼 스크립트를 사용하면 uv → pipx 순으로 자동 탐색합니다.

```json
{
  "mcpServers": {
    "pvm": {
      "type": "stdio",
      "command": "wsl",
      "args": ["bash", "-lc", "/path/to/repo/run_pvm_mcp.sh"]
    }
  }
}
```

#### poetry

```json
{
  "mcpServers": {
    "pvm": {
      "type": "stdio",
      "command": "wsl",
      "args": ["bash", "-lc", "cd /path/to/repo && poetry run pvm-mcp"]
    }
  }
}
```

---

### Linux / macOS

#### 일반 환경 (venv / 전역 pip)

```json
{
  "mcpServers": {
    "pvm": {
      "type": "stdio",
      "command": "/path/to/repo/.venv/bin/python",
      "args": ["-m", "pvm.mcp.server"],
      "cwd": "/path/to/repo"
    }
  }
}
```

> 전역 pip로 설치한 경우 `command`를 `python3`으로 지정합니다.

#### pipx

```json
{
  "mcpServers": {
    "pvm": {
      "type": "stdio",
      "command": "pvm-mcp",
      "cwd": "/path/to/repo"
    }
  }
}
```

#### uv

```json
{
  "mcpServers": {
    "pvm": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "pvm-mcp"],
      "cwd": "/path/to/repo"
    }
  }
}
```

#### poetry

```json
{
  "mcpServers": {
    "pvm": {
      "type": "stdio",
      "command": "poetry",
      "args": ["run", "pvm-mcp"],
      "cwd": "/path/to/repo"
    }
  }
}
```

---

### `run_pvm_mcp.sh`

WSL 설정에서 사용하는 헬퍼 스크립트입니다. `uv`를 자동으로 탐색하고, 없으면 전역 설치된 `pvm-mcp`로 폴백합니다.

## 빠른 시작

프로젝트 초기화 및 프롬프트 추가:

```
1. mcp__pvm__init
2. mcp__pvm__load_template      ← 템플릿 확인 후 YAML 파일 작성
3. mcp__pvm__add_prompt         (template_path: "prompt.yaml")
4. mcp__pvm__deploy_prompt      (prompt_id: "intent_classifier")
5. mcp__pvm__create_snapshot
```

프롬프트 조회 및 비교:

```
1. mcp__pvm__list_prompts
2. mcp__pvm__list_prompt_versions   (prompt_id: "intent_classifier")
3. mcp__pvm__get_prompt             (prompt_id: "intent_classifier")
4. mcp__pvm__diff_prompt            (prompt_id: "intent_classifier", from_version: "0.1.0", to_version: "0.2.0")
```

스냅샷 내보내기:

```
1. mcp__pvm__list_snapshots
2. mcp__pvm__export_snapshot    (version: "0.1.0")
   → export_snapshots/snapshot-0.1.0.zip 에 저장됨
```

## 도구 목록

도구는 `mcp__pvm__<tool_name>` 형태로 호출됩니다.

### 프로젝트

- `init [name]` — 현재 디렉토리에 pvm 프로젝트 초기화
- `check_integrity` — `.pvm/` 디렉토리 구조 무결성 확인
- `load_config` — `.pvm/config.yaml` 로드
- `load_template` — 기본 프롬프트 템플릿 로드
- `guide_destroy` — 프로젝트 영구 삭제 CLI 안내 반환
- `guide_reset` — 프로젝트 초기화 CLI 안내 반환

`guide_destroy`와 `guide_reset`은 되돌릴 수 없는 작업이므로 MCP 도구로 직접 실행하지 않습니다. 터미널에서 실행할 `pvm` CLI 명령어를 안내합니다.

### 프롬프트

- `list_prompts` — 전체 prompt ID 목록 조회
- `list_prompt_versions <prompt_id>` — 특정 prompt의 버전 목록 조회
- `get_prompt <prompt_id> [version]` — 프롬프트 조회 (production → latest 순 fallback)
- `get_prompt_info <prompt_id>` — 메타 정보 및 버전 요약 조회
- `add_prompt <template_path> [bump_level]` — YAML 템플릿으로 새 버전 생성
- `deploy_prompt <prompt_id> [version]` — 버전을 production으로 승격 (생략 시 최신 버전)
- `rollback_prompt <prompt_id>` — 이전 production 버전으로 롤백
- `diff_prompt <prompt_id> <from_version> <to_version>` — 두 버전 비교
- `guide_delete_prompt <prompt_id>` — 프롬프트 삭제 CLI 안내 반환

`bump_level` 값: `patch` (기본값) | `minor` | `major`

`guide_delete_prompt`도 되돌릴 수 없는 작업이므로 MCP 도구로 직접 실행하지 않습니다.

### 스냅샷

- `list_snapshots` — 스냅샷 버전 목록 조회
- `get_snapshot <version>` — 스냅샷 매니페스트 조회
- `read_snapshot <version>` — 스냅샷에 포함된 프롬프트 전체 내용 조회
- `create_snapshot [bump_level]` — 현재 production 프롬프트로 스냅샷 생성
- `export_snapshot <version> [output_path]` — 스냅샷을 ZIP 파일로 내보내기
- `diff_snapshots <from_version> <to_version>` — 두 스냅샷 비교

`output_path`를 생략하면 `export_snapshots/snapshot-<version>.zip`에 저장됩니다.

## 프롬프트 템플릿

`add_prompt`에 사용하는 YAML 필드:

```yaml
id: "intent_classifier"
description: "Classify the user's intent"
author: "alice"

llm:
  provider: "openai"
  model: "gpt-4.1"
  params:
    temperature: 0.2
    max_tokens: 300

prompt: |
  Classify the user's intent.

input_variables:
  - user_input
  - history
```

필수 필드: `id`, `llm`, `prompt`

규칙:

- `id`는 안정적인 prompt 식별자입니다
- `id`에는 공백과 `/`를 넣을 수 없습니다
- 첫 버전은 항상 `0.1.0`입니다
- 동일한 내용이면 no-op 처리됩니다

## 동작 규칙

- `init`의 기본 프로젝트 이름은 `my-project`
- `add_prompt`의 기본 bump는 `patch`
- `deploy_prompt`는 버전을 생략하면 최신 버전을 배포
- 현재 production과 같은 버전을 다시 배포하면 no-op
- `get_prompt`는 production이 있으면 production, 없으면 latest를 반환
- 첫 snapshot version은 항상 `0.1.0`

## 소스 구조

```text
pvm/mcp/
├── server.py        # FastMCP 앱 진입점 (pvm-mcp CLI)
├── __init__.py
└── tools/
    ├── project.py   # 프로젝트 도구
    ├── prompts.py   # 프롬프트 도구
    └── snapshots.py # 스냅샷 도구
```

## 의존성

- [`fastmcp`](https://github.com/jlowin/fastmcp) >= 3.2.0
- `pvm` (현재 패키지)

`pyproject.toml`에 `pvm-mcp = "pvm.mcp.server:main"`으로 등록됩니다.
