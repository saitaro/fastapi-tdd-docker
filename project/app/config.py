from functools import cache
import logging

from pydantic import BaseSettings


log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    environment: str = "dev"
    testing: bool = False


@cache
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()
