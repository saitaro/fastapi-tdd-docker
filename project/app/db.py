import logging
import os

from tortoise import Tortoise, run_async

logger = logging.getLogger('uvicorn')


TORTOISE_ORM = dict(
    connections={'default': os.environ.get('DATABASE_URL')},
    apps={
        'models': {
            'models': ['app.models.tortoise', 'aerich.models'],
            'default_connection': 'default',
        },
    },
)


async def generate_schemas() -> None:
    logger.info('Initializing Tortoise...')
    await Tortoise.init(
        db_url=os.environ.get('DATABASE_URL'),
        modules={'models': ['app.models.tortoise']},
    )
    logger.info('Generating database schemas via Tortoise...')
    await Tortoise.generate_schemas()
    await Tortoise.close_connections()


if __name__ == '__main__':
    run_async(generate_schemas())
