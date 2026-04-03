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
    import pvm.mcp.tools.snapshots  # noqa: F401

    mcp.run(transport="stdio")
