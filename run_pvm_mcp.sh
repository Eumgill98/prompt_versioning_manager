#!/usr/bin/env bash
cd prompt_versioning_manager || exit 1
exec /home/mdr/.local/bin/uv run pvm-mcp
