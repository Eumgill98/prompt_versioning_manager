from typing import Annotated

from fastmcp.exceptions import ToolError
from pydantic import Field

from pvm import PVMProject
from pvm.core.errors import PVMError
from pvm.mcp.server import mcp


@mcp.tool()
def check_integrity() -> dict:
    """Check which required directories and files are missing from `.pvm/`."""
    try:
        return PVMProject.cwd().check_integrity()
    except PVMError as e:
        raise ToolError(str(e))


@mcp.tool()
def init(
    name: Annotated[str, Field(description="프로젝트 이름")] = "my-project",
) -> dict:
    """Initialize a new pvm project in the current working directory."""
    try:
        return PVMProject.cwd().init(name)
    except PVMError as e:
        raise ToolError(str(e))


@mcp.tool()
def load_config() -> dict:
    """Load `.pvm/config.yaml` for the current project."""
    try:
        return PVMProject.cwd().load_config()
    except PVMError as e:
        raise ToolError(str(e))


@mcp.tool()
def load_template() -> dict:
    """Load the default prompt template stored in project settings."""
    try:
        return PVMProject.cwd().load_template()
    except PVMError as e:
        raise ToolError(str(e))


@mcp.tool()
def guide_destroy() -> str:
    """Return instructions for permanently deleting the project via CLI.

    The destroy operation removes the entire `.pvm/` directory and cannot be
    undone, so it is intentionally not exposed as a direct MCP tool.
    """
    return (
        "프로젝트를 영구 삭제하려면 터미널에서 실행하세요:\n\n"
        "  pvm destroy\n\n"
        "이 작업은 되돌릴 수 없습니다."
    )


@mcp.tool()
def guide_reset() -> str:
    """Return instructions for resetting the project via CLI.

    The reset operation destroys and re-initializes the project, wiping all
    prompts and snapshots, so it is intentionally not exposed as a direct MCP tool.
    """
    return (
        "프로젝트를 초기화하려면 터미널에서 실행하세요:\n\n"
        "  pvm reset\n\n"
        "모든 프롬프트와 스냅샷이 삭제됩니다."
    )
