from muscles_jsonrpc import JsonRpcAdapter


def test_jsonrpc_success():
    def handler(method, params):
        if method == "bookings.create":
            return {"booking_id": 1, "title": params["title"]}
        raise KeyError(method)

    adapter = JsonRpcAdapter(handler)
    response = adapter.handle(
        {"jsonrpc": "2.0", "id": 7, "method": "bookings.create", "params": {"title": "Call"}}
    )
    assert response == {"jsonrpc": "2.0", "id": 7, "result": {"booking_id": 1, "title": "Call"}}


def test_jsonrpc_method_not_found():
    adapter = JsonRpcAdapter(lambda method, params: (_ for _ in ()).throw(KeyError(method)))
    response = adapter.handle({"jsonrpc": "2.0", "id": 5, "method": "missing", "params": {}})
    assert response["error"]["code"] == -32601


def test_jsonrpc_invalid_params_shape():
    adapter = JsonRpcAdapter(lambda method, params: {})
    response = adapter.handle({"jsonrpc": "2.0", "id": 1, "method": "x", "params": []})
    assert response["error"]["code"] == -32602


def test_jsonrpc_invalid_request():
    adapter = JsonRpcAdapter(lambda method, params: {})
    response = adapter.handle({"id": 1, "method": "x"})
    assert response["error"]["code"] == -32600
