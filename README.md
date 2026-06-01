# Muscles JSON-RPC

JSON-RPC protocol projection for Muscles actions.

This package makes Muscles action-first applications callable over JSON-RPC
while preserving the same schemas, rules, dispatcher, and context used by other
projections.

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

## Core Stream Projection

English: stream-capable methods are discovered from `inspect_application(app)`.
When core returns `StreamResult`, JSON-RPC responds with a stable result
envelope: `{"stream": {"ok": bool, "events": [...]}}`. Each item is projected
from a core `StreamEvent`; JSON-RPC does not own a separate stream model.

Русский: stream-capable methods обнаруживаются через `inspect_application(app)`.
Когда core возвращает `StreamResult`, JSON-RPC отдаёт стабильный result
envelope: `{"stream": {"ok": bool, "events": [...]}}`. Каждый item проецируется
из core `StreamEvent`; JSON-RPC не владеет отдельной stream model.

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
