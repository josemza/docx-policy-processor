from typing import Any


def success_response(
    *,
    data: Any = None,
    message: str = "Operacion exitosa.",
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "success": True,
        "message": message,
        "data": data,
        "error": None,
        "meta": meta or {},
    }



def error_response(
    *,
    code: str,
    message: str,
    details: Any = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "data": None,
        "error": {"code": code, "details": details},
        "meta": meta or {},
    }
