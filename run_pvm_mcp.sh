#!/usr/bin/env bash

# 이 스크립트가 위치한 디렉토리를 절대 경로로 구한다.
# 심볼릭 링크나 상대 경로로 호출되더라도 올바른 경로를 얻기 위해 cd + pwd를 사용한다.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# pvm 프로젝트 루트로 이동한다. 이동 실패 시 즉시 종료한다.
cd "$SCRIPT_DIR" || exit 1

# uv 실행 파일을 탐색한다. 우선순위: PATH → ~/.local/bin → ~/.cargo/bin
if command -v uv &>/dev/null; then
  # PATH에 uv가 있는 경우
  UV=uv
elif [ -x "$HOME/.local/bin/uv" ]; then
  # pipx 또는 독립 설치 시 기본 위치
  UV="$HOME/.local/bin/uv"
elif [ -x "$HOME/.cargo/bin/uv" ]; then
  # cargo를 통해 설치된 경우
  UV="$HOME/.cargo/bin/uv"
fi

if [ -n "$UV" ]; then
  # uv가 발견된 경우: 전용 가상환경을 지정하고 pvm-mcp를 실행한다.
  # UV_PROJECT_ENVIRONMENT를 설정하면 프로젝트별 venv를 고정할 수 있다.
  export UV_PROJECT_ENVIRONMENT="$HOME/.venv/pvm-mcp"
  exec "$UV" run pvm-mcp
elif command -v pvm-mcp &>/dev/null; then
  # uv가 없고 pvm-mcp가 전역 명령으로 설치된 경우 (pipx 등)
  exec pvm-mcp
else
  # uv도 없고 pvm-mcp도 없는 경우: 설치 방법을 안내하고 종료한다.
  echo "Error: pvm-mcp not found. Install uv (https://astral.sh/uv) or run 'pipx install pvm'" >&2
  exit 1
fi
