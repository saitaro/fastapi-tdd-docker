import logging

from fastapi import FastAPI

from .api import ping, summaries
from .db import init_db

logger = logging.getLogger('uvicorn')


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(ping.router, prefix='/ping')
    app.include_router(summaries.router, prefix='/summaries', tags=['summaries'])

    return app


app = create_app()


@app.on_event('startup')
async def startup_event():
    logger.info('Starting up...')
    init_db(app)


@app.on_event('shutdown')
async def shutdown_event():
    logger.info('Shutting down...')
