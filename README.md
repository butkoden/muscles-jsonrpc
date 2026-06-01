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
