import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncContextManager

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise import Tortoise, connections
from tortoise.exceptions import DoesNotExist, IntegrityError

from .api import ping, summaries

logger = logging.getLogger('uvicorn')


@asynccontextmanager
async def main_lifespan(app: FastAPI):
    logger.info('Starting up...')
    await Tortoise.init(
        db_url=os.environ.get('DATABASE_URL'),
        modules={'models': ['app.models.tortoise']},
    )
    yield

    logger.info('Shutting down...')
    await connections.close_all()


def create_app(lifespan: AsyncContextManager = main_lifespan) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(ping.router, prefix='/ping')
    app.include_router(summaries.router, prefix='/summaries', tags=['summaries'])

    @app.exception_handler(DoesNotExist)
    async def doesnotexist_exception_handler(request: Request, exc: DoesNotExist):
        return JSONResponse(status_code=404, content={'detail': str(exc)})

    @app.exception_handler(IntegrityError)
    async def integrityerror_exception_handler(request: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=422,
            content={
                'detail': [{'loc': [], 'msg': str(exc), 'type': 'IntegrityError'}]
            },
        )

    return app


app = create_app()
