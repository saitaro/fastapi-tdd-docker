from functools import cache
import logging

from pydantic import BaseSettings, AnyUrl

log = logging.getLogger('uvicorn')


class Settings(BaseSettings):
    environment: str = 'dev'
    testing: bool = False
    database_url: AnyUrl = None


@cache
def get_settings() -> BaseSettings:
    log.info('Loading config settings from the environment...')
    return Settings()
