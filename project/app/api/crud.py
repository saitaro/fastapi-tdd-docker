from app.models.pydantic import SummaryPayloadSchema
from app.models.tortoise import TextSummary


async def post(payload: SummaryPayloadSchema) -> int:
    summary = TextSummary(
        url=payload.url,
        summary='dummy summary',
    )
    await summary.save()

    return summary.id


async def get(id: int) -> dict | None:
    return await TextSummary.filter(id=id).first().values()


async def get_all() -> list[dict]:
    return await TextSummary.all().values()
