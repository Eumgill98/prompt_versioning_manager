# pvm MCP Server

`pvm-mcp` is an MCP (Model Context Protocol) server that exposes pvm's prompt version management as tools.

It provides:

- project initialization and configuration tools
- prompt add / get / deploy / rollback / diff tools
- snapshot create / read / export / diff tools
- a `stdio`-based MCP transport via FastMCP

## Setup

If this is your first time, follow these steps in order.

```bash
# 1. Clone the repository
git clone https://github.com/OWNER/REPO.git
cd REPO

# 2. Install uv (skip if already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Verify the server runs
uv run pvm-mcp --help
```

To use with Claude Code, register `.mcp.json` in the project root. See the [Connect to Claude Code](#connect-to-claude-code) section below.

---

## Install

### Recommended: `uv`

Run directly from the project root without a separate install step:

```bash
uv run pvm-mcp
```

Point to a specific pvm project:

```bash
uv run pvm-mcp --root /path/to/your/project
```

### `pipx`

Install with the `server` extra:

```bash
pipx install ".[server]"
pvm-mcp
pvm-mcp --root /path/to/your/project
```

### Poetry (local development)

```bash
poetry install -E server
poetry run pvm-mcp
```

## Connect to Claude Code

### `.mcp.json` (project-local)

Place `.mcp.json` in the project root.

**WSL on Windows:**

```json
{
  "mcpServers": {
    "pvm": {
      "type": "stdio",
      "command": "wsl",
      "args": ["bash", "-lc", "./run_pvm_mcp.sh"],
      "env": {}
    }
  }
}
```

**Linux / macOS (uv):**

```json
{
  "mcpServers": {
    "pvm": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "pvm-mcp", "--root", "/path/to/your/project"]
    }
  }
}
```

**Linux / macOS (pipx):**

```json
{
  "mcpServers": {
    "pvm": {
      "type": "stdio",
      "command": "pvm-mcp",
      "args": ["--root", "/path/to/your/project"]
    }
  }
}
```

`pipx install ".[server]"` installs `pvm-mcp` as a global command, so it can be used directly without `uv run`.

### `run_pvm_mcp.sh`

The helper script used by the WSL config above. It locates `uv` automatically and falls back to a globally installed `pvm-mcp` if `uv` is not found.

## Quick Start

Initialize a project and add a prompt:

```
1. mcp__pvm__init
2. mcp__pvm__load_template      ← inspect the template, then write your YAML
3. mcp__pvm__add_prompt         (template_path: "prompt.yaml")
4. mcp__pvm__deploy_prompt      (prompt_id: "intent_classifier")
5. mcp__pvm__create_snapshot
```

Query and compare prompts:

```
1. mcp__pvm__list_prompts
2. mcp__pvm__list_prompt_versions   (prompt_id: "intent_classifier")
3. mcp__pvm__get_prompt             (prompt_id: "intent_classifier")
4. mcp__pvm__diff_prompt            (prompt_id: "intent_classifier", from_version: "0.1.0", to_version: "0.2.0")
```

Export a snapshot:

```
1. mcp__pvm__list_snapshots
2. mcp__pvm__export_snapshot    (version: "0.1.0")
   → saved to export_snapshots/snapshot-0.1.0.zip
```

## Tool Reference

Tools are called as `mcp__pvm__<tool_name>`.

### Project

- `init [name]` — initialize a pvm project in the current working directory
- `check_integrity` — verify `.pvm/` directory structure
- `load_config` — load `.pvm/config.yaml`
- `load_template` — load the default prompt template
- `guide_destroy` — return CLI instructions for permanently deleting the project
- `guide_reset` — return CLI instructions for resetting the project

`guide_destroy` and `guide_reset` are intentionally not executed directly because they are irreversible. They return the equivalent `pvm` CLI command to run in the terminal.

### Prompts

- `list_prompts` — list all prompt IDs
- `list_prompt_versions <prompt_id>` — list all versions for a prompt
- `get_prompt <prompt_id> [version]` — read a prompt (falls back to production → latest)
- `get_prompt_info <prompt_id>` — read stable metadata and version summary
- `add_prompt <template_path> [bump_level]` — create a new version from a YAML template
- `deploy_prompt <prompt_id> [version]` — promote a version to production (defaults to latest)
- `rollback_prompt <prompt_id>` — roll back to the previous production version
- `diff_prompt <prompt_id> <from_version> <to_version>` — compare two versions
- `guide_delete_prompt <prompt_id>` — return CLI instructions for deleting a prompt

`bump_level` values: `patch` (default) | `minor` | `major`

`guide_delete_prompt` is intentionally not executed directly because it is irreversible.

### Snapshots

- `list_snapshots` — list snapshot versions
- `get_snapshot <version>` — load a snapshot manifest
- `read_snapshot <version>` — expand a snapshot into full prompt contents
- `create_snapshot [bump_level]` — create a snapshot from the current production set
- `export_snapshot <version> [output_path]` — export a snapshot as a ZIP file
- `diff_snapshots <from_version> <to_version>` — compare two snapshots

If `output_path` is omitted, the ZIP is saved to `export_snapshots/snapshot-<version>.zip`.

## Prompt Template

The required YAML fields for `add_prompt`:

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

Required fields: `id`, `llm`, `prompt`

Rules:

- `id` is the stable prompt identifier
- `id` cannot contain spaces or `/`
- the first version is always `0.1.0`
- identical content is a no-op

## Behavior Notes

- `init` defaults the project name to `my-project`
- `add_prompt` defaults to a `patch` bump
- `deploy_prompt` deploys the latest version if `version` is omitted
- re-deploying the current production version is a no-op
- `get_prompt` returns the production version if it exists, otherwise the latest
- the first snapshot version is always `0.1.0`

## Source Layout

```text
pvm/mcp/
├── server.py        # FastMCP app entry point (pvm-mcp CLI)
├── __init__.py
└── tools/
    ├── project.py   # project tools
    ├── prompts.py   # prompt tools
    └── snapshots.py # snapshot tools
```

## Dependencies

- [`fastmcp`](https://github.com/jlowin/fastmcp) >= 3.2.0
- `pvm` (this package)

Registered in `pyproject.toml` as `pvm-mcp = "pvm.mcp.server:main"`.
