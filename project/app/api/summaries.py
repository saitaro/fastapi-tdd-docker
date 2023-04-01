from fastapi import APIRouter, HTTPException

from app.api import crud
from app.models.pydantic import (
    SummaryPayloadSchema,
    SummaryResponseSchema,
)
from app.models.tortoise import SummarySchema

router = APIRouter()


@router.post('/', response_model=SummaryResponseSchema, status_code=201)
async def create_summary(payload: SummaryPayloadSchema) -> SummaryResponseSchema:
    summary_id = await crud.post(payload)
    response = {
        'id': summary_id,
        'url': payload.url,
    }
    return response


@router.get('/{id}/', response_model=SummarySchema)
async def read_summary(id: int) -> SummarySchema:
    if summary := await crud.get(id):
        return summary
    else:
        raise HTTPException(404, 'Summary not found')


@router.get('/', response_model=list[SummarySchema])
async def read_all_summaries() -> list[SummarySchema]:
    return await crud.get_all()
