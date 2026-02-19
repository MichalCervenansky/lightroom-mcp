---
description: Run Unit and Integration Tests
---

This workflow runs the test suite for the Lightroom MCP project.

1. Run Broker Unit Tests (Python)
// turbo
2. Run Broker Integration Tests (Python)

```bash
cd mcp-server
.venv\Scripts\python.exe -m pytest -v tests/
```

3. Run Lua Plugin Tests (Requires Lua installed)

> [!NOTE]
> This step requires `lua` to be in your system PATH. The `luac.exe` included in the Lightroom SDK is a compiler and cannot run these tests.

```bash
cd lightroom-plugin.lrplugin/tests
& "C:\Program Files (x86)\Lua\5.1\lua.exe" RunTests.lua
```
