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

## Streaming

Actions с `stream_output=True` проецируются через общий core stream contract.
JSON-RPC response сохраняет request id и возвращает стабильный envelope
`result.stream`:

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

Core events `progress`, `log`, `result` и `error` сохраняют тип и payload.
Ошибка внутри stream становится `error` event и устанавливает
`stream.ok=false`. Списки и tuple, возвращённые non-stream action, остаются
обычными JSON-RPC results и никогда не трактуются как stream.

## Error mapping

- invalid request -> `-32600`;
- `ActionNotFound` -> `-32601`;
- invalid params / `ActionValidationError` -> `-32602`;
- `ActionPermissionDenied` -> `-32001`;
- `ActionExecutionError` -> `-32603`.
