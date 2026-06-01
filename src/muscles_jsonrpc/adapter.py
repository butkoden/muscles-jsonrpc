from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class JsonRpcError(Exception):
    code: int
    message: str
    data: dict[str, Any] | None = None


class JsonRpcAdapter:
    def __init__(self, action_handler: Callable[[str, dict[str, Any]], Any]) -> None:
        self._action_handler = action_handler

    def handle(self, request: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(request, dict):
            return self._error(None, -32600, "Invalid Request")
        if request.get("jsonrpc") != "2.0":
            return self._error(request.get("id"), -32600, "Invalid Request")
        if "method" not in request or not isinstance(request.get("method"), str):
            return self._error(request.get("id"), -32600, "Invalid Request")

        req_id = request.get("id")
        method = request["method"]
        params = request.get("params", {})
        if params is None:
            params = {}
        if not isinstance(params, dict):
            return self._error(req_id, -32602, "Invalid params")

        try:
            result = self._action_handler(method, params)
            return {"jsonrpc": "2.0", "id": req_id, "result": result}
        except KeyError:
            return self._error(req_id, -32601, "Method not found")
        except ValueError as exc:
            return self._error(req_id, -32602, "Invalid params", {"reason": str(exc)})
        except JsonRpcError as exc:
            return self._error(req_id, exc.code, exc.message, exc.data)
        except Exception:
            return self._error(req_id, -32603, "Internal error")

    @staticmethod
    def _error(req_id: Any, code: int, message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}
        if data is not None:
            payload["error"]["data"] = data
        return payload
