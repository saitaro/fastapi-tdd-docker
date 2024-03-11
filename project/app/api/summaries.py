from fastapi import APIRouter, HTTPException, Path

from app.api import crud
from app.models.pydantic import (SummaryPayloadSchema, SummaryResponseSchema,
                                 SummaryUpdatePayloadSchema)
from app.models.tortoise import SummarySchema

router = APIRouter()


@router.get('/', response_model=list[SummarySchema])
async def read_all_summaries():
    return await crud.read_all()


@router.get('/{summary_id}', response_model=SummarySchema)
async def read_summary(summary_id: int = Path(gt=0)):
    if summary := await crud.read(summary_id):
        return summary
    else:
        raise HTTPException(404, 'Summary not found')


@router.post('/', response_model=SummaryResponseSchema, status_code=201)
async def create_summary(payload: SummaryPayloadSchema):
    summary_id = await crud.create(payload)
    response = {
        'id': summary_id,
        'url': payload.url,
    }
    return response


@router.delete('/{summary_id}', response_model=SummaryResponseSchema)
async def delete_summary(summary_id: int):
    if summary := await crud.read(summary_id):
        await crud.delete(summary_id)
        return summary
    else:
        raise HTTPException(404, 'Summary not found')


@router.put('/{summary_id}', response_model=SummarySchema)
async def update_summary(
    payload: SummaryUpdatePayloadSchema, summary_id: int = Path(gt=0)
):
    if summary := await crud.update(summary_id, payload):
        return summary
    else:
        raise HTTPException(404, 'Summary not found')
