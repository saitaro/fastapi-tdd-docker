import os
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient
from tortoise import Tortoise, connections

from app.config import Settings, get_settings
from app.main import create_app


def get_settings_override():
    return Settings(testing=1, database_url=os.environ.get('DATABASE_TEST_URL'))


@pytest.fixture(scope='module')
def test_app():
    # set up
    app = create_app()
    app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(app) as test_client:

        # testing
        yield test_client

    # tear down


@asynccontextmanager
async def test_lifespan(app: FastAPI):
    await Tortoise.init(
        db_url=os.environ.get('DATABASE_TEST_URL'),
        modules={'models': ['app.models.tortoise']},
    )
    await Tortoise.generate_schemas()

    yield

    await connections.close_all()


@pytest.fixture(scope='module')
def test_app_with_db():
    app = create_app(lifespan=test_lifespan)
    app.dependency_overrides[get_settings] = get_settings_override

    with TestClient(app) as test_client:

        # testing
        yield test_client

    # tear down
