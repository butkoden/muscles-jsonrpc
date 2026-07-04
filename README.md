# Muscles JSON-RPC

JSON-RPC protocol projection for Muscles actions.

This package makes Muscles action-first applications callable over JSON-RPC
while preserving the same schemas, rules, dispatcher, and context used by other
projections.

## Related Repositories

- [`muscles`](https://github.com/butkoden/muscles) - core action contracts, dispatcher and inspect contract.
- [`muscles-cli`](https://github.com/butkoden/muscles-cli) - CLI action inspection and execution over the same contracts.
- [`muscles-mcp`](https://github.com/butkoden/muscles-mcp) - MCP projection over the same action model.
- [`muscles-sse`](https://github.com/butkoden/muscles-sse) - streaming projection for action output.
- [`muscles-benchmarks`](https://github.com/butkoden/muscles-benchmarks) - protocol projection regression checks.

## Concept Guardrails

- JSON-RPC is a protocol projection, not a new framework layer.
- Methods must be discovered from `inspect_application(app)`.
- Validation and error normalization must reuse Muscles core schema/rules/errors.
- Auth/rules must run through `ActionDispatcher`.
- The same use case must be callable from CLI, HTTP, MCP, and JSON-RPC without
  duplicating implementation.
- JSON-RPC state is scoped to the application instance; no mutable module-level
  method registry is the source of truth.

## Initial Goal

Implement a JSON-RPC 2.0 projection around Muscles actions with typed
request/response contracts, deterministic error mapping, notifications, and
batch dispatch.

## Current Stage (Issue #1)

Implemented JSON-RPC 2.0 projection:

- request validation (`jsonrpc`, `method`, `params`);
- method discovery from `inspect_application(app)`;
- dispatch through `ActionDispatcher(..., transport="jsonrpc")`;
- notification calls;
- batch calls;
- deterministic error mapping:
  - `-32600` invalid request;
  - `-32601` method not found;
  - `-32602` invalid params;
  - `-32001` permission denied;
  - `-32603` internal error.

### Run tests

```bash
python -m pytest -q
```

When testing against local core changes:

```bash
PYTHONPATH=../muscles/src:src python -m pytest -q
```

User docs:

- English: [docs/jsonrpc-projection.en.md](docs/jsonrpc-projection.en.md)
- Русский: [docs/jsonrpc-projection.ru.md](docs/jsonrpc-projection.ru.md)
