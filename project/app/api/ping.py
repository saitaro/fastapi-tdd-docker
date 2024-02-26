from fastapi import APIRouter, Depends

from app.config import Settings, get_settings

router = APIRouter()


@router.get('/')
async def pong(settings: Settings = Depends(get_settings)):
    return {
        'ping': 'pong on Render!!!',
        'environment': settings.environment,
        'testing': settings.testing,
    }
