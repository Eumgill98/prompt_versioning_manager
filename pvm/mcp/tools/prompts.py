from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

from fastmcp.exceptions import ToolError
from pydantic import Field

from pvm import PVMProject
from pvm.core.errors import PVMError
from pvm.mcp.server import mcp
from pvm.storage.yaml_io import load_yaml


@mcp.tool()
def list_prompts() -> list[str]:
    """List all prompt ids in the current project."""
    try:
        return PVMProject.cwd().list_prompt_ids()
    except PVMError as e:
        raise ToolError(str(e))


@mcp.tool()
def list_prompt_versions(
    prompt_id: Annotated[str, Field(description="버전 목록을 조회할 prompt ID")],
) -> list[str]:
    """List all versions for a single prompt id."""
    try:
        return PVMProject.cwd().list_prompt_versions(prompt_id)
    except PVMError as e:
        raise ToolError(str(e))


@mcp.tool()
def get_prompt(
    prompt_id: Annotated[str, Field(description="조회할 prompt ID")],
    version: Annotated[
        str | None,
        Field(description="조회할 버전 (생략 시 production → latest 순으로 fallback)"),
    ] = None,
) -> dict:
    """Read a prompt by explicit version, production version, or latest version.

    If version is omitted, falls back to the current production version.
    If no production version exists, returns the latest version.
    """
    try:
        return PVMProject.cwd().get_prompt(prompt_id, version=version)
    except PVMError as e:
        raise ToolError(str(e))


@mcp.tool()
def get_prompt_info(
    prompt_id: Annotated[str, Field(description="메타 정보를 조회할 prompt ID")],
) -> dict:
    """Read stable prompt metadata and version summary."""
    try:
        return PVMProject.cwd().get_prompt_info(prompt_id)
    except PVMError as e:
        raise ToolError(str(e))


@mcp.tool()
def add_prompt(
    template_path: Annotated[
        str,
        Field(description="프롬프트 템플릿 YAML 파일 경로 (id, llm, prompt 필드 필수)"),
    ],
    bump_level: Annotated[
        Literal["patch", "minor", "major"],
        Field(description="버전 증가 단위"),
    ] = "patch",
) -> dict:
    """Create a new prompt version from a YAML template file.

    Validates the template before calling the project facade:
    - template must be a valid YAML file with 'id', 'llm', and 'prompt' fields
    - 'llm' must be a non-empty dict
    """
    try:
        user_data = load_yaml(Path(template_path))
    except Exception as e:
        raise ValueError(f"템플릿 파일을 읽을 수 없습니다: {e}")

    for field in ("id", "llm", "prompt"):
        if not user_data.get(field):
            raise ValueError(f"템플릿에 필수 필드가 없습니다: '{field}'")

    if not isinstance(user_data["llm"], dict) or not user_data["llm"]:
        raise ValueError("'llm' 필드는 비어있지 않은 dict이어야 합니다.")

    try:
        return PVMProject.cwd().add_prompt(template_path, bump_level=bump_level)
    except PVMError as e:
        raise ToolError(str(e))


@mcp.tool()
def deploy_prompt(
    prompt_id: Annotated[str, Field(description="production으로 승격할 prompt ID")],
    version: Annotated[
        str | None,
        Field(description="배포할 버전 (생략 시 최신 버전)"),
    ] = None,
) -> dict:
    """Promote a prompt version to production, defaulting to the latest version."""
    try:
        return PVMProject.cwd().deploy(prompt_id, version)
    except PVMError as e:
        raise ToolError(str(e))


@mcp.tool()
def rollback_prompt(
    prompt_id: Annotated[str, Field(description="이전 production 버전으로 롤백할 prompt ID")],
) -> dict:
    """Rollback a prompt to the previous production version."""
    try:
        return PVMProject.cwd().rollback(prompt_id)
    except PVMError as e:
        raise ToolError(str(e))


@mcp.tool()
def diff_prompt(
    prompt_id: Annotated[str, Field(description="비교할 prompt ID")],
    from_version: Annotated[str, Field(description="비교 기준 버전 (이전)")],
    to_version: Annotated[str, Field(description="비교 대상 버전 (이후)")],
) -> dict:
    """Compare two versions of the same prompt."""
    try:
        return PVMProject.cwd().diff_prompt(prompt_id, from_version, to_version)
    except PVMError as e:
        raise ToolError(str(e))


@mcp.tool()
def guide_delete_prompt(
    prompt_id: Annotated[str, Field(description="삭제할 prompt ID")],
) -> str:
    """Return instructions for deleting a prompt via CLI.

    The delete operation removes all versions of a prompt and cannot be undone,
    so it is intentionally not exposed as a direct MCP tool.
    """
    return (
        f"프롬프트를 삭제하려면 터미널에서 실행하세요:\n\n"
        f"  pvm delete {prompt_id}\n\n"
        "이 작업은 되돌릴 수 없습니다."
    )
