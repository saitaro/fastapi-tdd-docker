from fastapi import APIRouter, BackgroundTasks, HTTPException, Path

from app.api import crud
from app.models.pydantic import (
    SummaryPayloadSchema,
    SummaryResponseSchema,
    SummaryUpdatePayloadSchema,
)
from app.models.tortoise import SummarySchema
from app.summarizer import generate_summary

router = APIRouter()


@router.get('/', response_model=list[SummarySchema])
async def get_all_summaries():
    return await crud.read_all()


@router.get('/{summary_id}', response_model=SummarySchema)
async def get_summary(summary_id: int = Path(gt=0)):
    if summary := await crud.read(summary_id):
        return summary
    else:
        raise HTTPException(404, 'Summary not found')


@router.post('/', response_model=SummaryResponseSchema, status_code=201)
async def create_summary(
    payload: SummaryPayloadSchema, background_tasks: BackgroundTasks
):
    summary_id = await crud.create(payload)
    background_tasks.add_task(generate_summary, summary_id, str(payload.url))
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
