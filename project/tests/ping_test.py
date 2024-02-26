from starlette.testclient import TestClient

"""
docker-compose exec web python -m pytest tests/ping_test.py
"""


def test_ping(test_app: TestClient):
    response = test_app.get('/ping')

    assert response.status_code == 200
    assert response.json() == {'environment': 'dev', 'testing': True, 'ping': 'pong!'}
