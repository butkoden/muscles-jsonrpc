# JSON-RPC Projection

`muscles-jsonrpc` exposes Muscles actions as JSON-RPC 2.0 methods. It does not
define a separate action registry, validation model, permissions model, or use
case layer.

## Discovery

Methods are discovered from the Muscles inspect contract:

```python
adapter = JsonRpcAdapter.from_application(app)
methods = adapter.list_methods()
```

Only actions with an empty `transports` list or a `jsonrpc` transport are
exposed.

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

The adapter dispatches through `ActionDispatcher(app).execute(...)` with
`transport="jsonrpc"`. Core owns validation, rules/security, and handler
execution.

## Notifications And Batches

Requests without `id` are notifications. They are dispatched but do not return a
response.

Batch requests dispatch each item through the same core path. Notification items
are omitted from the batch response.

## Error Mapping

- invalid request -> `-32600`;
- `ActionNotFound` -> `-32601`;
- invalid params / `ActionValidationError` -> `-32602`;
- `ActionPermissionDenied` -> `-32001`;
- `ActionExecutionError` -> `-32603`.
