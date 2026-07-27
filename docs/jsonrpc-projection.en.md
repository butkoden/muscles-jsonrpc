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

## Streaming

Actions marked with `stream_output=True` are projected through the core stream
contract. The JSON-RPC response keeps the request id and returns a stable
`result.stream` envelope:

```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "result": {
    "stream": {
      "ok": true,
      "events": [
        {"event": "progress", "data": {"step": 1}, "id": "evt-1", "metadata": {}},
        {"event": "result", "data": {"ok": true}, "id": null, "metadata": {}}
      ]
    }
  }
}
```

Core `progress`, `log`, `result`, and `error` events keep their event type and
payload. A stream error is represented as an `error` event and sets
`stream.ok` to `false`. Lists and tuples returned by a non-stream action remain
ordinary JSON-RPC results and are never treated as streams.

## Error Mapping

- invalid request -> `-32600`;
- `ActionNotFound` -> `-32601`;
- invalid params / `ActionValidationError` -> `-32602`;
- `ActionPermissionDenied` -> `-32001`;
- `ActionExecutionError` -> `-32603`.
