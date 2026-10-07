from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar('T')

class Pagination(BaseModel):
    page: int
    pageSize: int
    total: int
    totalPages: int

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    pagination: Pagination

class ErrorDetail(BaseModel):
    code: str
    message: str

class ErrorResponse(BaseModel):
    error: ErrorDetail
