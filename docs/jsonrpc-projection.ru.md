# JSON-RPC Projection

`muscles-jsonrpc` открывает Muscles actions как JSON-RPC 2.0 methods. Он не
определяет отдельный action registry, validation model, permissions model или
use-case layer.

## Discovery

Methods читаются из Muscles inspect contract:

```python
adapter = JsonRpcAdapter.from_application(app)
methods = adapter.list_methods()
```

Показываются только actions с пустым `transports` или с transport `jsonrpc`.

## Calls

```python
response = adapter.handle(
    {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "bookings.create",
        "params": {"title": "Call"},
    }
)
```

Adapter вызывает `ActionDispatcher(app).execute(...)` с
`transport="jsonrpc"`. Core отвечает за validation, rules/security и handler
execution.

## Notifications и batches

Requests без `id` считаются notifications. Они dispatch-ятся, но не возвращают
response.

Batch requests dispatch-ят каждый item через тот же core path. Notification
items не попадают в batch response.

## Error mapping

- invalid request -> `-32600`;
- `ActionNotFound` -> `-32601`;
- invalid params / `ActionValidationError` -> `-32602`;
- `ActionPermissionDenied` -> `-32001`;
- `ActionExecutionError` -> `-32603`.
