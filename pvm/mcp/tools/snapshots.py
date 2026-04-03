from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

from fastmcp.exceptions import ToolError
from pydantic import Field

from pvm import PVMProject
from pvm.core.errors import PVMError
from pvm.mcp.server import mcp


@mcp.tool()
def list_snapshots() -> list[str]:
    """List snapshot versions in the current project."""
    try:
        return PVMProject.cwd().list_snapshots()
    except PVMError as e:
        raise ToolError(str(e))


@mcp.tool()
def get_snapshot(
    version: Annotated[str, Field(description="조회할 스냅샷 버전")],
) -> dict:
    """Load a snapshot manifest by version."""
    try:
        return PVMProject.cwd().get_snapshot(version)
    except PVMError as e:
        raise ToolError(str(e))


@mcp.tool()
def read_snapshot(
    version: Annotated[str, Field(description="전체 내용을 조회할 스냅샷 버전")],
) -> dict:
    """Expand a snapshot into the prompt contents it references."""
    try:
        return PVMProject.cwd().read_snapshot(version)
    except PVMError as e:
        raise ToolError(str(e))


@mcp.tool()
def create_snapshot(
    bump_level: Annotated[
        Literal["patch", "minor", "major"],
        Field(description="버전 증가 단위"),
    ] = "patch",
) -> dict:
    """Create a snapshot from the current production prompt set."""
    try:
        return PVMProject.cwd().create_snapshot(bump_level=bump_level)
    except PVMError as e:
        raise ToolError(str(e))


@mcp.tool()
def export_snapshot(
    version: Annotated[str, Field(description="내보낼 스냅샷 버전")],
    output_path: Annotated[
        str | None,
        Field(description="저장할 ZIP 파일 경로 (생략 시 <project_root>/export_snapshots/snapshot-<version>.zip)"),
    ] = None,
) -> dict:
    """Export a snapshot version as a zip file.

    If output_path is omitted, the zip is saved to
    `<project_root>/export_snapshots/snapshot-<version>.zip`.
    """
    try:
        project = PVMProject.cwd()
        if output_path is None:
            resolved = project.root / "export_snapshots" / f"snapshot-{version}.zip"
        else:
            resolved = Path(output_path).resolve()

        resolved.parent.mkdir(parents=True, exist_ok=True)
        return project.export_snapshot(version, resolved)
    except PVMError as e:
        raise ToolError(str(e))


@mcp.tool()
def diff_snapshots(
    from_version: Annotated[str, Field(description="비교 기준 스냅샷 버전 (이전)")],
    to_version: Annotated[str, Field(description="비교 대상 스냅샷 버전 (이후)")],
) -> dict:
    """Compare two snapshots by prompt membership and version mapping."""
    try:
        return PVMProject.cwd().diff_snapshot(from_version, to_version)
    except PVMError as e:
        raise ToolError(str(e))
