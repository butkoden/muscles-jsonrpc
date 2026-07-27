# JSON-RPC RC checklist

The projection is released only when its contract tests pass for single calls,
notifications, batches, invalid requests, permissions, core stream projection,
stream errors, non-stream list results and non-serializable results:

```bash
PYTHONPATH=../muscles/src:src python -m pytest -q
python -m build --wheel --sdist
```

Discovery comes from `inspect_application`; execution comes from
`ActionDispatcher`. No protocol-local action registry is allowed.
