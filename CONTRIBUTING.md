# Contributing to Lightroom MCP

Thanks for your interest in contributing. This document gives a short overview of how to work on the project.

## Development setup

1. **Lightroom plugin**
   - Install the plugin per [README.md](./README.md#1-install-the-lightroom-plugin).
   - Use a code editor with Lua support. The plugin uses Lightroom’s Lua 5.1–compatible runtime and SDK.

2. **MCP server**
   - From `mcp-server/`: create a venv, activate it, run `pip install -r requirements.txt`.
   - Ensure Lightroom is running with the plugin enabled (port **54321**) before testing the MCP server.

## Project structure

- **lightroom-plugin.lrplugin/** — Lua plugin (Lightroom SDK).
- **mcp-server/** — Python MCP server (FastMCP + `lrc_client`).
- **agents.md** — MCP tools and agent workflows; update when changing tool behavior.

See [.cursorrules](./.cursorrules) for conventions and references.

## Making changes

1. **Branch** from `main` (or the default branch) for new work.
2. **Implement** your changes. Keep the plugin and MCP server in sync (e.g. new commands in both plugin and `lrc_client`/tools).
3. **Update docs** as needed:
   - [README.md](./README.md) — setup, usage, troubleshooting.
   - [agents.md](./agents.md) — tool descriptions, parameters, return values, workflows.
   - [CHANGELOG.md](./CHANGELOG.md) — add entries under `[Unreleased]` per [Keep a Changelog](https://keepachangelog.com/).

## Testing

- **Plugin:** Restart Lightroom after plugin changes; use **Plug-in Manager** to confirm it loads.
- **MCP server:** Run it locally and call tools via Cursor or another MCP client. Use `test_connection.py` if available to verify connectivity to the plugin.

## Submitting changes

- Prefer small, focused commits and clear commit messages.
- Open a pull request against the default branch. Describe what changed and why, and link any related issues.

## Code style

- **Lua:** Follow existing style in the plugin (indentation, naming, use of SDK APIs).
- **Python:** Use `mcp-server`’s existing style; consider formatting with `black` or `ruff` if the project adopts them.

## Questions

If something is unclear, open an issue so we can improve the docs or the contribution process.
