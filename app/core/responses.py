from typing import Any, Generic, TypeVar
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

T = TypeVar("T")


class ResponseEnvelope(BaseModel, Generic[T]):
    data: T | dict[str, Any] = {}
    meta: dict[str, Any] = {}


def create_response(
    data: Any = None,
    meta: dict[str, Any] | None = None,
    status_code: int = 200,
    message: str | None = None,
) -> JSONResponse:
    """Helper to return standardized FastAPI JSONResponse."""
    meta_dict = meta.copy() if meta is not None else {}
    if message is not None:
        meta_dict["message"] = message
    raw_content: dict[str, Any] = {
        "data": data if data is not None else {},
        "meta": meta_dict,
    }
    return JSONResponse(status_code=status_code, content=jsonable_encoder(raw_content))


success_response = create_response
