from app.models.pydantic import (SummaryPayloadSchema,
                                 SummaryUpdatePayloadSchema)
from app.models.tortoise import TextSummary


async def read_all() -> list[dict]:
    return await TextSummary.all().values()


async def read(summary_id: int) -> dict | None:
    return await TextSummary.filter(id=summary_id).first().values()


async def create(payload: SummaryPayloadSchema) -> int:
    summary = TextSummary(
        url=payload.url,
        summary='dummy summary',
    )
    await summary.save()

    return summary.id


async def delete(summary_id: int) -> int:
    return await TextSummary.filter(id=summary_id).first().delete()


async def update(summary_id: int, payload: SummaryUpdatePayloadSchema) -> dict | None:
    db_summaries = TextSummary.filter(id=summary_id)
    summaries_updated: int = await db_summaries.update(
        url=payload.url, summary=payload.summary
    )
    if summaries_updated:
        return await db_summaries.first().values()
    else:
        return None
