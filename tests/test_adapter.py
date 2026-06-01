from muscles.core import (
    ActionPermissionDenied,
    ApplicationMeta,
    BaseStrategy,
    Context,
    register_action,
)

from muscles_jsonrpc import JsonRpcAdapter


class _EchoStrategy(BaseStrategy):
    def execute(self, *args, **kwargs):
        return kwargs


BOOKING_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "guest_count": {"type": "integer"},
    },
    "required": ["title"],
}


def _build_app(handler=None, transports=None):
    class _App(metaclass=ApplicationMeta):
        context = Context(_EchoStrategy)

    app = _App()
    calls = []

    def default_handler(payload, context):
        calls.append((context.action.name, payload, context.transport))
        return {
            "id": len(calls),
            "title": payload["title"],
            "guest_count": payload.get("guest_count", 1),
        }

    register_action(
        app,
        name="bookings.create",
        description="Create booking",
        input_schema=BOOKING_INPUT_SCHEMA,
        output_schema={"type": "object", "properties": {"id": {"type": "integer"}}},
        transports=transports if transports is not None else ["http", "jsonrpc"],
        handler=handler or default_handler,
    )
    return app, calls


def test_jsonrpc_success_uses_core_dispatcher_once():
    app, calls = _build_app()
    adapter = JsonRpcAdapter.from_application(app)

    response = adapter.handle(
        {"jsonrpc": "2.0", "id": 7, "method": "bookings.create", "params": {"title": "Call"}}
    )

    assert calls == [("bookings.create", {"title": "Call"}, "jsonrpc")]
    assert response == {
        "jsonrpc": "2.0",
        "id": 7,
        "result": {"id": 1, "title": "Call", "guest_count": 1},
    }


def test_jsonrpc_method_list_comes_from_inspect_contract_and_transport_filter():
    app, _ = _build_app()
    register_action(
        app,
        name="bookings.http_only",
        input_schema=BOOKING_INPUT_SCHEMA,
        transports=["http"],
        handler=lambda payload, context: {"ok": True},
    )
    adapter = JsonRpcAdapter.from_application(app)

    assert adapter.list_methods() == [
        {
            "name": "bookings.create",
            "description": "Create booking",
            "params_schema": BOOKING_INPUT_SCHEMA,
        }
    ]


def test_jsonrpc_method_not_found_maps_core_error():
    app, _ = _build_app()
    adapter = JsonRpcAdapter.from_application(app)

    response = adapter.handle({"jsonrpc": "2.0", "id": 5, "method": "missing", "params": {}})

    assert response["error"]["code"] == -32601
    assert response["error"]["message"] == "Method not found"


def test_jsonrpc_invalid_params_shape():
    app, _ = _build_app()
    adapter = JsonRpcAdapter.from_application(app)

    response = adapter.handle({"jsonrpc": "2.0", "id": 1, "method": "bookings.create", "params": []})

    assert response["error"]["code"] == -32602


def test_jsonrpc_invalid_params_from_core_validation():
    app, _ = _build_app()
    adapter = JsonRpcAdapter.from_application(app)

    response = adapter.handle({"jsonrpc": "2.0", "id": 1, "method": "bookings.create", "params": {}})

    assert response["error"]["code"] == -32602
    assert response["error"]["message"] == "Invalid params"
    assert "title" in response["error"]["data"]["reason"]


def test_jsonrpc_permission_denied_from_core_rules():
    def deny(payload, context):
        raise ActionPermissionDenied(context.action.name, "Denied by core rules")

    app, _ = _build_app(handler=deny)
    adapter = JsonRpcAdapter.from_application(app)

    response = adapter.handle({"jsonrpc": "2.0", "id": 2, "method": "bookings.create", "params": {"title": "Call"}})

    assert response["error"]["code"] == -32001
    assert response["error"]["message"] == "Permission denied"
    assert response["error"]["data"]["reason"] == "Denied by core rules"


def test_jsonrpc_denies_method_not_open_to_jsonrpc_transport():
    app, _ = _build_app(transports=["http"])
    adapter = JsonRpcAdapter.from_application(app)

    response = adapter.handle({"jsonrpc": "2.0", "id": 3, "method": "bookings.create", "params": {"title": "Call"}})

    assert response["error"]["code"] == -32001


def test_jsonrpc_execution_error_for_async_handler():
    async def create_booking(payload, context):
        return {"title": payload["title"]}

    app, _ = _build_app(handler=create_booking)
    adapter = JsonRpcAdapter.from_application(app)

    response = adapter.handle({"jsonrpc": "2.0", "id": 4, "method": "bookings.create", "params": {"title": "Call"}})

    assert response["error"]["code"] == -32603


def test_jsonrpc_notification_returns_none_but_dispatches():
    app, calls = _build_app()
    adapter = JsonRpcAdapter.from_application(app)

    response = adapter.handle({"jsonrpc": "2.0", "method": "bookings.create", "params": {"title": "Notify"}})

    assert response is None
    assert calls == [("bookings.create", {"title": "Notify"}, "jsonrpc")]


def test_jsonrpc_batch_dispatches_each_request_without_bypassing_core():
    app, calls = _build_app()
    adapter = JsonRpcAdapter.from_application(app)

    response = adapter.handle(
        [
            {"jsonrpc": "2.0", "id": 1, "method": "bookings.create", "params": {"title": "A"}},
            {"jsonrpc": "2.0", "id": 2, "method": "missing", "params": {}},
            {"jsonrpc": "2.0", "method": "bookings.create", "params": {"title": "Notification"}},
        ]
    )

    assert response == [
        {"jsonrpc": "2.0", "id": 1, "result": {"id": 1, "title": "A", "guest_count": 1}},
        {"jsonrpc": "2.0", "id": 2, "error": {"code": -32601, "message": "Method not found"}},
    ]
    assert calls == [
        ("bookings.create", {"title": "A"}, "jsonrpc"),
        ("bookings.create", {"title": "Notification"}, "jsonrpc"),
    ]


def test_jsonrpc_invalid_request():
    app, _ = _build_app()
    adapter = JsonRpcAdapter.from_application(app)

    response = adapter.handle({"id": 1, "method": "x"})

    assert response["error"]["code"] == -32600


def test_jsonrpc_state_is_scoped_to_application_instance():
    app_a, _ = _build_app()

    class _OtherApp(metaclass=ApplicationMeta):
        context = Context(_EchoStrategy)

    app_b = _OtherApp()
    register_action(
        app_b,
        name="tasks.create",
        input_schema={"type": "object", "properties": {}},
        handler=lambda payload, context: {"ok": True},
    )

    methods_a = JsonRpcAdapter.from_application(app_a).list_methods()
    methods_b = JsonRpcAdapter.from_application(app_b).list_methods()

    assert [method["name"] for method in methods_a] == ["bookings.create"]
    assert [method["name"] for method in methods_b] == ["tasks.create"]
