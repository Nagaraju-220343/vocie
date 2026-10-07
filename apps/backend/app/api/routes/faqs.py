import math
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Response

from app.repositories.faq_repository import FaqRepository
from app.schemas.common import ErrorResponse, PaginatedResponse, Pagination
from app.schemas.faq import FaqCreate, FaqMatchResponse, FaqResponse, FaqUpdate
from app.services.faq_service import FaqService

router = APIRouter(prefix="/faqs", tags=["FAQs"])
service = FaqService()

@router.get("/search", response_model=FaqMatchResponse)
def search_faq(q: str, language: str = "EN") -> FaqMatchResponse:
    result = service.find_faq(q, language)
    resp_dict = result.model_dump()
    if resp_dict.get("faq"):
        resp_dict["faq"] = FaqResponse(**resp_dict["faq"])
    return FaqMatchResponse(**resp_dict)

@router.get("", response_model=PaginatedResponse[FaqResponse])
def get_faqs(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    active: Optional[bool] = None,
    category: Optional[str] = None,
) -> PaginatedResponse[FaqResponse]:
    filters: dict = {}
    if active is not None: filters["active"] = active
    if category: filters["category"] = category

    repo = FaqRepository()
    skip = (page - 1) * pageSize
    items = repo.list(limit=pageSize, skip=skip, filters=filters)
    total = repo.count(filters=filters)
    total_pages = math.ceil(total / pageSize) if pageSize else 0

    return PaginatedResponse(
        data=[FaqResponse(**item.model_dump()) for item in items],
        pagination=Pagination(page=page, pageSize=pageSize, total=total, totalPages=total_pages)
    )

@router.get("/{faq_id}", response_model=FaqResponse, responses={404: {"model": ErrorResponse}})
def get_faq(faq_id: str) -> FaqResponse:
    repo = FaqRepository()
    faq = repo.get_by_id(faq_id)
    if not faq:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "FAQ not found"}})
    return FaqResponse(**faq.model_dump())

@router.post("", response_model=FaqResponse, status_code=201)
def create_faq(faq: FaqCreate) -> FaqResponse:
    created = service.create_faq(faq.model_dump())
    return FaqResponse(**created.model_dump())

@router.patch("/{faq_id}", response_model=FaqResponse, responses={404: {"model": ErrorResponse}})
def update_faq(faq_id: str, updates: FaqUpdate) -> FaqResponse:
    updated = service.update_faq(faq_id, updates.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "FAQ not found"}})
    return FaqResponse(**updated.model_dump())

@router.delete("/{faq_id}", status_code=204, responses={404: {"model": ErrorResponse}})
def delete_faq(faq_id: str) -> Response:
    if not service.delete_faq(faq_id):
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "FAQ not found"}})
    return Response(status_code=204)
