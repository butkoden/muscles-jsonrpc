from __future__ import annotations

from dataclasses import dataclass
from typing import Any


JSONRPC_VERSION = "2.0"


@dataclass(frozen=True)
class JsonRpcError(Exception):
    code: int
    message: str
    data: dict[str, Any] | None = None


class JsonRpcAdapter:
    """Projects Muscles actions into JSON-RPC 2.0 methods."""

    def __init__(self, app) -> None:
        self._app = app

    @classmethod
    def from_application(cls, app):
        return cls(app)

    @property
    def _contract(self) -> dict[str, Any]:
        from muscles.core import inspect_application

        return inspect_application(self._app)

    def list_methods(self) -> list[dict[str, Any]]:
        methods: list[dict[str, Any]] = []
        for action in self._contract.get("actions", []):
            name = action.get("name")
            if not name:
                continue
            transports = action.get("transports") or []
            if transports and "jsonrpc" not in transports:
                continue
            methods.append(
                {
                    "name": name,
                    "description": action.get("description", ""),
                    "params_schema": action.get("input_schema", {"type": "object", "properties": {}}),
                }
            )
        return methods

    def handle(self, request: dict[str, Any] | list[Any]) -> dict[str, Any] | list[dict[str, Any]] | None:
        if isinstance(request, list):
            if not request:
                return self._error(None, -32600, "Invalid Request")
            responses = [response for item in request if (response := self._handle_single(item)) is not None]
            return responses or None
        return self._handle_single(request)

    def _handle_single(self, request: Any) -> dict[str, Any] | None:
        if not isinstance(request, dict):
            return self._error(None, -32600, "Invalid Request")
        req_id = request.get("id")
        is_notification = "id" not in request
        if request.get("jsonrpc") != JSONRPC_VERSION:
            return self._error(req_id, -32600, "Invalid Request")
        if "method" not in request or not isinstance(request.get("method"), str):
            return self._error(req_id, -32600, "Invalid Request")

        params = request.get("params", {})
        if params is None:
            params = {}
        if not isinstance(params, dict):
            if is_notification:
                return None
            return self._error(req_id, -32602, "Invalid params")

        try:
            from muscles.core import ActionDispatcher

            result = ActionDispatcher(self._app).execute(request["method"], params, transport="jsonrpc")
            if is_notification:
                return None
            return {"jsonrpc": JSONRPC_VERSION, "id": req_id, "result": result.value}
        except Exception as exc:
            if is_notification:
                return None
            mapped = self._map_core_error(exc)
            if mapped is not None:
                return self._error(req_id, mapped.code, mapped.message, mapped.data)
            return self._error(req_id, -32603, "Internal error")

    @staticmethod
    def _map_core_error(exc: Exception) -> JsonRpcError | None:
        try:
            from muscles.core import (
                ActionExecutionError,
                ActionNotFound,
                ActionPermissionDenied,
                ActionValidationError,
            )
        except Exception:
            return None

        if isinstance(exc, ActionNotFound):
            return JsonRpcError(-32601, "Method not found")
        if isinstance(exc, ActionValidationError):
            return JsonRpcError(-32602, "Invalid params", {"reason": exc.message, "data": exc.data})
        if isinstance(exc, ActionPermissionDenied):
            return JsonRpcError(-32001, "Permission denied", {"reason": exc.message, "data": exc.data})
        if isinstance(exc, ActionExecutionError):
            return JsonRpcError(-32603, "Internal error", {"reason": exc.message, "data": exc.data})
        if isinstance(exc, JsonRpcError):
            return exc
        return None

    @staticmethod
    def _error(req_id: Any, code: int, message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"jsonrpc": JSONRPC_VERSION, "id": req_id, "error": {"code": code, "message": message}}
        if data is not None:
            payload["error"]["data"] = data
        return payload


JsonRpcServer = JsonRpcAdapter
