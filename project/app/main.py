import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api import ping, summaries
from .db import init_db

logger = logging.getLogger('uvicorn')


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Starting up...')
    init_db(app)

    yield

    logger.info('Shutting down...')


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(ping.router, prefix='/ping')
    app.include_router(summaries.router, prefix='/summaries', tags=['summaries'])

    return app


app = create_app()
