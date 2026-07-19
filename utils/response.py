from typing import Any, Dict, Optional


def success_response(message: str, data: Optional[Any] = None) -> Dict[str, Any]:
    return {"message": message, "data": data}


def error_response(message: str) -> Dict[str, Any]:
    return {"message": message}
