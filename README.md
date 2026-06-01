# Muscles JSON-RPC

JSON-RPC protocol adapter for Muscles actions.

This package should make Muscles action-first applications callable over JSON-RPC
while preserving the same schemas, rules, and context used by other runtimes.

## Concept Guardrails

- JSON-RPC is a protocol adapter, not a new framework layer.
- Methods must map to Muscles actions/routes/commands from the application
  contract.
- Validation and error normalization must reuse Muscles schemas and exceptions.
- Auth/rules must be shared with the core application model.
- The same use case must be callable from CLI, HTTP, MCP, and JSON-RPC without
  duplicating implementation.

## Initial Goal

Implement a minimal JSON-RPC 2.0 endpoint around Muscles actions with typed
request/response contracts and deterministic error mapping.

## Current Stage (Issue #1)

Implemented minimal JSON-RPC 2.0 adapter:

- request validation (`jsonrpc`, `method`, `params`);
- deterministic error mapping:
  - `-32600` invalid request;
  - `-32601` method not found;
  - `-32602` invalid params;
  - `-32603` internal error.

### Run tests

```bash
python -m pytest -q
```
